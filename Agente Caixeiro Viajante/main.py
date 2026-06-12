"""
main.py
-------
Ponto de entrada interativo do Agente Caixeiro Viajante.

O usuário informa as cidades via terminal (nome e coordenadas x, y)
e escolhe a cidade de origem. O agente então resolve o TSP com A*.

Execute com:
  python main.py
"""

import sys
from tsp_environment import City
from tsp_agent import TSPAgent
from romania_data import ROMANIA_COORDINATES

# Configura o console para UTF-8 no Windows para evitar UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')



# ---------------------------------------------------------------------------
# Helpers de Input
# ---------------------------------------------------------------------------

def _input(prompt: str) -> str:
    """Wrapper de input que encerra o programa graciosamente com Ctrl+C."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nEncerrando o agente. Até logo!")
        sys.exit(0)


def _read_float(prompt: str) -> float:
    """Lê um número float do terminal, pedindo novamente em caso de erro."""
    while True:
        raw = _input(prompt)
        try:
            return float(raw)
        except ValueError:
            print(f"  ✘ '{raw}' não é um número válido. Tente novamente.")


def _read_int(prompt: str, min_val: int, max_val: int) -> int:
    """Lê um inteiro dentro do intervalo [min_val, max_val]."""
    while True:
        raw = _input(prompt)
        try:
            value = int(raw)
            if min_val <= value <= max_val:
                return value
            print(f"  ✘ Digite um número entre {min_val} e {max_val}.")
        except ValueError:
            print(f"  ✘ '{raw}' não é um inteiro válido. Tente novamente.")


# ---------------------------------------------------------------------------
# Helpers de Exibição
# ---------------------------------------------------------------------------

def print_cities_menu(cities_list: list[str]) -> None:
    """Exibe as cidades em duas colunas organizadas."""
    for i in range(0, len(cities_list), 2):
        city1 = cities_list[i]
        num1 = i + 1
        line = f"    [{num1:>2}] {city1:<20}"
        if i + 1 < len(cities_list):
            city2 = cities_list[i + 1]
            num2 = i + 2
            line += f"[{num2:>2}] {city2:<20}"
        print(line)


# ---------------------------------------------------------------------------
# Ponto de Entrada
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n" + "=" * 60)
    print("   AGENTE CAIXEIRO VIAJANTE  —  Configuração Interativa")
    print("=" * 60)

    cities_list = sorted(ROMANIA_COORDINATES.keys())

    print("\n" + "─" * 60)
    print("  CIDADES DISPONÍVEIS NO MAPA DA ROMÊNIA")
    print("─" * 60)
    print_cities_menu(cities_list)
    print("─" * 60 + "\n")

    # 1. Escolher cidade de início
    print("  1. ESCOLHA A CIDADE DE INÍCIO (PARTIDA)")
    start_idx = _read_int(f"  Digite o número da cidade de início [1-{len(cities_list)}]: ", 1, len(cities_list))
    start_name = cities_list[start_idx - 1]
    start_city = City(name=start_name, x=ROMANIA_COORDINATES[start_name][0], y=ROMANIA_COORDINATES[start_name][1])
    print(f"  ✔ Cidade de início definida: '{start_name}'\n")

    # 2. Escolher cidade de destino final
    print("  2. ESCOLHA A CIDADE DE DESTINO FINAL")
    end_idx = _read_int(f"  Digite o número da cidade de destino final [1-{len(cities_list)}]: ", 1, len(cities_list))
    end_name = cities_list[end_idx - 1]
    end_city = City(name=end_name, x=ROMANIA_COORDINATES[end_name][0], y=ROMANIA_COORDINATES[end_name][1])
    print(f"  ✔ Cidade de destino final definida: '{end_name}'\n")

    # 3. Escolher 3 paradas intermediárias
    print("─" * 60)
    print("  3. TRÊS PARADAS INTERMEDIÁRIAS")
    print("─" * 60)
    print(f"  • Escolha exatamente 3 cidades para visitar entre '{start_name}' e '{end_name}'.")
    print(f"  • As paradas não podem ser iguais a '{start_name}' ou '{end_name}'.")
    print("─" * 60 + "\n")

    while True:
        raw_stops = _input("  Digite os números das 3 paradas (ex: 3, 5, 8): ")
        try:
            parts = [p.strip() for p in raw_stops.split(",")]
            indices = [int(p) - 1 for p in parts if p]
            if len(indices) != 3:
                print(f"  ✘ Você deve escolher exatamente 3 paradas. Escolhidas: {len(indices)}.")
                continue
            if any(idx < 0 or idx >= len(cities_list) for idx in indices):
                print(f"  ✘ Os números devem estar entre 1 e {len(cities_list)}.")
                continue

            selected_stop_names = [cities_list[idx] for idx in indices]
            # Verifica se há duplicados nas paradas
            if len(set(selected_stop_names)) < 3:
                print("  ✘ As 3 paradas devem ser cidades diferentes entre si.")
                continue

            # Verifica se as paradas coincidem com início ou fim
            if start_name in selected_stop_names:
                print(f"  ✘ A cidade de início '{start_name}' não pode ser uma das paradas.")
                continue
            if end_name in selected_stop_names:
                print(f"  ✘ A cidade de destino final '{end_name}' não pode ser uma das paradas.")
                continue

            # Constrói os objetos City para as paradas
            stops = []
            for name in selected_stop_names:
                stops.append(City(name=name, x=ROMANIA_COORDINATES[name][0], y=ROMANIA_COORDINATES[name][1]))
            break
        except ValueError:
            print("  ✘ Entrada inválida. Digite 3 números separados por vírgula.")
            continue

    print(f"\n  ✔ Paradas definidas: {', '.join(selected_stop_names)}\n")

    # Constrói a lista total de cidades envolvidas no TSP
    all_cities = [start_city] + stops
    if end_name != start_name:
        all_cities.append(end_city)

    # 4. Ativar modo verbose?
    verbose_raw = _input("  Exibir progresso detalhado da busca? [s/N]: ").lower()
    verbose = verbose_raw in ("s", "sim", "y", "yes")

    # 5. Executar o agente
    agent = TSPAgent(cities=all_cities, origin=start_city, end_city=end_city, stops=stops, verbose=verbose)
    result = agent.run()

    # 6. Resumo final
    if result.found:
        print(f"\n  ► Caminho: {' → '.join(result.path)}")
        print(f"  ► Custo Total Ótimo: {result.total_cost:.4f}")
    else:
        print(f"\n  ✘ {result.message}")

    print()


if __name__ == "__main__":
    main()
