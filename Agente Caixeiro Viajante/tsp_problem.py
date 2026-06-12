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
        start_city   (City):           Cidade de partida.
        end_city     (Optional[City]): Cidade de destino final (se omitida, é igual a start_city).
        stops        (Optional[List[City]]): Paradas intermediárias (se omitida, todas as outras do ambiente).
    """

    def __init__(
        self,
        environment: TSPEnvironment,
        start_city: City,
        end_city: Optional[City] = None,
        stops: Optional[List[City]] = None,
    ) -> None:
        self.environment = environment
        self.start_city = start_city
        self.origin_city = start_city  # Para compatibilidade legada
        self.end_city = end_city if end_city is not None else start_city

        if stops is not None:
            self.stops = stops
        else:
            # Modo legado: todas as outras cidades do ambiente são paradas
            self.stops = [c for c in environment.cities if c.name != start_city.name]

        self.stops_names: FrozenSet[str] = frozenset(c.name for c in self.stops)
        self._all_city_names: FrozenSet[str] = frozenset(
            c.name for c in environment.cities
        )

    # ------------------------------------------------------------------
    # 1. Estado Inicial
    # ------------------------------------------------------------------

    def initial_state(self) -> TSPState:
        """Retorna o estado inicial do agente.

        O agente começa na cidade de início, que já está marcada
        como visitada.

        Returns:
            TSPState com cidade atual = início e visitadas = {início}.
        """
        return TSPState(
            current_city=self.start_city,
            visited_cities=frozenset([self.start_city.name]),
        )

    # ------------------------------------------------------------------
    # 2. Função Sucessor
    # ------------------------------------------------------------------

    def successors(
        self, state: TSPState
    ) -> List[Tuple[str, TSPState, float]]:
        """Gera todos os estados sucessores válidos a partir de `state`.

        O agente pode se mover para qualquer parada intermediária ainda não visitada.
        Se todas as paradas intermediárias foram visitadas, o único movimento permitido
        é ir para a cidade de destino final.

        Args:
            state: Estado atual do agente.

        Returns:
            Lista de tuplas (action, next_state, step_cost) onde:
              - action    (str):      Nome da cidade de destino.
              - next_state (TSPState): Novo estado após a ação.
              - step_cost  (float):   Custo do passo (distância).
        """
        successors_list: List[Tuple[str, TSPState, float]] = []

        unvisited_stops = self.stops_names - state.visited_cities

        if unvisited_stops:
            # Caso geral: mover para uma parada intermediária ainda não visitada.
            for neighbor in self.environment.neighbors(state.current_city):
                if neighbor.name in unvisited_stops:
                    step_cost = self.environment.distance(
                        state.current_city, neighbor
                    )
                    next_state = TSPState(
                        current_city=neighbor,
                        visited_cities=state.visited_cities | frozenset([neighbor.name]),
                    )
                    successors_list.append((neighbor.name, next_state, step_cost))
        else:
            # Caso de conclusão: todas as paradas visitadas → ir para o destino final.
            if state.current_city.name != self.end_city.name:
                step_cost = self.environment.distance(
                    state.current_city, self.end_city
                )
                next_state = TSPState(
                    current_city=self.end_city,
                    visited_cities=state.visited_cities | frozenset([self.end_city.name]),
                )
                successors_list.append(
                    (self.end_city.name, next_state, step_cost)
                )

        return successors_list

    # ------------------------------------------------------------------
    # 3. Teste de Objetivo
    # ------------------------------------------------------------------

    def is_goal(self, state: TSPState) -> bool:
        """Verifica se o estado é um objetivo (solução completa).

        A solução é válida quando:
          (a) Todas as paradas intermediárias foram visitadas.
          (b) O agente chegou à cidade de destino final.

        Args:
            state: Estado a ser verificado.

        Returns:
            True se o estado é objetivo, False caso contrário.
        """
        return (
            self.stops_names.issubset(state.visited_cities)
            and state.current_city.name == self.end_city.name
        )

    # ------------------------------------------------------------------
    # 4. Custo do Caminho (Custo do Passo)
    # ------------------------------------------------------------------

    def step_cost(self, from_city: City, to_city: City) -> float:
        """Retorna o custo de uma transição (distância).

        Args:
            from_city: Cidade de origem.
            to_city:   Cidade de destino.

        Returns:
            Distância entre as duas cidades.
        """
        return self.environment.distance(from_city, to_city)

    # ------------------------------------------------------------------
    # 5. Heurística h(n) para A* — Admissível e Consistente
    # ------------------------------------------------------------------

    def heuristic(self, state: TSPState) -> float:
        """Heurística admissível para A*: distância até a parada não visitada mais próxima.

        Estratégia:
          - Calcula a distância da cidade atual até cada parada intermediária *não visitada*.
          - Retorna o *mínimo* dessas distâncias.
          - Se todas as paradas intermediárias já foram visitadas, retorna a distância
            até a cidade de destino final.
          - Se já está no destino final com todas as paradas visitadas, retorna 0.

        Args:
            state: Estado atual do agente.

        Returns:
            Estimativa admissível do custo restante.
        """
        unvisited_stops = self.stops_names - state.visited_cities
        city_map = self.environment.city_map

        if not unvisited_stops:
            # Todas as paradas visitadas: o custo restante é ir ao destino final.
            if state.current_city.name == self.end_city.name:
                return 0.0
            return self.environment.distance(state.current_city, self.end_city)

        # Distância mínima até qualquer parada intermediária não visitada.
        min_dist = min(
            self.environment.distance(state.current_city, city_map[name])
            for name in unvisited_stops
        )
        return min_dist

    # ------------------------------------------------------------------
    # Representação
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        n_stops = len(self.stops)
        return (
            f"TSPProblem(start={self.start_city.name!r}, end={self.end_city.name!r}, stops={n_stops})"
        )
