"""
tsp_problem.py
--------------
Formulação formal do Problema do Caixeiro Viajante (TSP).

Responsabilidades:
  - Definir o Estado do agente.
  - Implementar Estado Inicial, Função Sucessor, Teste de Objetivo e Custo.
  - Fornecer a heurística h(n) para o algoritmo A*.

Esta camada separa a *semântica do problema* da *estratégia de busca*,
seguindo os princípios PEAS (Performance, Environment, Actuators, Sensors).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import FrozenSet, List, Optional, Tuple

from tsp_environment import City, TSPEnvironment


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TSPState:
    """Estado imutável do agente no TSP.

    Um estado é uma fotografia completa da situação do agente:

    Atributos:
        current_city    (City):           Cidade onde o agente se encontra.
        visited_cities  (FrozenSet[str]): Conjunto imutável dos nomes de
                                          cidades já visitadas. Usar frozenset
                                          garante que estados logicamente
                                          equivalentes possuam o mesmo hash,
                                          permitindo deduplicação eficiente
                                          na tabela de explorados.
    """

    current_city: City
    visited_cities: FrozenSet[str]

    def __hash__(self) -> int:
        # Hashing explícito para maior clareza (frozen=True já provê isso).
        return hash((self.current_city.name, self.visited_cities))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TSPState):
            return NotImplemented
        return (
            self.current_city.name == other.current_city.name
            and self.visited_cities == other.visited_cities
        )

    def __repr__(self) -> str:
        visited = sorted(self.visited_cities)
        return f"TSPState(at={self.current_city.name!r}, visited={visited})"


# ---------------------------------------------------------------------------
# Formulação do Problema
# ---------------------------------------------------------------------------

class TSPProblem:
    """Formulação PEAS do TSP para uso com algoritmos de busca.

    A classe encapsula:
      - Estado inicial
      - Função sucessor (transições válidas)
      - Teste de objetivo
      - Custo do passo
      - Heurística admissível h(n) para A*

    Args:
        environment  (TSPEnvironment): Ambiente com cidades e distâncias.
        origin_city  (City):           Cidade de partida e retorno.
    """

    def __init__(self, environment: TSPEnvironment, origin_city: City) -> None:
        self.environment = environment
        self.origin_city = origin_city
        self._all_city_names: FrozenSet[str] = frozenset(
            c.name for c in environment.cities
        )

    # ------------------------------------------------------------------
    # 1. Estado Inicial
    # ------------------------------------------------------------------

    def initial_state(self) -> TSPState:
        """Retorna o estado inicial do agente.

        O agente começa na cidade de origem, que já está marcada
        como visitada.

        Returns:
            TSPState com cidade atual = origem e visitadas = {origem}.
        """
        return TSPState(
            current_city=self.origin_city,
            visited_cities=frozenset([self.origin_city.name]),
        )

    # ------------------------------------------------------------------
    # 2. Função Sucessor
    # ------------------------------------------------------------------

    def successors(
        self, state: TSPState
    ) -> List[Tuple[str, TSPState, float]]:
        """Gera todos os estados sucessores válidos a partir de `state`.

        O agente pode se mover para qualquer cidade ainda não visitada.
        Se todas as cidades foram visitadas, o único movimento permitido
        é retornar à cidade de origem (fechamento do ciclo).

        Args:
            state: Estado atual do agente.

        Returns:
            Lista de tuplas (action, next_state, step_cost) onde:
              - action    (str):      Nome da cidade de destino.
              - next_state (TSPState): Novo estado após a ação.
              - step_cost  (float):   Custo do passo (distância euclidiana).
        """
        successors_list: List[Tuple[str, TSPState, float]] = []

        unvisited = self._all_city_names - state.visited_cities

        if unvisited:
            # Caso geral: mover para uma cidade ainda não visitada.
            for neighbor in self.environment.neighbors(state.current_city):
                if neighbor.name in unvisited:
                    step_cost = self.environment.distance(
                        state.current_city, neighbor
                    )
                    next_state = TSPState(
                        current_city=neighbor,
                        visited_cities=state.visited_cities | frozenset([neighbor.name]),
                    )
                    successors_list.append((neighbor.name, next_state, step_cost))
        else:
            # Caso de retorno: todas visitadas → voltar à origem.
            step_cost = self.environment.distance(
                state.current_city, self.origin_city
            )
            next_state = TSPState(
                current_city=self.origin_city,
                visited_cities=state.visited_cities,
            )
            successors_list.append(
                (self.origin_city.name, next_state, step_cost)
            )

        return successors_list

    # ------------------------------------------------------------------
    # 3. Teste de Objetivo
    # ------------------------------------------------------------------

    def is_goal(self, state: TSPState) -> bool:
        """Verifica se o estado é um objetivo (solução completa).

        A solução é válida quando:
          (a) Todas as cidades foram visitadas.
          (b) O agente retornou à cidade de origem.

        Args:
            state: Estado a ser verificado.

        Returns:
            True se o estado é objetivo, False caso contrário.
        """
        return (
            state.visited_cities == self._all_city_names
            and state.current_city.name == self.origin_city.name
        )

    # ------------------------------------------------------------------
    # 4. Custo do Caminho (Custo do Passo)
    # ------------------------------------------------------------------

    def step_cost(self, from_city: City, to_city: City) -> float:
        """Retorna o custo de uma transição (distância euclidiana).

        Args:
            from_city: Cidade de origem.
            to_city:   Cidade de destino.

        Returns:
            Distância euclidiana entre as duas cidades.
        """
        return self.environment.distance(from_city, to_city)

    # ------------------------------------------------------------------
    # 5. Heurística h(n) para A* — Admissível e Consistente
    # ------------------------------------------------------------------

    def heuristic(self, state: TSPState) -> float:
        """Heurística admissível para A*: distância até a cidade não visitada mais próxima.

        Estratégia:
          - Calcula a distância da cidade atual até cada cidade *não visitada*.
          - Retorna o *mínimo* dessas distâncias.
          - Se não há cidades não visitadas, retorna a distância de retorno
            à origem (caso todas já foram visitadas mas ainda não voltou).
          - Se já está na origem com todas visitadas, retorna 0.

        Admissibilidade:
          Esta heurística nunca superestima o custo real, pois o agente
          precisará percorrer *pelo menos* a distância até a cidade mais
          próxima não visitada antes de concluir o tour.

        Args:
            state: Estado atual do agente.

        Returns:
            Estimativa admissível do custo restante.
        """
        unvisited_names = self._all_city_names - state.visited_cities
        city_map = self.environment.city_map

        if not unvisited_names:
            # Todas visitadas: o custo restante é o retorno à origem.
            if state.current_city.name == self.origin_city.name:
                return 0.0
            return self.environment.distance(state.current_city, self.origin_city)

        # Distância mínima até qualquer cidade não visitada.
        min_dist = min(
            self.environment.distance(state.current_city, city_map[name])
            for name in unvisited_names
        )
        return min_dist

    # ------------------------------------------------------------------
    # Representação
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        n = len(self.environment.cities)
        return (
            f"TSPProblem(cities={n}, origin={self.origin_city.name!r})"
        )
