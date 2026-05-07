"""
tsp_environment.py
------------------
Define o ambiente do Problema do Caixeiro Viajante (TSP).

Responsabilidades:
  - Representar cidades com coordenadas (x, y).
  - Calcular distâncias euclidianas.
  - Expor o grafo de adjacência completo (problema simétrico).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Estruturas de Dados do Ambiente
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class City:
    """Representa uma cidade no espaço euclidiano 2-D.

    Atributos:
        name (str): Identificador único da cidade.
        x    (float): Coordenada horizontal.
        y    (float): Coordenada vertical.
    """
    name: str
    x: float
    y: float

    def __repr__(self) -> str:
        return f"City({self.name!r}, x={self.x}, y={self.y})"


@dataclass
class TSPEnvironment:
    """Ambiente determinístico e totalmente observável para o TSP.

    Parâmetros:
        cities (List[City]): Lista de cidades do problema.

    Propriedades Calculadas:
        _distance_cache: Cache de distâncias euclidianas pré-calculadas
                         para acesso em O(1).
    """

    cities: List[City]
    _distance_cache: Dict[Tuple[str, str], float] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        """Pré-calcula e armazena em cache todas as distâncias par-a-par."""
        for i, city_a in enumerate(self.cities):
            for city_b in self.cities[i + 1 :]:
                dist = self._euclidean(city_a, city_b)
                self._distance_cache[(city_a.name, city_b.name)] = dist
                self._distance_cache[(city_b.name, city_a.name)] = dist
        # Distância de uma cidade para ela mesma
        for city in self.cities:
            self._distance_cache[(city.name, city.name)] = 0.0

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    @property
    def city_map(self) -> Dict[str, City]:
        """Dicionário {nome -> City} para acesso rápido por nome."""
        return {city.name: city for city in self.cities}

    def distance(self, city_a: City, city_b: City) -> float:
        """Retorna a distância euclidiana entre duas cidades (com cache).

        Args:
            city_a: Cidade de origem.
            city_b: Cidade de destino.

        Returns:
            Distância euclidiana (float).
        """
        return self._distance_cache[(city_a.name, city_b.name)]

    def neighbors(self, city: City) -> List[City]:
        """Retorna todas as cidades acessíveis a partir de `city` (grafo completo).

        No TSP simétrico, qualquer cidade pode ser visitada a partir de qualquer outra.

        Args:
            city: Cidade atual.

        Returns:
            Lista de cidades vizinhas (todas exceto a própria).
        """
        return [c for c in self.cities if c.name != city.name]

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    @staticmethod
    def _euclidean(city_a: City, city_b: City) -> float:
        """Calcula a distância euclidiana entre dois pontos."""
        return math.sqrt((city_a.x - city_b.x) ** 2 + (city_a.y - city_b.y) ** 2)

    def __repr__(self) -> str:
        names = [c.name for c in self.cities]
        return f"TSPEnvironment(cities={names})"
