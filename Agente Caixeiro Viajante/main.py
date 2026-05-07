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
# Coleta de Cidades
# ---------------------------------------------------------------------------

def collect_cities() -> list[City]:
    """Solicita ao usuário as cidades do problema via terminal.

    O usuário digita o nome e as coordenadas (x, y) de cada cidade.
    Para encerrar a entrada, basta deixar o nome em branco.

    Returns:
        Lista de objetos City fornecidos pelo usuário.
    """
    print("\n" + "─" * 60)
    print("  CADASTRO DE CIDADES")
    print("─" * 60)
    print("  • Digite o nome e as coordenadas de cada cidade.")
    print("  • Pressione ENTER sem digitar nada para encerrar.")
    print("  • São necessárias pelo menos 3 cidades.")
    print("─" * 60 + "\n")

    cities: list[City] = []
    city_names: set[str] = set()

    while True:
        index = len(cities) + 1
        name = _input(f"  Cidade {index} — Nome (ou ENTER para finalizar): ")

        if not name:
            if len(cities) < 3:
                print(f"  ✘ Você precisa cadastrar pelo menos 3 cidades. "
                      f"Atualmente: {len(cities)}.")
                continue
            break

        # Evita nomes duplicados
        if name in city_names:
            print(f"  ✘ A cidade '{name}' já foi cadastrada. Use um nome diferente.")
            continue

        x = _read_float(f"         Coordenada X de '{name}': ")
        y = _read_float(f"         Coordenada Y de '{name}': ")

        city = City(name=name, x=x, y=y)
        cities.append(city)
        city_names.add(name)
        print(f"  ✔ '{name}' adicionada! ({len(cities)} cidade(s) no total.)\n")

    return cities


# ---------------------------------------------------------------------------
# Escolha da Cidade de Origem
# ---------------------------------------------------------------------------

def choose_origin(cities: list[City]) -> City:
    """Exibe a lista de cidades e solicita a escolha da cidade de origem.

    Args:
        cities: Lista de cidades cadastradas.

    Returns:
        Cidade escolhida como ponto de partida e retorno.
    """
    print("\n" + "─" * 60)
    print("  ESCOLHA DA CIDADE DE ORIGEM")
    print("─" * 60)
    print("  Cidades cadastradas:\n")
    for i, city in enumerate(cities, start=1):
        print(f"    [{i:>2}]  {city.name:<25}  (x={city.x:>8.2f}, y={city.y:>8.2f})")
    print()

    index = _read_int(
        f"  Digite o número da cidade de origem [1–{len(cities)}]: ",
        min_val=1,
        max_val=len(cities),
    )
    chosen = cities[index - 1]
    print(f"\n  ✔ Cidade de origem definida: '{chosen.name}'\n")
    return chosen


# ---------------------------------------------------------------------------
# Ponto de Entrada
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n" + "=" * 60)
    print("   AGENTE CAIXEIRO VIAJANTE  —  Configuração Interativa")
    print("=" * 60)

    # 1. Coletar cidades
    cities = collect_cities()

    # 2. Escolher origem
    origin = choose_origin(cities)

    # 3. Ativar modo verbose?
    verbose_raw = _input("  Exibir progresso detalhado da busca? [s/N]: ").lower()
    verbose = verbose_raw in ("s", "sim", "y", "yes")

    # 4. Executar o agente
    agent = TSPAgent(cities=cities, origin=origin, verbose=verbose)
    result = agent.run()

    # 5. Resumo final
    if result.found:
        print(f"\n  ► Caminho: {' → '.join(result.path)}")
        print(f"  ► Custo Total Ótimo: {result.total_cost:.4f}")
    else:
        print(f"\n  ✘ {result.message}")

    print()


if __name__ == "__main__":
    main()
