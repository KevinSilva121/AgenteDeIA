"""
tsp_agent.py
------------
Agente de Resolução de Problemas Autônomo para o TSP.

Arquitetura: FORMULAR → BUSCAR → EXECUTAR

O TSPAgent é o orquestrador central que:
  1. FORMULA o problema a partir do ambiente e do objetivo.
  2. BUSCA a solução usando o algoritmo A*.
  3. EXECUTA (relata) a sequência de ações e o custo total.

Esta separação de responsabilidades (SRP) garante que cada componente
possa ser testado, substituído ou evoluído de forma independente.
"""

from __future__ import annotations

from typing import List, Optional

from tsp_environment import City, TSPEnvironment
from tsp_problem import TSPProblem
from tsp_search import AStarGraphSearch, SearchResult


# ---------------------------------------------------------------------------
# Agente Principal
# ---------------------------------------------------------------------------

class TSPAgent:
    """Agente autônomo para resolver o Problema do Caixeiro Viajante.

    O agente segue o ciclo clássico de um agente solucionador de problemas
    (Russell & Norvig, AIMA):

        1. Formulação do Objetivo: Dado um conjunto de cidades, o objetivo
           é encontrar o ciclo hamiltoniano de menor custo.

        2. Formulação do Problema: Definir estados, ações, transições,
           custo e heurística.

        3. Busca: Encontrar a sequência de ações que leva ao objetivo.

        4. Execução: Reportar a solução encontrada.

    Args:
        cities    (List[City]):       Cidades do problema.
        origin    (City):             Cidade de partida/retorno.
        verbose   (bool):             Ativa logs de progresso durante a busca.
    """

    def __init__(
        self,
        cities: List[City],
        origin: City,
        verbose: bool = False,
    ) -> None:
        self.cities = cities
        self.origin = origin
        self.verbose = verbose

        # Componentes internos (inicializados em _formulate)
        self._environment: Optional[TSPEnvironment] = None
        self._problem: Optional[TSPProblem] = None
        self._result: Optional[SearchResult] = None

    # ------------------------------------------------------------------
    # Ciclo Principal: Formular → Buscar → Executar
    # ------------------------------------------------------------------

    def run(self) -> SearchResult:
        """Executa o ciclo completo do agente.

        Returns:
            SearchResult contendo o caminho ótimo, custo e estatísticas.
        """
        print("=" * 60)
        print("  AGENTE CAIXEIRO VIAJANTE — A* (BUSCA-EM-GRAFO)")
        print("=" * 60)

        # FASE 1: FORMULAR
        self._formulate()

        # FASE 2: BUSCAR
        self._search()

        # FASE 3: EXECUTAR (reportar)
        self._execute()

        return self._result

    # ------------------------------------------------------------------
    # Fase 1: Formulação
    # ------------------------------------------------------------------

    def _formulate(self) -> None:
        """Constrói o ambiente e formula o problema.

        Passos:
          - Cria TSPEnvironment com as cidades fornecidas.
          - Pré-calcula a matriz de distâncias euclidianas.
          - Instancia TSPProblem com a cidade de origem.
        """
        print("\n[1/3] FORMULANDO O PROBLEMA...")
        self._environment = TSPEnvironment(cities=self.cities)
        self._problem = TSPProblem(
            environment=self._environment,
            origin_city=self.origin,
        )

        n = len(self.cities)
        print(f"  ✔ Ambiente criado: {n} cidades.")
        print(f"  ✔ Cidade de origem: {self.origin.name!r}")
        print(f"  ✔ Estado inicial  : {self._problem.initial_state()}")
        print(f"  ✔ Espaço de estados: {n}! / {n} = {self._factorial(n - 1):,} rotas possíveis.")

    # ------------------------------------------------------------------
    # Fase 2: Busca
    # ------------------------------------------------------------------

    def _search(self) -> None:
        """Executa o algoritmo A* para encontrar a rota ótima."""
        print("\n[2/3] EXECUTANDO A BUSCA A*...")
        searcher = AStarGraphSearch(problem=self._problem)
        self._result = searcher.search(verbose=self.verbose)
        print(f"  ✔ Busca concluída em {self._result.elapsed_time:.4f}s")
        print(f"  ✔ Nós expandidos : {self._result.nodes_expanded:,}")
        print(f"  ✔ Nós gerados    : {self._result.nodes_generated:,}")

    # ------------------------------------------------------------------
    # Fase 3: Execução (Relatório)
    # ------------------------------------------------------------------

    def _execute(self) -> None:
        """Exibe a solução encontrada de forma estruturada."""
        print("\n[3/3] EXECUTANDO A SOLUÇÃO...")
        print("-" * 60)

        if not self._result.found:
            print(f"  ✘ {self._result.message}")
            return

        path = self._result.path
        total_cost = self._result.total_cost
        city_map = self._environment.city_map

        print(f"  ✔ {self._result.message}")
        print(f"\n  ROTA ÓTIMA ({len(path) - 1} movimentos):")
        print(f"  {'─' * 50}")

        for i in range(len(path) - 1):
            from_name = path[i]
            to_name = path[i + 1]
            from_city = city_map[from_name]
            to_city = city_map[to_name]
            dist = self._environment.distance(from_city, to_city)
            arrow = "→" if i < len(path) - 2 else "↩"
            print(
                f"  Passo {i + 1:>2}: {from_name:>10} {arrow} {to_name:<10} "
                f"  (distância: {dist:>8.4f})"
            )

        print(f"  {'─' * 50}")
        print(f"  CUSTO TOTAL ÓTIMO : {total_cost:.4f}")
        print("=" * 60)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _factorial(n: int) -> int:
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
