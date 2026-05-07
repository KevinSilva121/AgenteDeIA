"""
romania_problem.py
------------------
Formulação formal do Problema do Caminho Mínimo na Romênia.

Segue a definição clássica de Russell & Norvig (AIMA):
  - Estado inicial  : cidade de partida.
  - Função de ações : vizinhos da cidade atual.
  - Modelo de transição: mover para o vizinho escolhido.
  - Teste de objetivo: cidade atual == cidade de destino.
  - Custo de passo  : distância real (km) entre cidades adjacentes.

Responsabilidade única: modelar o problema (não o ambiente, não o algoritmo).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from romania_environment import RomaniaEnvironment, Neighbor


# ---------------------------------------------------------------------------
# Estrutura: Nó de Busca
# ---------------------------------------------------------------------------

@dataclass
class Node:
    """Nó da árvore de busca conforme definição AIMA.

    Armazena:
      - state      : cidade representada por este nó.
      - parent     : nó pai na árvore de busca (None para o nó raiz).
      - path_cost  : custo acumulado g(n) do caminho raiz → este nó.
    """
    state: str
    parent: Optional["Node"]
    path_cost: int  # g(n) — custo acumulado

    def __lt__(self, other: "Node") -> bool:
        """Desempate por custo acumulado (usado internamente pela heap)."""
        return self.path_cost < other.path_cost

    def solution_path(self) -> List[str]:
        """Reconstrói o caminho do nó raiz até este nó.

        Percorre os pais recursivamente e inverte a lista para
        obter a sequência na ordem correta (origem → destino).

        Returns:
            Lista de nomes de cidades do caminho completo.
        """
        path: List[str] = []
        node: Optional[Node] = self
        while node is not None:
            path.append(node.state)
            node = node.parent
        path.reverse()
        return path


# ---------------------------------------------------------------------------
# Formulação: Problema de Caminho Mínimo
# ---------------------------------------------------------------------------

class ShortestPathProblem:
    """Define formalmente o Problema do Caminho Mínimo no mapa da Romênia.

    Conecta o Ambiente (RomaniaEnvironment) com a interface de busca:
      - initial_state() → estado inicial para o algoritmo.
      - actions()       → lista de ações possíveis (vizinhos).
      - result()        → estado resultante de uma ação.
      - goal_test()     → verifica se chegamos ao destino.
      - step_cost()     → custo de transição entre dois estados.

    Args:
        environment (RomaniaEnvironment): Mapa com cidades e distâncias.
        origin      (str): Cidade de partida.
        destination (str): Cidade de destino.
    """

    def __init__(
        self,
        environment: RomaniaEnvironment,
        origin: str,
        destination: str,
    ) -> None:
        if not environment.is_valid_city(origin):
            raise ValueError(f"Cidade de origem inválida: '{origin}'")
        if not environment.is_valid_city(destination):
            raise ValueError(f"Cidade de destino inválida: '{destination}'")

        self.environment = environment
        self.origin = origin
        self.destination = destination

    # ------------------------------------------------------------------
    # Interface formal do problema (AIMA)
    # ------------------------------------------------------------------

    def initial_state(self) -> str:
        """Retorna o estado inicial (cidade de partida)."""
        return self.origin

    def actions(self, state: str) -> List[Neighbor]:
        """Retorna as ações disponíveis no estado atual.

        Cada ação é um Neighbor (cidade vizinha + distância).

        Args:
            state: Nome da cidade atual.

        Returns:
            Lista de Neighbor representando estradas disponíveis.
        """
        return self.environment.neighbors(state)

    def result(self, action: Neighbor) -> str:
        """Retorna o estado resultante de executar uma ação.

        Args:
            action: Neighbor escolhido (estrada a percorrer).

        Returns:
            Nome da cidade de destino da ação.
        """
        return action.city

    def goal_test(self, state: str) -> bool:
        """Testa se o estado atual é o objetivo.

        Args:
            state: Nome da cidade atual.

        Returns:
            True se chegamos ao destino.
        """
        return state == self.destination

    def step_cost(self, from_state: str, action: Neighbor) -> int:
        """Retorna o custo do passo (distância em km).

        Args:
            from_state: Cidade de origem da ação.
            action: Neighbor com a cidade de destino e distância.

        Returns:
            Distância em km entre as duas cidades.
        """
        return action.distance

    def __repr__(self) -> str:
        return (
            f"ShortestPathProblem("
            f"origin='{self.origin}', "
            f"destination='{self.destination}')"
        )
