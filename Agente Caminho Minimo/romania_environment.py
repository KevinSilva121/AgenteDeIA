"""
romania_environment.py
----------------------
Ambiente do Mapa da Romênia.

Representa o grafo de cidades e as distâncias reais (em km) entre
cidades adjacentes, conforme o mapa clássico de Russell & Norvig (AIMA).

Responsabilidade única: modelar o mundo (cidades e conexões).
O agente não precisa saber como o mapa é armazenado internamente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Estrutura de dados: Vizinho
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Neighbor:
    """Representa uma cidade vizinha e a distância até ela (em km)."""
    city: str
    distance: int


# ---------------------------------------------------------------------------
# Ambiente: Mapa da Romênia
# ---------------------------------------------------------------------------

class RomaniaEnvironment:
    """Mapa estático com todas as cidades e estradas da Romênia (AIMA).

    O ambiente fornece:
      - Lista de todas as cidades disponíveis.
      - Mapa de adjacências: para cada cidade, suas vizinhas e distâncias.

    Uso:
        env = RomaniaEnvironment()
        vizinhos = env.neighbors("Arad")
        # → [Neighbor("Zerind", 75), Neighbor("Sibiu", 140), Neighbor("Timisoara", 118)]
    """

    # Grafo do mapa da Romênia (bidirecional).
    # Fonte: Russell & Norvig — Artificial Intelligence: A Modern Approach (AIMA).
    _ROAD_MAP: Dict[str, List[Tuple[str, int]]] = {
        "Arad":            [("Zerind", 75),  ("Sibiu", 140),  ("Timisoara", 118)],
        "Zerind":          [("Arad", 75),    ("Oradea", 71)],
        "Oradea":          [("Zerind", 71),  ("Sibiu", 151)],
        "Sibiu":           [("Arad", 140),   ("Oradea", 151), ("Fagaras", 99),  ("Rimnicu Vilcea", 80)],
        "Timisoara":       [("Arad", 118),   ("Lugoj", 111)],
        "Lugoj":           [("Timisoara", 111), ("Mehadia", 70)],
        "Mehadia":         [("Lugoj", 70),   ("Dobreta", 75)],
        "Dobreta":         [("Mehadia", 75), ("Craiova", 120)],
        "Craiova":         [("Dobreta", 120), ("Rimnicu Vilcea", 146), ("Pitesti", 138)],
        "Rimnicu Vilcea":  [("Sibiu", 80),   ("Craiova", 146), ("Pitesti", 97)],
        "Fagaras":         [("Sibiu", 99),   ("Bucharest", 211)],
        "Pitesti":         [("Rimnicu Vilcea", 97), ("Craiova", 138), ("Bucharest", 101)],
        "Bucharest":       [("Fagaras", 211), ("Pitesti", 101), ("Giurgiu", 90), ("Urziceni", 85)],
        "Giurgiu":         [("Bucharest", 90)],
        "Urziceni":        [("Bucharest", 85), ("Hirsova", 98), ("Vaslui", 142)],
        "Hirsova":         [("Urziceni", 98), ("Eforie", 86)],
        "Eforie":          [("Hirsova", 86)],
        "Vaslui":          [("Urziceni", 142), ("Iasi", 92)],
        "Iasi":            [("Vaslui", 92),  ("Neamt", 87)],
        "Neamt":           [("Iasi", 87)],
    }

    def __init__(self) -> None:
        # Converte para objetos Neighbor para interface tipada e imutável
        self._graph: Dict[str, List[Neighbor]] = {
            city: [Neighbor(neighbor, dist) for neighbor, dist in neighbors]
            for city, neighbors in self._ROAD_MAP.items()
        }

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    @property
    def cities(self) -> List[str]:
        """Retorna a lista de todas as cidades do mapa."""
        return list(self._graph.keys())

    def neighbors(self, city: str) -> List[Neighbor]:
        """Retorna os vizinhos diretos de uma cidade com suas distâncias.

        Args:
            city: Nome da cidade (case-sensitive).

        Returns:
            Lista de Neighbor(city, distance).

        Raises:
            KeyError: Se a cidade não existir no mapa.
        """
        if city not in self._graph:
            raise KeyError(
                f"Cidade '{city}' não encontrada no mapa. "
                f"Cidades disponíveis: {sorted(self.cities)}"
            )
        return self._graph[city]

    def distance(self, city_a: str, city_b: str) -> int:
        """Retorna a distância (km) entre duas cidades adjacentes.

        Args:
            city_a: Cidade de origem.
            city_b: Cidade de destino.

        Returns:
            Distância em km.

        Raises:
            ValueError: Se as cidades não forem adjacentes.
        """
        for neighbor in self.neighbors(city_a):
            if neighbor.city == city_b:
                return neighbor.distance
        raise ValueError(
            f"'{city_a}' e '{city_b}' não são cidades adjacentes no mapa."
        )

    def is_valid_city(self, city: str) -> bool:
        """Verifica se uma cidade existe no mapa."""
        return city in self._graph

    def __repr__(self) -> str:
        return f"RomaniaEnvironment(cidades={len(self._graph)})"
