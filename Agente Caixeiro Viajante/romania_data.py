"""
romania_data.py
---------------
Contém as constantes de dados para o mapa da Romênia (cidades, coordenadas e conexões rodoviárias)
e a lógica para computar a matriz de menores caminhos via Floyd-Warshall.
"""

from typing import Dict, Tuple

# Coordenadas 2D aproximadas (x, y) de cada cidade para cálculo de heurística e visualização
ROMANIA_COORDINATES: Dict[str, Tuple[float, float]] = {
    "Arad": (91.0, 492.0),
    "Bucharest": (400.0, 327.0),
    "Craiova": (253.0, 288.0),       # Grafia "Craiova" conforme a imagem
    "Dobreta": (165.0, 299.0),       # Grafia "Dobreta" conforme a imagem
    "Eforie": (562.0, 293.0),
    "Fagaras": (305.0, 449.0),
    "Giurgiu": (375.0, 270.0),
    "Hirsova": (534.0, 350.0),
    "Iasi": (473.0, 506.0),
    "Lugoj": (165.0, 379.0),
    "Mehadia": (168.0, 339.0),
    "Neamt": (406.0, 537.0),
    "Oradea": (131.0, 571.0),
    "Pitesti": (320.0, 368.0),
    "Rimnicu Vilcea": (233.0, 410.0), # Grafia "Rimnicu Vilcea" conforme a imagem
    "Sibiu": (207.0, 457.0),
    "Timisoara": (94.0, 410.0),
    "Urziceni": (456.0, 350.0),
    "Vaslui": (509.0, 444.0),
    "Zerind": (108.0, 531.0)
}

# Conexões de estradas diretas e seus comprimentos (pesos das arestas) conforme a imagem
ROMANIA_CONNECTIONS: Dict[str, Dict[str, float]] = {
    "Oradea": {"Zerind": 71.0, "Sibiu": 151.0},
    "Zerind": {"Arad": 75.0, "Oradea": 71.0},
    "Arad": {"Zerind": 75.0, "Sibiu": 140.0, "Timisoara": 118.0},
    "Timisoara": {"Arad": 118.0, "Lugoj": 111.0},
    "Lugoj": {"Timisoara": 111.0, "Mehadia": 70.0},
    "Mehadia": {"Lugoj": 70.0, "Dobreta": 75.0},
    "Dobreta": {"Mehadia": 75.0, "Craiova": 120.0},
    "Craiova": {"Dobreta": 120.0, "Rimnicu Vilcea": 146.0, "Pitesti": 138.0},
    "Sibiu": {"Oradea": 151.0, "Arad": 140.0, "Rimnicu Vilcea": 80.0, "Fagaras": 99.0},
    "Rimnicu Vilcea": {"Sibiu": 80.0, "Craiova": 146.0, "Pitesti": 97.0},
    "Fagaras": {"Sibiu": 99.0, "Bucharest": 211.0},
    "Pitesti": {"Rimnicu Vilcea": 97.0, "Craiova": 138.0, "Bucharest": 101.0},
    "Bucharest": {"Fagaras": 211.0, "Pitesti": 101.0, "Giurgiu": 90.0, "Urziceni": 85.0},
    "Giurgiu": {"Bucharest": 90.0},
    "Urziceni": {"Bucharest": 85.0, "Hirsova": 98.0, "Vaslui": 142.0},
    "Hirsova": {"Urziceni": 98.0, "Eforie": 86.0},
    "Eforie": {"Hirsova": 86.0},
    "Vaslui": {"Urziceni": 142.0, "Iasi": 92.0},
    "Iasi": {"Vaslui": 92.0, "Neamt": 87.0},
    "Neamt": {"Iasi": 87.0}
}


def compute_shortest_paths() -> Dict[str, Dict[str, float]]:
    """Calcula a matriz de distâncias de menor caminho entre todas as cidades do mapa da Romênia.

    Utiliza o algoritmo clássico de Floyd-Warshall para encontrar a rota rodoviária mais curta
    entre qualquer par de cidades, de modo que o caixeiro viajante possa viajar de uma cidade
    para outra mesmo que não haja uma estrada direta entre elas.

    Returns:
        Um dicionário aninhado onde d[cidade_a][cidade_b] é a distância mínima de estrada.
    """
    cities = list(ROMANIA_CONNECTIONS.keys())
    dist: Dict[str, Dict[str, float]] = {}

    # Inicializa a matriz com distâncias conhecidas e infinito
    for u in cities:
        dist[u] = {}
        for v in cities:
            if u == v:
                dist[u][v] = 0.0
            elif v in ROMANIA_CONNECTIONS[u]:
                dist[u][v] = ROMANIA_CONNECTIONS[u][v]
            else:
                dist[u][v] = float("inf")

    # Algoritmo de Floyd-Warshall
    for k in cities:
        for i in cities:
            for j in cities:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist
