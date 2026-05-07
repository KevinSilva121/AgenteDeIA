"""
main.py
-------
Menu interativo — Agente de Caminho Minimo no Mapa da Romania.

O usuario escolhe a cidade de origem e de destino digitando o numero
correspondente. O agente executa a Busca de Custo Uniforme (UCS) e
exibe o caminho otimo encontrado. Ao final, o usuario pode rodar
uma nova consulta ou sair.
"""

from romania_environment import RomaniaEnvironment
from shortest_path_agent import ShortestPathAgent


# ---------------------------------------------------------------------------
# Exibicao do menu de cidades
# ---------------------------------------------------------------------------

def display_city_menu(cities: list[str]) -> None:
    """Imprime a lista de cidades numeradas em colunas."""
    print()
    print("  Cidades disponiveis:")
    print("  " + "-" * 54)
    # Exibe em 2 colunas
    col = (len(cities) + 1) // 2
    for i in range(col):
        left_idx  = i
        right_idx = i + col
        left  = f"  [{left_idx + 1:>2}] {cities[left_idx]}"
        right = f"  [{right_idx + 1:>2}] {cities[right_idx]}" if right_idx < len(cities) else ""
        print(f"{left:<35}{right}")
    print("  " + "-" * 54)


# ---------------------------------------------------------------------------
# Leitura e validacao da escolha do usuario
# ---------------------------------------------------------------------------

def choose_city(prompt: str, cities: list[str]) -> str:
    """Solicita que o usuario escolha uma cidade pelo numero.

    Fica em loop ate receber uma entrada valida.

    Args:
        prompt: Texto exibido ao usuario (ex.: "Escolha a ORIGEM").
        cities: Lista ordenada de cidades.

    Returns:
        Nome da cidade escolhida.
    """
    while True:
        try:
            raw = input(f"\n  {prompt} (1-{len(cities)}): ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(cities):
                return cities[idx]
            print(f"  [!] Numero invalido. Digite entre 1 e {len(cities)}.")
        except ValueError:
            print("  [!] Entrada invalida. Digite apenas o numero da cidade.")


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------

def main() -> None:
    env = RomaniaEnvironment()
    cities = sorted(env.cities)   # lista ordenada alfabeticamente

    print("=" * 60)
    print("  AGENTE DE CAMINHO MINIMO -- MAPA DA ROMANIA")
    print("  Algoritmo: Busca de Custo Uniforme (UCS)")
    print("=" * 60)

    while True:
        # Mostra o menu de cidades
        display_city_menu(cities)

        # Coleta origem e destino
        origin      = choose_city("Escolha a cidade de ORIGEM ", cities)
        destination = choose_city("Escolha a cidade de DESTINO", cities)

        print()

        # Executa o agente
        agent = ShortestPathAgent(
            origin=origin,
            destination=destination,
            verbose=False,
        )
        agent.run()

        # Pergunta se quer repetir
        print()
        again = input("  Deseja calcular outro caminho? (s/n): ").strip().lower()
        if again not in ("s", "sim", "y", "yes"):
            print()
            print("  Encerrando o agente. Ate logo!")
            print("=" * 60)
            break
        print()


if __name__ == "__main__":
    main()
