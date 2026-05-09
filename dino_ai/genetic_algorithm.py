# -*- coding: utf-8 -*-
"""
Algoritmo Genetico melhorado para evolucao das redes neurais.

Estrategia de reproducao por faixa de fitness:
  - [Campeao]     top-1 sempre sobrevive intacto
  - [Elite]       top 15%: copia exata + copia com micro-mutacao
  - [Cruzamento]  40%: crossover entre os top-40% com mutacao moderada
  - [Mutantes]    25%: mutacoes maiores dos top-50% (exploracao mais ampla)
  - [Aleatorios]  20%: individuos completamente novos (diversidade / fresh blood)

Mutacao adaptativa:
  - Quanto pior o individuo no ranking, maior a escala de mutacao
  - Se as geracoes passam sem melhora (estagnacao), aumenta a mutacao geral
"""

import numpy as np
from neural_network import NeuralNetwork


class GeneticAlgorithm:

    def __init__(
        self,
        population_size: int   = 30,
        mutation_rate:   float = 0.12,
        mutation_scale:  float = 0.25,
        crossover_rate:  float = 0.80,
        elite_frac:      float = 0.15,
        crossover_frac:  float = 0.40,
        mutant_frac:     float = 0.25,
        # resto (1 - elite - crossover - mutant) sera aleatorio
        stagnation_limit: int  = 8,     # geracoes sem melhora ate aumentar mutacao
    ):
        self.pop_size         = population_size
        self.base_mut_rate    = mutation_rate
        self.base_mut_scale   = mutation_scale
        self.crossover_rate   = crossover_rate
        self.elite_frac       = elite_frac
        self.crossover_frac   = crossover_frac
        self.mutant_frac      = mutant_frac
        self.stagnation_limit = stagnation_limit

        self.generation       = 0
        self.stagnation_count = 0
        self.best_fitness     = -np.inf
        self.best_network: NeuralNetwork | None = None
        self.fitnesses: list[float] = [0.0] * population_size

        # Populacao inicial completamente aleatoria
        self.population: list[NeuralNetwork] = [
            NeuralNetwork.random() for _ in range(population_size)
        ]

    # ──────────────────────────────────────────────────────────────────
    # Operadores geneticos
    # ──────────────────────────────────────────────────────────────────

    def _mutate(self, nn: NeuralNetwork,
                rate: float, scale: float) -> NeuralNetwork:
        """Mutacao gaussiana com mascara de taxa variavel."""
        w  = nn.get_weights().copy()
        mask = np.random.rand(len(w)) < rate
        w[mask] += np.random.randn(mask.sum()) * scale
        return NeuralNetwork(w)

    def _crossover_uniform(self, a: NeuralNetwork,
                           b: NeuralNetwork) -> NeuralNetwork:
        """Crossover uniforme: cada gene escolhe aleatoriamente de um pai."""
        wa, wb = a.get_weights(), b.get_weights()
        mask   = np.random.rand(len(wa)) < 0.5
        return NeuralNetwork(np.where(mask, wa, wb))

    def _crossover_blend(self, a: NeuralNetwork,
                         b: NeuralNetwork, alpha: float = 0.2) -> NeuralNetwork:
        """Crossover BLX-alpha: interpola entre os pais com jitter."""
        wa, wb = a.get_weights(), b.get_weights()
        lo  = np.minimum(wa, wb) - alpha * np.abs(wa - wb)
        hi  = np.maximum(wa, wb) + alpha * np.abs(wa - wb)
        child_w = lo + np.random.rand(len(wa)) * (hi - lo)
        return NeuralNetwork(child_w)

    def _tournament(self, sorted_pop: list[NeuralNetwork],
                    sorted_fits: list[float], k: int = 4) -> NeuralNetwork:
        """Selecao por torneio entre os melhores individuos."""
        pool_size = max(k, len(sorted_pop) // 2)
        idxs = np.random.choice(pool_size, size=min(k, pool_size), replace=False)
        winner = min(idxs)   # menor idx = maior fitness (lista ordenada decrescente)
        return sorted_pop[winner]

    # ──────────────────────────────────────────────────────────────────
    # Evolucao
    # ──────────────────────────────────────────────────────────────────

    def evolve(self, fitnesses: list[float]) -> list[NeuralNetwork]:
        """
        Recebe os fitnesses da geracao atual e gera a proxima geracao.
        Retorna a nova populacao.
        """
        self.fitnesses = fitnesses
        self.generation += 1

        # Ordena decrescente por fitness
        order       = np.argsort(fitnesses)[::-1]
        sorted_pop  = [self.population[i] for i in order]
        sorted_fits = [fitnesses[i]       for i in order]

        # Atualiza campeao
        if sorted_fits[0] > self.best_fitness:
            self.best_fitness  = sorted_fits[0]
            self.best_network  = NeuralNetwork(sorted_pop[0].get_weights().copy())
            self.stagnation_count = 0
        else:
            self.stagnation_count += 1

        # Mutacao adaptativa em cenario de estagnacao
        stag_factor = 1.0
        if self.stagnation_count >= self.stagnation_limit:
            stag_factor = 1.0 + 0.5 * (self.stagnation_count - self.stagnation_limit + 1)
            stag_factor = min(stag_factor, 4.0)   # limita a 4x

        mut_rate  = min(self.base_mut_rate  * stag_factor, 0.5)
        mut_scale = min(self.base_mut_scale * stag_factor, 2.0)

        n = self.pop_size
        n_elite     = max(1, int(n * self.elite_frac))
        n_crossover = max(1, int(n * self.crossover_frac))
        n_mutant    = max(1, int(n * self.mutant_frac))
        n_random    = n - n_elite - n_crossover - n_mutant

        new_pop: list[NeuralNetwork] = []

        # ── 1. CAMPEAO: preservado intacto (sempre o melhor) ──────────
        new_pop.append(NeuralNetwork(sorted_pop[0].get_weights().copy()))

        # ── 2. ELITE: copias com micro-mutacao ao redor do campeao ───
        #    Escala de mutacao muito pequena para refinar o campeao
        micro_scale = mut_scale * 0.15
        for i in range(1, n_elite):
            parent = sorted_pop[min(i, len(sorted_pop) - 1)]
            child  = self._mutate(parent, rate=mut_rate * 0.5, scale=micro_scale)
            new_pop.append(child)

        # ── 3. CRUZAMENTO: crossover entre os top-40% ────────────────
        top_pool_n = max(2, int(len(sorted_pop) * 0.4))
        top_pool   = sorted_pop[:top_pool_n]

        for _ in range(n_crossover):
            a = self._tournament(sorted_pop, sorted_fits, k=4)
            b = self._tournament(sorted_pop, sorted_fits, k=4)
            # Alterna entre crossover uniforme e blend
            if np.random.rand() < 0.5:
                child = self._crossover_uniform(a, b)
            else:
                child = self._crossover_blend(a, b)
            # Mutacao moderada pos-crossover
            child = self._mutate(child, rate=mut_rate, scale=mut_scale * 0.8)
            new_pop.append(child)

        # ── 4. MUTANTES: mutacoes mais agressivas dos top-50% ────────
        half_pool = sorted_pop[:max(2, n // 2)]
        for i in range(n_mutant):
            # Escala cresce conforme o rank do individuo escolhido
            rank_frac  = i / max(n_mutant - 1, 1)          # 0.0 a 1.0
            dyn_scale  = mut_scale * (1.0 + rank_frac * 1.5)
            parent_idx = int(rank_frac * (len(half_pool) - 1))
            parent     = half_pool[parent_idx]
            child      = self._mutate(parent, rate=mut_rate * 1.2, scale=dyn_scale)
            new_pop.append(child)

        # ── 5. ALEATORIOS: individuos totalmente novos ───────────────
        for _ in range(n_random):
            new_pop.append(NeuralNetwork.random())

        # Garante tamanho exato
        new_pop = new_pop[:n]
        while len(new_pop) < n:
            new_pop.append(NeuralNetwork.random())

        self.population = new_pop
        return self.population

    # ──────────────────────────────────────────────────────────────────
    # Persistencia
    # ──────────────────────────────────────────────────────────────────

    def save_best(self, path: str = "best_dino.npy"):
        if self.best_network is not None:
            np.save(path, self.best_network.get_weights())
            print(f"[GA] Campeao salvo '{path}'  fitness={self.best_fitness:.1f}", flush=True)

    def load_best(self, path: str = "best_dino.npy") -> NeuralNetwork:
        w  = np.load(path)
        nn = NeuralNetwork(w)
        print(f"[GA] Individuo carregado de '{path}'", flush=True)
        return nn

    def stats(self) -> dict:
        fits = self.fitnesses
        return {
            "generation":      self.generation,
            "best_fitness":    self.best_fitness,
            "avg_fitness":     float(np.mean(fits)),
            "max_fitness":     float(np.max(fits)),
            "min_fitness":     float(np.min(fits)),
            "stagnation":      self.stagnation_count,
            "mut_scale_factor": min(1.0 + 0.5 * max(0, self.stagnation_count - self.stagnation_limit + 1), 4.0),
        }
