"""
tests/test_tsp.py
-----------------
Testes unitários para o Agente Caixeiro Viajante.

Execute com:
  python -m pytest tests/ -v
"""

import math
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tsp_environment import City, TSPEnvironment
from tsp_problem import TSPProblem, TSPState
from tsp_search import AStarGraphSearch
from tsp_agent import TSPAgent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def square_cities():
    """4 cidades nos cantos de um quadrado 3x3.

    A ─────── B
    │         │
    D ─────── C

    Distância dos lados: 3.0
    Distância diagonal:  3√2 ≈ 4.243
    Rota ótima (perímetro): A→B→C→D→A = 12.0
    """
    return [
        City("A", 0.0, 0.0),
        City("B", 3.0, 0.0),
        City("C", 3.0, 3.0),
        City("D", 0.0, 3.0),
    ]


@pytest.fixture
def triangle_cities():
    """3 cidades em triângulo equilátero (lado = 2)."""
    h = math.sqrt(3)  # ≈ 1.732
    return [
        City("P1", 0.0, 0.0),
        City("P2", 2.0, 0.0),
        City("P3", 1.0, h),
    ]


# ---------------------------------------------------------------------------
# Testes do Ambiente (TSPEnvironment)
# ---------------------------------------------------------------------------

class TestTSPEnvironment:

    def test_distance_symmetry(self, square_cities):
        env = TSPEnvironment(square_cities)
        city_map = env.city_map
        a, b = city_map["A"], city_map["B"]
        assert env.distance(a, b) == pytest.approx(env.distance(b, a))

    def test_distance_self_zero(self, square_cities):
        env = TSPEnvironment(square_cities)
        a = env.city_map["A"]
        assert env.distance(a, a) == pytest.approx(0.0)

    def test_distance_euclidean(self, square_cities):
        env = TSPEnvironment(square_cities)
        city_map = env.city_map
        # A=(0,0) → C=(3,3): sqrt(18) ≈ 4.2426
        assert env.distance(city_map["A"], city_map["C"]) == pytest.approx(
            math.sqrt(18), abs=1e-9
        )

    def test_neighbors_count(self, square_cities):
        env = TSPEnvironment(square_cities)
        a = env.city_map["A"]
        neighbors = env.neighbors(a)
        assert len(neighbors) == 3  # Todas exceto A

    def test_neighbors_no_self(self, square_cities):
        env = TSPEnvironment(square_cities)
        a = env.city_map["A"]
        names = [c.name for c in env.neighbors(a)]
        assert "A" not in names

    def test_city_map_keys(self, square_cities):
        env = TSPEnvironment(square_cities)
        assert set(env.city_map.keys()) == {"A", "B", "C", "D"}


# ---------------------------------------------------------------------------
# Testes da Formulação (TSPProblem)
# ---------------------------------------------------------------------------

class TestTSPProblem:

    def test_initial_state(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        state = problem.initial_state()
        assert state.current_city.name == "A"
        assert state.visited_cities == frozenset(["A"])

    def test_successors_from_initial(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        initial = problem.initial_state()
        successors = problem.successors(initial)
        # A partir de A, pode ir para B, C ou D (não visitados)
        actions = [s[0] for s in successors]
        assert set(actions) == {"B", "C", "D"}

    def test_successors_return_home(self, square_cities):
        """Quando todas visitadas, deve retornar à origem."""
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        # Estado: em D, todas visitadas
        all_visited = frozenset(["A", "B", "C", "D"])
        state = TSPState(
            current_city=env.city_map["D"],
            visited_cities=all_visited,
        )
        successors = problem.successors(state)
        assert len(successors) == 1
        action, next_state, _ = successors[0]
        assert action == "A"
        assert next_state.current_city.name == "A"

    def test_is_goal_true(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        goal_state = TSPState(
            current_city=origin,
            visited_cities=frozenset(["A", "B", "C", "D"]),
        )
        assert problem.is_goal(goal_state) is True

    def test_is_goal_false_not_all_visited(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        state = TSPState(
            current_city=origin,
            visited_cities=frozenset(["A", "B"]),
        )
        assert problem.is_goal(state) is False

    def test_is_goal_false_not_at_origin(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        state = TSPState(
            current_city=env.city_map["B"],
            visited_cities=frozenset(["A", "B", "C", "D"]),
        )
        assert problem.is_goal(state) is False

    def test_heuristic_admissible_zero_at_goal(self, square_cities):
        """Heurística deve ser 0 no estado objetivo."""
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        goal_state = TSPState(
            current_city=origin,
            visited_cities=frozenset(["A", "B", "C", "D"]),
        )
        assert problem.heuristic(goal_state) == pytest.approx(0.0)

    def test_heuristic_non_negative(self, square_cities):
        """Heurística deve ser sempre não-negativa."""
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        initial = problem.initial_state()
        assert problem.heuristic(initial) >= 0.0

    def test_state_hash_equality(self, square_cities):
        """Estados logicamente iguais devem ter mesmo hash (frozenset)."""
        env = TSPEnvironment(square_cities)
        city_a = env.city_map["A"]
        s1 = TSPState(city_a, frozenset(["A", "B"]))
        s2 = TSPState(city_a, frozenset(["B", "A"]))  # mesma ordem lógica
        assert s1 == s2
        assert hash(s1) == hash(s2)


# ---------------------------------------------------------------------------
# Testes da Busca (AStarGraphSearch)
# ---------------------------------------------------------------------------

class TestAStarSearch:

    def test_finds_solution_triangle(self, triangle_cities):
        env = TSPEnvironment(triangle_cities)
        origin = env.city_map["P1"]
        problem = TSPProblem(env, origin)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()
        assert result.found is True

    def test_finds_solution_square(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()
        assert result.found is True

    def test_optimal_cost_square(self, square_cities):
        """Rota ótima no quadrado 3x3 deve ser o perímetro = 12.0."""
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()
        assert result.total_cost == pytest.approx(12.0, abs=1e-9)

    def test_path_starts_and_ends_at_origin(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()
        assert result.path[0] == "A"
        assert result.path[-1] == "A"

    def test_path_visits_all_cities(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()
        # Todos os 4 nomes de cidades devem aparecer no caminho
        assert set(result.path) == {"A", "B", "C", "D"}

    def test_nodes_expanded_positive(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        problem = TSPProblem(env, origin)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()
        assert result.nodes_expanded > 0


# ---------------------------------------------------------------------------
# Testes de Integração (TSPAgent)
# ---------------------------------------------------------------------------

class TestTSPAgent:

    def test_agent_run_returns_result(self, square_cities):
        env = TSPEnvironment(square_cities)
        origin = env.city_map["A"]
        agent = TSPAgent(cities=square_cities, origin=origin, verbose=False)
        result = agent.run()
        assert result is not None
        assert result.found is True

    def test_agent_5_cities(self):
        cities = [
            City("A", 0.0, 0.0),
            City("B", 3.0, 4.0),
            City("C", 6.0, 1.0),
            City("D", 5.0, 5.0),
            City("E", 1.0, 6.0),
        ]
        agent = TSPAgent(cities=cities, origin=cities[0], verbose=False)
        result = agent.run()
        assert result.found is True
        assert result.total_cost > 0
        assert result.path[0] == result.path[-1] == "A"
        assert set(result.path) == {"A", "B", "C", "D", "E"}


class TestRomaniaTSP:

    def test_romania_environment_shortest_paths(self):
        cities = [
            City(name="Arad", x=91.0, y=492.0),
            City(name="Bucharest", x=400.0, y=327.0),
            City(name="Sibiu", x=207.0, y=457.0),
            City(name="Fagaras", x=305.0, y=449.0),
        ]
        env = TSPEnvironment(cities)
        city_map = env.city_map
        # Arad para Bucharest deve ser 418.0 (Arad-Sibiu: 140, Sibiu-Rimnicu Vilcea: 80, Rimnicu-Pitesti: 97, Pitesti-Bucharest: 101)
        assert env.distance(city_map["Arad"], city_map["Bucharest"]) == pytest.approx(418.0)
        # Sibiu para Bucharest deve ser 278.0
        assert env.distance(city_map["Sibiu"], city_map["Bucharest"]) == pytest.approx(278.0)

    def test_romania_search_optimal_tour(self):
        cities = [
            City(name="Arad", x=91.0, y=492.0),
            City(name="Bucharest", x=400.0, y=327.0),
            City(name="Sibiu", x=207.0, y=457.0),
            City(name="Fagaras", x=305.0, y=449.0),
        ]
        env = TSPEnvironment(cities)
        origin = env.city_map["Arad"]
        problem = TSPProblem(env, origin)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()
        assert result.found is True
        assert result.total_cost == pytest.approx(868.0)
        assert result.path[0] == "Arad"
        assert result.path[-1] == "Arad"
        assert set(result.path) == {"Arad", "Bucharest", "Sibiu", "Fagaras"}

    def test_romania_custom_route_start_end_stops(self):
        cities = [
            City(name="Arad", x=91.0, y=492.0),
            City(name="Bucharest", x=400.0, y=327.0),
            City(name="Sibiu", x=207.0, y=457.0),
            City(name="Fagaras", x=305.0, y=449.0),
            City(name="Zerind", x=108.0, y=531.0),
        ]
        env = TSPEnvironment(cities)
        city_map = env.city_map
        start = city_map["Arad"]
        end = city_map["Bucharest"]
        stops = [city_map["Zerind"], city_map["Sibiu"], city_map["Fagaras"]]

        problem = TSPProblem(env, start_city=start, end_city=end, stops=stops)
        searcher = AStarGraphSearch(problem)
        result = searcher.search()

        assert result.found is True
        assert result.total_cost == pytest.approx(600.0)
        assert result.path == ["Arad", "Zerind", "Sibiu", "Fagaras", "Bucharest"]


