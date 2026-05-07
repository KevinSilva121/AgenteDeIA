# Agente Caixeiro Viajante — TSP com A* (A-Estrela)

Agente de Resolução de Problemas autônomo em Python para o **Problema do Caixeiro Viajante (TSP)**, implementado seguindo a arquitetura clássica de IA: **Formular → Buscar → Executar**.

## Arquitetura do Projeto

```
Agente Caixeiro Viajante/
├── tsp_environment.py   # Ambiente: cidades, distâncias, grafo
├── tsp_problem.py       # Formulação: estado, sucessor, objetivo, heurística
├── tsp_search.py        # Algoritmo: A* (BUSCA-EM-GRAFO)
├── tsp_agent.py         # Agente: orquestrador Formular→Buscar→Executar
├── main.py              # Ponto de entrada (cenários de teste)
└── tests/
    └── test_tsp.py      # Testes unitários e de integração (pytest)
```

## Componentes

### `tsp_environment.py` — Ambiente
- **`City`**: dataclass imutável com `name`, `x`, `y`.
- **`TSPEnvironment`**: Pré-calcula e cacheia toda a matriz de distâncias euclidianas em `__post_init__`, garantindo acesso O(1).

### `tsp_problem.py` — Formulação PEAS
- **`TSPState`**: Tupla imutável `(current_city, visited_cities: frozenset)`. O uso de `frozenset` garante que estados logicamente equivalentes tenham o **mesmo hash**, essencial para a tabela de explorados.
- **`TSPProblem`**: Implementa todos os 5 elementos da formulação:

| Elemento | Implementação |
|---|---|
| Estado Inicial | `(Origem, {Origem})` |
| Função Sucessor | Todas as cidades não visitadas; ou retorno à origem |
| Teste de Objetivo | `visited == all_cities AND current == origin` |
| Custo do Passo | Distância euclidiana |
| Heurística h(n) | Distância mínima até a cidade não visitada mais próxima (admissível) |

### `tsp_search.py` — Algoritmo A*
- **`SearchNode`**: Nó da árvore com `g(n)`, `h(n)`, `f(n) = g+h` e ponteiro para o pai.
- **`AStarGraphSearch`**: Implementa BUSCA-EM-GRAFO com:
  - **Fronteira**: `heapq` (min-heap ordenado por `f(n)`)
  - **Conjunto explorado**: `set` Python (tabela hash, O(1) médio)
  - **Lazy deletion**: `dict` de melhor custo por estado para evitar reprocessamento sem remoção explícita do heap

### `tsp_agent.py` — Agente Orquestrador
Executa as 3 fases com output detalhado:
1. **FORMULAR**: Cria o ambiente e instancia `TSPProblem`
2. **BUSCAR**: Executa `AStarGraphSearch.search()`
3. **EXECUTAR**: Exibe rota, distâncias por passo e custo total

## Como Executar

```bash
# Executar os cenários de demonstração
python main.py

# Executar os testes unitários
python -m pytest tests/ -v
```

## Exemplo de Saída

```
============================================================
  AGENTE CAIXEIRO VIAJANTE — A* (BUSCA-EM-GRAFO)
============================================================

[1/3] FORMULANDO O PROBLEMA...
  ✔ Ambiente criado: 5 cidades.
  ✔ Cidade de origem: 'A'
  ✔ Estado inicial  : TSPState(at='A', visited=['A'])
  ✔ Espaço de estados: 5! / 5 = 24 rotas possíveis.

[2/3] EXECUTANDO A BUSCA A*...
  ✔ Busca concluída em 0.0123s
  ✔ Nós expandidos : 42
  ✔ Nós gerados    : 118

[3/3] EXECUTANDO A SOLUÇÃO...
------------------------------------------------------------
  ✔ Solução ótima encontrada pelo A*.

  ROTA ÓTIMA (5 movimentos):
  ──────────────────────────────────────────────────
  Passo  1:          A →  E           (distância:   6.0828)
  Passo  2:          E →  D           (distância:   4.1231)
  Passo  3:          D →  B           (distância:   2.2361)
  Passo  4:          B →  C           (distância:   3.6056)
  Passo  5:          C ↩  A           (distância:   6.0828)
  ──────────────────────────────────────────────────
  CUSTO TOTAL ÓTIMO : 22.1303
============================================================
```

## Decisões de Design

| Decisão | Justificativa |
|---|---|
| `frozenset` para cidades visitadas | Permite hashing de estados para a tabela de explorados |
| Cache de distâncias em `__post_init__` | Evita recalcular `sqrt` a cada expansão — O(1) vs O(1) com overhead |
| Lazy deletion com `best_cost_in_frontier` | Evita remoção O(n) do heap mantendo eficiência |
| Separação em 4 módulos | SRP: cada módulo tem uma única responsabilidade |
| Heurística: cidade mais próxima não visitada | Admissível (não superestima) e fácil de calcular |

## Requisitos

- Python 3.8+
- Bibliotecas da stdlib: `math`, `heapq`, `dataclasses`, `typing`
- Para testes: `pytest` (`pip install pytest`)
