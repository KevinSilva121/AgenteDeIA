"""
tsp_search.py
-------------
Implementação do algoritmo BUSCA-EM-GRAFO com A* (A-Estrela).

Responsabilidades:
  - Implementar a estrutura de nó de busca (SearchNode).
  - Implementar BUSCA-EM-GRAFO usando heapq (fila de prioridade) e
    conjunto explorado (tabela hash / Python set).
  - Separar completamente a lógica de busca da formulação do problema.

Complexidade:
  Tempo:  O(b^d) — dominado pela qualidade da heurística.
  Espaço: O(b^d) — todos os nós na fronteira e no conjunto explorado.
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Tuple

from tsp_problem import TSPProblem, TSPState


# ---------------------------------------------------------------------------
# Nó de Busca
# ---------------------------------------------------------------------------

@dataclass
class SearchNode:
    """Nó da árvore de busca A*.

    Atributos:
        state       (TSPState):           Estado do problema neste nó.
        parent      (Optional[SearchNode]): Nó pai (None para o nó raiz).
        action      (Optional[str]):      Ação que gerou este nó a partir do pai.
        path_cost   (float):              Custo acumulado g(n) desde a raiz.
        heuristic   (float):              Valor heurístico h(n) estimado.
        f_value     (float):              f(n) = g(n) + h(n) usado na fila.

    O campo `f_value` é gerado automaticamente no __post_init__.
    """

    state: TSPState
    parent: Optional["SearchNode"]
    action: Optional[str]
    path_cost: float
    heuristic: float
    f_value: float = field(init=False)

    def __post_init__(self) -> None:
        self.f_value = self.path_cost + self.heuristic

    # Protocolo de comparação necessário para heapq (min-heap por f_value).
    def __lt__(self, other: "SearchNode") -> bool:
        return self.f_value < other.f_value

    def __le__(self, other: "SearchNode") -> bool:
        return self.f_value <= other.f_value

    def __repr__(self) -> str:
        return (
            f"SearchNode(state={self.state!r}, "
            f"g={self.path_cost:.2f}, h={self.heuristic:.2f}, "
            f"f={self.f_value:.2f})"
        )


# ---------------------------------------------------------------------------
# Resultado da Busca
# ---------------------------------------------------------------------------

@dataclass
class SearchResult:
    """Encapsula o resultado completo de uma busca A*.

    Atributos:
        found         (bool):        Se uma solução foi encontrada.
        path          (List[str]):   Sequência de cidades (nomes) na solução.
        total_cost    (float):       Custo total do caminho ótimo.
        nodes_expanded (int):        Número de nós expandidos (nós explorados).
        nodes_generated (int):       Número de nós gerados (incluindo fronteira).
        elapsed_time  (float):       Tempo de execução em segundos.
        message       (str):         Mensagem descritiva do resultado.
    """

    found: bool
    path: List[str]
    total_cost: float
    nodes_expanded: int
    nodes_generated: int
    elapsed_time: float
    message: str = ""

    def __repr__(self) -> str:
        return (
            f"SearchResult(found={self.found}, cost={self.total_cost:.4f}, "
            f"nodes_expanded={self.nodes_expanded}, "
            f"time={self.elapsed_time:.4f}s)"
        )


# ---------------------------------------------------------------------------
# Algoritmo BUSCA-EM-GRAFO com A*
# ---------------------------------------------------------------------------

class AStarGraphSearch:
    """Implementação do algoritmo A* com BUSCA-EM-GRAFO.

    BUSCA-EM-GRAFO evita reexpansão de estados já explorados através de
    um conjunto explorado (closed set / tabela hash).

    Estruturas de Dados:
      - Fronteira (fringe): heapq (min-heap) ordenado por f(n) = g(n) + h(n).
      - Conjunto explorado: Python set de estados já expandidos.
      - Tabela de melhor custo: dict para rastrear o menor g(n) por estado
        na fronteira (permite lazy deletion eficiente).

    Args:
        problem (TSPProblem): Formulação do problema a ser resolvido.
    """

    def __init__(self, problem: TSPProblem) -> None:
        self.problem = problem

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def search(self, verbose: bool = False) -> SearchResult:
        """Executa a busca A* e retorna o resultado.

        Args:
            verbose (bool): Se True, imprime progresso a cada 1000 expansões.

        Returns:
            SearchResult com o caminho ótimo, custo e estatísticas.
        """
        start_time = time.perf_counter()

        # ---- Inicialização ----
        initial_state = self.problem.initial_state()
        h0 = self.problem.heuristic(initial_state)
        root = SearchNode(
            state=initial_state,
            parent=None,
            action=None,
            path_cost=0.0,
            heuristic=h0,
        )

        # Fronteira: lista usada como heap (min-heap por f_value).
        # Cada entrada: (f_value, counter, SearchNode) — counter quebra empates.
        frontier: List[Tuple[float, int, SearchNode]] = []
        counter = 0  # desempate determinístico (FIFO para igual f)
        heapq.heappush(frontier, (root.f_value, counter, root))

        # Tabela de melhor custo conhecida para estados na fronteira.
        # Usada para lazy deletion: só expandimos um nó se seu g(n)
        # ainda for o melhor para aquele estado.
        best_cost_in_frontier: Dict[TSPState, float] = {initial_state: 0.0}

        # Conjunto explorado (closed set) — tabela hash de estados.
        explored: set = set()

        nodes_expanded = 0
        nodes_generated = 1  # raiz já gerada

        # ---- Loop principal ----
        while frontier:
            _, _, node = heapq.heappop(frontier)

            # Lazy deletion: ignora nó obsoleto (custo superado por versão melhor).
            if node.state in explored:
                continue
            if best_cost_in_frontier.get(node.state, float("inf")) < node.path_cost:
                continue

            # ---- Teste de Objetivo ----
            if self.problem.is_goal(node.state):
                elapsed = time.perf_counter() - start_time
                path = self._reconstruct_path(node)
                return SearchResult(
                    found=True,
                    path=path,
                    total_cost=node.path_cost,
                    nodes_expanded=nodes_expanded,
                    nodes_generated=nodes_generated,
                    elapsed_time=elapsed,
                    message="Solução ótima encontrada pelo A*.",
                )

            # ---- Expansão ----
            explored.add(node.state)
            nodes_expanded += 1

            if verbose and nodes_expanded % 1_000 == 0:
                print(
                    f"  [A*] Expandidos: {nodes_expanded} | "
                    f"Fronteira: {len(frontier)} | "
                    f"f(n) atual: {node.f_value:.2f}"
                )

            for action, child_state, step_cost in self.problem.successors(node.state):
                if child_state in explored:
                    continue

                child_g = node.path_cost + step_cost
                nodes_generated += 1

                # Só insere na fronteira se o novo caminho é melhor.
                if child_g < best_cost_in_frontier.get(child_state, float("inf")):
                    best_cost_in_frontier[child_state] = child_g
                    child_h = self.problem.heuristic(child_state)
                    child_node = SearchNode(
                        state=child_state,
                        parent=node,
                        action=action,
                        path_cost=child_g,
                        heuristic=child_h,
                    )
                    counter += 1
                    heapq.heappush(frontier, (child_node.f_value, counter, child_node))

        # Fronteira esgotada sem solução.
        elapsed = time.perf_counter() - start_time
        return SearchResult(
            found=False,
            path=[],
            total_cost=float("inf"),
            nodes_expanded=nodes_expanded,
            nodes_generated=nodes_generated,
            elapsed_time=elapsed,
            message="Nenhuma solução encontrada (fronteira esgotada).",
        )

    # ------------------------------------------------------------------
    # Helper privado
    # ------------------------------------------------------------------

    @staticmethod
    def _reconstruct_path(node: SearchNode) -> List[str]:
        """Reconstrói o caminho percorrido a partir do nó objetivo.

        Percorre os ponteiros `parent` de volta até a raiz e inverte.

        Args:
            node: Nó objetivo da busca.

        Returns:
            Lista de nomes de cidades na ordem do caminho percorrido.
        """
        path: List[str] = []
        current: Optional[SearchNode] = node
        while current is not None:
            path.append(current.state.current_city.name)
            current = current.parent
        path.reverse()
        return path
