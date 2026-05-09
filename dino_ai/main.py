# -*- coding: utf-8 -*-
"""
main.py - Dino AI com treinamento paralelo (N Chromes simultaneos)

Acoes do dino:
  0 = nada
  1 = pulo normal (arco completo)
  2 = pulo curto  (pula + agacha = sai mais rapido do pulo!)
  3 = agachar

Uso:
    python main.py              # treina com 5 Chromes em paralelo
    python main.py --workers 3  # usa 3 Chromes
    python main.py --load       # assiste o melhor individuo salvo
    python main.py --headless   # sem janela visivel (mais rapido)
"""

import argparse
import time
import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np

from neural_network    import NeuralNetwork
from genetic_algorithm import GeneticAlgorithm
from game_controller   import GameController


# ─── Configuracoes ───────────────────────────────────────────────────────────
POPULATION_SIZE   = 30
MAX_GENERATIONS   = 500     # 0 = infinito
STEP_DELAY        = 0.03    # segundos entre decisoes (~33fps)
MAX_SCORE_TARGET  = 9999    # score alvo para considerar "aprendido"
NUM_WORKERS       = 5       # Chromes em paralelo
SAVE_PATH         = "best_dino.npy"
LOG_PATH          = "training_log.csv"

GA_PARAMS = dict(
    population_size  = POPULATION_SIZE,
    mutation_rate    = 0.12,
    mutation_scale   = 0.25,
    crossover_rate   = 0.80,
    elite_frac       = 0.15,
    crossover_frac   = 0.40,
    mutant_frac      = 0.25,
    stagnation_limit = 8,
)

_print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs, flush=True)


# ─── Pool de GameControllers ──────────────────────────────────────────────────

class GamePool:
    def __init__(self, n: int, headless: bool = False):
        self.n         = n
        self.headless  = headless
        self.games: list[GameController] = []
        self._available: list[GameController] = []
        self._lock      = threading.Lock()
        self._semaphore = threading.Semaphore(n)

    def start(self):
        safe_print(f"\n[Pool] Iniciando {self.n} instancias do Chrome...")
        results = [None] * self.n
        threads = []

        def launch(i):
            try:
                gc = GameController(headless=self.headless,
                                    window_index=i, total_windows=self.n)
                results[i] = gc
                safe_print(f"  [Chrome {i+1}/{self.n}] Pronto!")
            except Exception as e:
                safe_print(f"  [Chrome {i+1}/{self.n}] ERRO: {e}")

        for i in range(self.n):
            t = threading.Thread(target=launch, args=(i,), daemon=True)
            threads.append(t)
            t.start()
            time.sleep(0.8)

        for t in threads:
            t.join()

        self.games     = [g for g in results if g is not None]
        self._available = list(self.games)

        safe_print(f"[Pool] {len(self.games)} instancias prontas!\n")
        if not self.games:
            raise RuntimeError("Nenhuma instancia do Chrome inicializada!")

    def acquire(self) -> GameController:
        self._semaphore.acquire()
        with self._lock:
            return self._available.pop()

    def release(self, game: GameController):
        with self._lock:
            self._available.append(game)
        self._semaphore.release()

    def close_all(self):
        safe_print("\n[Pool] Fechando browsers...")
        for gc in self.games:
            try:
                gc.close()
            except Exception:
                pass


# ─── Logica de acao ──────────────────────────────────────────────────────────

def apply_action(game: GameController, action: int):
    """
    Acao 0 = nada
    Acao 1 = pulo normal
    Acao 2 = pulo curto (pula + agacha logo = menor arco!)
    Acao 3 = agachar
    """
    if action == 1:
        game.jump()
    elif action == 2:
        game.short_jump()
    elif action == 3:
        game.duck()
    else:
        game.do_nothing()


# ─── Execucao de um individuo ─────────────────────────────────────────────────

def run_individual(game: GameController, nn: NeuralNetwork,
                   max_steps: int = 99999) -> float:
    """Roda um individuo ate morrer. Retorna fitness."""
    game.restart()
    time.sleep(0.6)

    steps          = 0
    score          = 0.0
    last_score_chk = time.time()

    while steps < max_steps:
        state = game.get_state()

        if state is None or state.get("dead", False):
            break

        inputs = game.state_to_inputs(state)
        action = nn.forward(inputs)
        apply_action(game, action)

        score  = float(state.get("score", 0))
        steps += 1

        # Timeout: nao comecou a pontuar em 5s -> assume travado
        if steps % 60 == 0:
            if time.time() - last_score_chk > 5.0 and score < 5:
                break
        if score > 0:
            last_score_chk = time.time()

        time.sleep(STEP_DELAY)

    game.is_ducking = False
    game.release_duck()

    # Fitness: score (principal) + bonus de longevidade
    fitness = score + steps * 0.04
    return fitness


def run_worker(pool: GamePool, idx: int,
               nn: NeuralNetwork) -> tuple[int, float, float]:
    game = pool.acquire()
    try:
        fit   = run_individual(game, nn)
        score = game.get_score()
        return idx, score, fit
    except Exception as e:
        safe_print(f"  [Worker {idx}] Excecao: {e}")
        return idx, 0.0, 0.0
    finally:
        pool.release(game)


# ─── Log CSV ────────────────────────────────────────────────────────────────

def init_log():
    with open(LOG_PATH, "w") as f:
        f.write("generation,best_fitness,avg_fitness,max_gen_fitness,stagnation,mut_factor\n")

def append_log(stats: dict):
    with open(LOG_PATH, "a") as f:
        f.write(f"{stats['generation']},{stats['best_fitness']:.2f},"
                f"{stats['avg_fitness']:.2f},{stats['max_fitness']:.2f},"
                f"{stats['stagnation']},{stats['mut_scale_factor']:.2f}\n")


# ─── Treinamento principal ───────────────────────────────────────────────────

def train(num_workers: int = NUM_WORKERS, headless: bool = False):
    print("=" * 65, flush=True)
    print(f"  DINO AI - Treinamento Paralelo ({num_workers} Chromes)", flush=True)
    print(f"  Pop: {POPULATION_SIZE} | Elite: 15% | Crossover: 40% | Mutantes: 25% | Aleatorios: 20%", flush=True)
    print(f"  Acoes: nada / pulo-normal / pulo-curto / agachar", flush=True)
    print("=" * 65, flush=True)

    ga   = GeneticAlgorithm(**GA_PARAMS)
    pool = GamePool(n=num_workers, headless=headless)
    pool.start()
    init_log()

    generation     = 0
    target_reached = False

    try:
        while (MAX_GENERATIONS == 0 or generation < MAX_GENERATIONS) and not target_reached:
            generation += 1
            fitnesses = [0.0] * POPULATION_SIZE

            print(f"\n{'-'*65}", flush=True)
            print(f"  GERACAO {generation:>3}  |  workers={num_workers}  "
                  f"| melhor hist={ga.best_fitness:.1f}  "
                  f"| estag={ga.stagnation_count}", flush=True)
            print(f"{'-'*65}", flush=True)

            done_count = 0
            with ThreadPoolExecutor(max_workers=num_workers) as ex:
                futures = {
                    ex.submit(run_worker, pool, i, nn): i
                    for i, nn in enumerate(ga.population)
                }
                for future in as_completed(futures):
                    i, score, fit = future.result()
                    fitnesses[i]  = fit
                    done_count   += 1
                    print(f"  [{done_count:>2}/{POPULATION_SIZE}] "
                          f"Ind {i+1:>2} | score={score:>6.0f} | fit={fit:>7.2f}",
                          flush=True)

                    if score >= MAX_SCORE_TARGET:
                        print(f"\n*** OBJETIVO ATINGIDO! Score={score:.0f} gen={generation} ***",
                              flush=True)
                        ga.fitnesses      = fitnesses
                        ga.best_fitness   = max(fitnesses)
                        ga.best_network   = ga.population[i]
                        ga.save_best(SAVE_PATH)
                        target_reached = True
                        break

            if target_reached:
                break

            ga.evolve(fitnesses)
            stats = ga.stats()
            append_log(stats)
            ga.save_best(SAVE_PATH)

            stag_info = ""
            if stats["stagnation"] > 0:
                stag_info = f" | estagnacao={stats['stagnation']}x (mut x{stats['mut_scale_factor']:.1f})"

            print(f"\n  => Geracao {generation} concluida:", flush=True)
            print(f"     Melhor fitness historico : {stats['best_fitness']:.2f}", flush=True)
            print(f"     Fitness medio desta gen  : {stats['avg_fitness']:.2f}", flush=True)
            print(f"     Fitness max desta gen    : {stats['max_fitness']:.2f}{stag_info}", flush=True)

    except KeyboardInterrupt:
        print("\nTreinamento interrompido.", flush=True)
    finally:
        ga.save_best(SAVE_PATH)
        pool.close_all()
        print(f"\nLog: {LOG_PATH}  |  Campeao: {SAVE_PATH}", flush=True)


# ─── Modo assistir ───────────────────────────────────────────────────────────

def watch():
    if not os.path.exists(SAVE_PATH):
        print(f"Arquivo '{SAVE_PATH}' nao encontrado. Treine primeiro.", flush=True)
        sys.exit(1)

    print("=" * 60, flush=True)
    print("  DINO AI - Modo Assistir (melhor individuo salvo)", flush=True)
    print("=" * 60, flush=True)

    ga   = GeneticAlgorithm(population_size=1)
    nn   = ga.load_best(SAVE_PATH)
    game = GameController(headless=False, window_index=0, total_windows=1)

    episode = 0
    try:
        while True:
            episode += 1
            print(f"\nEpisodio {episode} - Ctrl+C para sair", flush=True)
            fit   = run_individual(game, nn, max_steps=999999)
            score = game.get_score()
            print(f"  Score: {score:.0f} | Fitness: {fit:.2f}", flush=True)
    except KeyboardInterrupt:
        print("\nEncerrando...", flush=True)
    finally:
        game.close()


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Dino AI")
    parser.add_argument("--load",     action="store_true",
                        help="Assiste o melhor individuo")
    parser.add_argument("--headless", action="store_true",
                        help="Sem janela (mais rapido)")
    parser.add_argument("--workers",  type=int, default=NUM_WORKERS,
                        help=f"Chromes em paralelo (default={NUM_WORKERS})")
    args = parser.parse_args()

    if args.load:
        watch()
    else:
        train(num_workers=args.workers, headless=args.headless)


if __name__ == "__main__":
    main()
