"""
ucs_search.py
-------------
Busca de Custo Uniforme (Uniform-Cost Search — UCS).

Implementa a Busca-em-Grafo com:
  - Fila de Prioridade (min-heap) para a BORDA (fringe/frontier).
  - Lista Fechada (closed set / explored set) para evitar ciclos.
  - Expansão sempre pelo nó de MENOR CUSTO ACUMULADO g(n).

Referência: Russell & Norvig, AIMA — Seção 3.4.2
             "Uniform-cost search is the algorithm of choice when step
              costs vary."

Complexidade:
  - Temporal: O(b^(C*/ε))  — C* = custo da solução, ε = menor passo
  - Espacial: O(b^(C*/ε))  — mantém todos os nós na borda
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from typing import List, Optional, Set

from romania_problem import Node, ShortestPathProblem


# ---------------------------------------------------------------------------
# Resultado da Busca
# ---------------------------------------------------------------------------

@dataclass
class SearchResult:
    """Encapsula o resultado da busca UCS.

    Atributos:
        found          : True se uma solução foi encontrada.
        path           : Sequência de cidades do caminho (vazia se não encontrou).
        total_cost     : Custo total em km (0 se não encontrou).
        nodes_expanded : Número de nós expandidos (removidos da borda).
        nodes_generated: Número de nós gerados (inseridos na borda).
        elapsed_time   : Tempo de execução em segundos.
        message        : Mensagem descritiva sobre o resultado.
    """
    found: bool
    path: List[str]
    total_cost: int
    nodes_expanded: int
    nodes_generated: int
    elapsed_time: float
    message: str


# ---------------------------------------------------------------------------
# Algoritmo: Busca de Custo Uniforme
# ---------------------------------------------------------------------------

class UniformCostSearch:
    """Implementa a Busca de Custo Uniforme (UCS) em grafo.

    Estrutura de dados interna:
      - _frontier : min-heap de tuplas (g(n), contador, Node).
                    O contador evita comparações diretas entre Nodes quando
                    g(n) é idêntico (desempate por ordem de inserção — FIFO).
      - _explored : set de estados já expandidos (Lista Fechada).
      - _frontier_costs: dict {estado → melhor g(n) na borda} para
                         verificação rápida de duplicatas na borda.

    Args:
        problem (ShortestPathProblem): Problema formulado a resolver.
    """

    def __init__(self, problem: ShortestPathProblem) -> None:
        self._problem = problem

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def search(self, verbose: bool = False) -> SearchResult:
        """Executa a Busca de Custo Uniforme.

        Pseudocódigo (AIMA, Fig. 3.14):
            function UNIFORM-COST-SEARCH(problem) returns solution or failure
              node ← NODE(problem.INITIAL-STATE, path-cost=0)
              frontier ← priority queue ordered by PATH-COST, with node
              explored ← empty set
              loop do
                if EMPTY?(frontier) then return failure
                node ← POP(frontier)        (* nó com menor g(n) *)
                if problem.GOAL-TEST(node.STATE) then return SOLUTION(node)
                add node.STATE to explored
                for each action in problem.ACTIONS(node.STATE) do
                  child ← CHILD-NODE(problem, node, action)
                  if child.STATE not in explored and not in frontier then
                    frontier ← INSERT(child, frontier)
                  else if child in frontier with higher PATH-COST then
                    replace that frontier node with child

        Args:
            verbose: Se True, imprime cada expansão de nó.

        Returns:
            SearchResult com o caminho, custo e estatísticas.
        """
        start_time = time.perf_counter()

        # ── Inicialização ──────────────────────────────────────────────
        initial_state = self._problem.initial_state()
        root = Node(state=initial_state, parent=None, path_cost=0)

        # Borda: min-heap de (custo, contador, nó)
        _frontier: list = []
        _counter = 0  # desempate FIFO quando g(n) idêntico
        heapq.heappush(_frontier, (root.path_cost, _counter, root))
        _counter += 1

        # Mapa auxiliar: estado → melhor g(n) na borda (para atualizações)
        _frontier_costs: dict[str, int] = {initial_state: 0}

        # Lista Fechada: estados já completamente expandidos
        _explored: Set[str] = set()

        nodes_expanded = 0
        nodes_generated = 1  # o nó raiz já foi gerado

        # ── Loop principal ─────────────────────────────────────────────
        while _frontier:

            # 1. Remove o nó de MENOR CUSTO da borda
            cost, _, node = heapq.heappop(_frontier)

            # Nó pode ter entrado na heap mais de uma vez (versão lazy).
            # Ignora se já foi explorado (versão mais recente tem custo menor).
            if node.state in _explored:
                continue

            # 2. Teste de objetivo — retorna solução imediatamente
            if self._problem.goal_test(node.state):
                elapsed = time.perf_counter() - start_time
                return SearchResult(
                    found=True,
                    path=node.solution_path(),
                    total_cost=node.path_cost,
                    nodes_expanded=nodes_expanded,
                    nodes_generated=nodes_generated,
                    elapsed_time=elapsed,
                    message=(
                        f"Solução encontrada! "
                        f"{self._problem.origin} → {self._problem.destination} "
                        f"com custo {node.path_cost} km."
                    ),
                )

            # 3. Adiciona à Lista Fechada e expande
            _explored.add(node.state)
            nodes_expanded += 1

            if verbose:
                print(
                    f"    [UCS] Expandindo: {node.state:<20} "
                    f"g(n)={node.path_cost:>4} km"
                )

            # 4. Gera nós filhos para cada ação disponível
            for action in self._problem.actions(node.state):
                child_state = self._problem.result(action)

                # Ignora estados já na Lista Fechada
                if child_state in _explored:
                    continue

                child_cost = node.path_cost + self._problem.step_cost(node.state, action)
                child_node = Node(
                    state=child_state,
                    parent=node,
                    path_cost=child_cost,
                )
                nodes_generated += 1

                # Insere na borda se não está lá, ou atualiza se custo menor
                if child_state not in _frontier_costs or child_cost < _frontier_costs[child_state]:
                    _frontier_costs[child_state] = child_cost
                    heapq.heappush(_frontier, (child_cost, _counter, child_node))
                    _counter += 1

        # ── Borda vazia: sem solução ───────────────────────────────────
        elapsed = time.perf_counter() - start_time
        return SearchResult(
            found=False,
            path=[],
            total_cost=0,
            nodes_expanded=nodes_expanded,
            nodes_generated=nodes_generated,
            elapsed_time=elapsed,
            message=(
                f"Falha: nenhum caminho encontrado entre "
                f"'{self._problem.origin}' e '{self._problem.destination}'."
            ),
        )
