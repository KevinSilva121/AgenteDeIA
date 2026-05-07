"""
tests/test_shortest_path.py
----------------------------
Testes unitários para o Agente de Caminho Mínimo.

Cobre:
  - Validade do ambiente (cidades e adjacências).
  - Formulação do problema (estados, ações, custo).
  - Algoritmo UCS (resultado, custo ótimo, caminho correto).
  - Casos extremos: origem == destino, cidades sem saída.
"""

import sys
import os

# Garante que o diretório raiz do projeto esteja no path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from romania_environment import RomaniaEnvironment, Neighbor
from romania_problem import Node, ShortestPathProblem
from ucs_search import UniformCostSearch
from shortest_path_agent import ShortestPathAgent


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def env() -> RomaniaEnvironment:
    return RomaniaEnvironment()


@pytest.fixture
def problem_arad_bucharest(env) -> ShortestPathProblem:
    return ShortestPathProblem(env, origin="Arad", destination="Bucharest")


# ===========================================================================
# Testes do Ambiente
# ===========================================================================

class TestRomaniaEnvironment:

    def test_total_cities(self, env):
        """O mapa deve ter exatamente 20 cidades."""
        assert len(env.cities) == 20

    def test_known_city_exists(self, env):
        assert env.is_valid_city("Arad")
        assert env.is_valid_city("Bucharest")
        assert env.is_valid_city("Eforie")

    def test_unknown_city_does_not_exist(self, env):
        assert not env.is_valid_city("Paris")
        assert not env.is_valid_city("")

    def test_neighbors_arad(self, env):
        """Arad deve ter 3 vizinhos com distâncias corretas."""
        neighbors = {n.city: n.distance for n in env.neighbors("Arad")}
        assert neighbors == {"Zerind": 75, "Sibiu": 140, "Timisoara": 118}

    def test_neighbors_bucharest(self, env):
        """Bucharest deve ter 4 vizinhos."""
        names = {n.city for n in env.neighbors("Bucharest")}
        assert names == {"Fagaras", "Pitesti", "Giurgiu", "Urziceni"}

    def test_symmetry(self, env):
        """Todas as arestas devem ser simétricas."""
        for city in env.cities:
            for neighbor in env.neighbors(city):
                reverse = {n.city: n.distance for n in env.neighbors(neighbor.city)}
                assert city in reverse, f"Aresta {city}↔{neighbor.city} não é simétrica"
                assert reverse[city] == neighbor.distance

    def test_distance_arad_sibiu(self, env):
        assert env.distance("Arad", "Sibiu") == 140
        assert env.distance("Sibiu", "Arad") == 140  # simetria

    def test_invalid_city_raises(self, env):
        with pytest.raises(KeyError):
            env.neighbors("Roma")

    def test_non_adjacent_distance_raises(self, env):
        with pytest.raises(ValueError):
            env.distance("Arad", "Bucharest")  # não são adjacentes


# ===========================================================================
# Testes do Nó
# ===========================================================================

class TestNode:

    def test_solution_path_root(self):
        root = Node(state="Arad", parent=None, path_cost=0)
        assert root.solution_path() == ["Arad"]

    def test_solution_path_chain(self):
        n0 = Node("Arad", None, 0)
        n1 = Node("Sibiu", n0, 140)
        n2 = Node("Rimnicu Vilcea", n1, 220)
        n3 = Node("Pitesti", n2, 317)
        n4 = Node("Bucharest", n3, 418)
        assert n4.solution_path() == [
            "Arad", "Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest"
        ]

    def test_node_comparison(self):
        n1 = Node("A", None, 100)
        n2 = Node("B", None, 200)
        assert n1 < n2


# ===========================================================================
# Testes da Formulação do Problema
# ===========================================================================

class TestShortestPathProblem:

    def test_initial_state(self, problem_arad_bucharest):
        assert problem_arad_bucharest.initial_state() == "Arad"

    def test_goal_test_true(self, problem_arad_bucharest):
        assert problem_arad_bucharest.goal_test("Bucharest")

    def test_goal_test_false(self, problem_arad_bucharest):
        assert not problem_arad_bucharest.goal_test("Sibiu")

    def test_actions_returns_neighbors(self, problem_arad_bucharest):
        actions = problem_arad_bucharest.actions("Arad")
        cities = {a.city for a in actions}
        assert "Zerind" in cities
        assert "Sibiu" in cities
        assert "Timisoara" in cities

    def test_result_returns_city(self, env):
        problem = ShortestPathProblem(env, "Arad", "Bucharest")
        action = Neighbor("Sibiu", 140)
        assert problem.result(action) == "Sibiu"

    def test_step_cost(self, problem_arad_bucharest):
        action = Neighbor("Sibiu", 140)
        assert problem_arad_bucharest.step_cost("Arad", action) == 140

    def test_invalid_origin_raises(self, env):
        with pytest.raises(ValueError):
            ShortestPathProblem(env, "Roma", "Bucharest")

    def test_invalid_destination_raises(self, env):
        with pytest.raises(ValueError):
            ShortestPathProblem(env, "Arad", "Lisboa")


# ===========================================================================
# Testes do Algoritmo UCS
# ===========================================================================

class TestUniformCostSearch:

    def test_arad_to_bucharest_cost(self, problem_arad_bucharest):
        """Custo ótimo Arad→Bucharest deve ser 418 km (AIMA)."""
        result = UniformCostSearch(problem_arad_bucharest).search()
        assert result.found
        assert result.total_cost == 418

    def test_arad_to_bucharest_path(self, problem_arad_bucharest):
        """Caminho ótimo: Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest."""
        result = UniformCostSearch(problem_arad_bucharest).search()
        assert result.path == [
            "Arad", "Sibiu", "Rimnicu Vilcea", "Pitesti", "Bucharest"
        ]

    def test_same_city(self, env):
        """Origem == destino deve retornar custo 0 e caminho de 1 cidade."""
        problem = ShortestPathProblem(env, "Arad", "Arad")
        result = UniformCostSearch(problem).search()
        assert result.found
        assert result.total_cost == 0
        assert result.path == ["Arad"]

    def test_adjacent_cities(self, env):
        """Cidades adjacentes: custo deve ser a distância direta."""
        problem = ShortestPathProblem(env, "Arad", "Zerind")
        result = UniformCostSearch(problem).search()
        assert result.found
        assert result.total_cost == 75
        assert result.path == ["Arad", "Zerind"]

    def test_nodes_expanded_positive(self, problem_arad_bucharest):
        result = UniformCostSearch(problem_arad_bucharest).search()
        assert result.nodes_expanded > 0

    def test_nodes_generated_gte_expanded(self, problem_arad_bucharest):
        result = UniformCostSearch(problem_arad_bucharest).search()
        assert result.nodes_generated >= result.nodes_expanded

    def test_elapsed_time_positive(self, problem_arad_bucharest):
        result = UniformCostSearch(problem_arad_bucharest).search()
        assert result.elapsed_time >= 0

    def test_oradea_to_eforie(self, env):
        """Verifica que UCS encontra solução em rotas mais longas."""
        problem = ShortestPathProblem(env, "Oradea", "Eforie")
        result = UniformCostSearch(problem).search()
        assert result.found
        # Verifica que o caminho começa e termina correto
        assert result.path[0] == "Oradea"
        assert result.path[-1] == "Eforie"
        # Verifica que o custo é positivo
        assert result.total_cost > 0


# ===========================================================================
# Testes de Integração (Agente Completo)
# ===========================================================================

class TestShortestPathAgent:

    def test_agent_run_returns_result(self):
        agent = ShortestPathAgent("Arad", "Bucharest")
        result = agent.run()
        assert result.found
        assert result.total_cost == 418

    def test_agent_path_format(self):
        agent = ShortestPathAgent("Arad", "Bucharest")
        result = agent.run()
        assert isinstance(result.path, list)
        assert all(isinstance(c, str) for c in result.path)

    def test_agent_same_city(self):
        agent = ShortestPathAgent("Sibiu", "Sibiu")
        result = agent.run()
        assert result.found
        assert result.total_cost == 0
