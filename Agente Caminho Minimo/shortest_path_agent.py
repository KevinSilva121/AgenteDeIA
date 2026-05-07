"""
shortest_path_agent.py
-----------------------
Agente de Resolução de Problemas — Caminho Mínimo no Mapa da Romênia.

Arquitetura: FORMULAR → BUSCAR → EXECUTAR  (Russell & Norvig, AIMA Cap. 3)

O ShortestPathAgent orquestra os três módulos independentes:
  - RomaniaEnvironment : o AMBIENTE (cidades e distâncias).
  - ShortestPathProblem: a FORMULAÇÃO do problema.
  - UniformCostSearch  : o ALGORITMO de busca.

Dessa forma, cada componente pode ser substituído ou testado isoladamente
sem alterar os demais (princípio da responsabilidade única — SRP).
"""

from __future__ import annotations

from typing import Optional

from romania_environment import RomaniaEnvironment
from romania_problem import ShortestPathProblem
from ucs_search import UniformCostSearch, SearchResult


# ---------------------------------------------------------------------------
# Agente Principal
# ---------------------------------------------------------------------------

class ShortestPathAgent:
    """Agente autônomo que encontra o caminho de menor custo entre duas cidades.

    Segue o ciclo clássico de um Agente Solucionador de Problemas (AIMA):

        1. Formulação do Objetivo  : chegar à cidade de destino.
        2. Formulação do Problema  : estados, ações, custo, teste de objetivo.
        3. Busca                   : Uniform-Cost Search (UCS) garante otimalidade.
        4. Execução / Relatório    : exibe o caminho e custo encontrados.

    Args:
        origin      (str):  Cidade de partida (ex.: "Arad").
        destination (str):  Cidade de destino (ex.: "Bucharest").
        verbose     (bool): Se True, exibe cada expansão de nó durante a busca.
    """

    def __init__(
        self,
        origin: str,
        destination: str,
        verbose: bool = False,
    ) -> None:
        self.origin = origin
        self.destination = destination
        self.verbose = verbose

        # Componentes internos (construídos em _formulate)
        self._environment: Optional[RomaniaEnvironment] = None
        self._problem: Optional[ShortestPathProblem] = None
        self._result: Optional[SearchResult] = None

    # ------------------------------------------------------------------
    # Ciclo Principal
    # ------------------------------------------------------------------

    def run(self) -> SearchResult:
        """Executa o ciclo completo: Formular → Buscar → Executar.

        Returns:
            SearchResult com o caminho, custo e estatísticas da busca.
        """
        self._print_header()

        # FASE 1: FORMULAR
        self._formulate()

        # FASE 2: BUSCAR
        self._search()

        # FASE 3: EXECUTAR (relatório)
        self._execute()

        return self._result

    # ------------------------------------------------------------------
    # Fase 1: Formulação
    # ------------------------------------------------------------------

    def _formulate(self) -> None:
        """Constrói o ambiente e formula o problema formalmente."""
        print("\n[1/3] FORMULANDO O PROBLEMA...")

        self._environment = RomaniaEnvironment()
        self._problem = ShortestPathProblem(
            environment=self._environment,
            origin=self.origin,
            destination=self.destination,
        )

        print(f"  [OK] Ambiente criado      : {self._environment}")
        print(f"  [OK] Estado inicial       : '{self._problem.initial_state()}'")
        print(f"  [OK] Estado objetivo      : '{self.destination}'")
        print(f"  [OK] Algoritmo            : Busca de Custo Uniforme (UCS)")

    # ------------------------------------------------------------------
    # Fase 2: Busca
    # ------------------------------------------------------------------

    def _search(self) -> None:
        """Executa a Busca de Custo Uniforme."""
        print("\n[2/3] EXECUTANDO A BUSCA UCS...")
        if self.verbose:
            print()

        searcher = UniformCostSearch(problem=self._problem)
        self._result = searcher.search(verbose=self.verbose)

        if self.verbose:
            print()

        print(f"  [OK] Busca concluida em   : {self._result.elapsed_time * 1000:.3f} ms")
        print(f"  [OK] Nos expandidos       : {self._result.nodes_expanded}")
        print(f"  [OK] Nos gerados          : {self._result.nodes_generated}")

    # ------------------------------------------------------------------
    # Fase 3: Execução (Relatório)
    # ------------------------------------------------------------------

    def _execute(self) -> None:
        """Exibe a solucao encontrada de forma estruturada e didatica."""
        print("\n[3/3] SOLUCAO ENCONTRADA")
        print("-" * 60)

        if not self._result.found:
            print(f"  [FALHA] {self._result.message}")
            print("=" * 60)
            return

        path = self._result.path
        total_cost = self._result.total_cost

        print(f"  [OK] {self._result.message}\n")
        print(f"  CAMINHO MINIMO ({len(path) - 1} {'etapa' if len(path) - 1 == 1 else 'etapas'}):")
        print(f"  {'-' * 54}")

        # Detalhamento de cada etapa
        for i in range(len(path) - 1):
            from_city = path[i]
            to_city = path[i + 1]
            dist = self._environment.distance(from_city, to_city)
            is_last = (i == len(path) - 2)
            marker = ">>" if is_last else "  "
            print(
                f"  {marker} Etapa {i + 1:>2}: "
                f"{from_city:<20} ->  {to_city:<20} "
                f"[{dist:>3} km]"
            )

        print(f"  {'-' * 54}")

        # Caminho resumido (formato solicitado)
        path_str = " -> ".join(path)
        print(f"\n  ROTA    : {path_str}")
        print(f"  CUSTO   : {total_cost} km")
        print("=" * 60)

    # ------------------------------------------------------------------
    # Helper: cabeçalho
    # ------------------------------------------------------------------

    def _print_header(self) -> None:
        print("=" * 60)
        print("  AGENTE DE CAMINHO MINIMO -- MAPA DA ROMENIA")
        print("  Algoritmo: Busca de Custo Uniforme (UCS)")
        print("=" * 60)
        print(f"  Origem    : {self.origin}")
        print(f"  Destino   : {self.destination}")
