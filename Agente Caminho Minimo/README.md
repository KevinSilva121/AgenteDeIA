# Agente de Caminho Mínimo — Mapa da Romênia

Agente de Resolução de Problemas em Python que encontra o **caminho de menor custo** entre duas cidades do mapa clássico da Romênia, utilizando a **Busca de Custo Uniforme (UCS)** conforme definição do livro *Artificial Intelligence: A Modern Approach* (Russell & Norvig, AIMA).

---

## Estrutura do Projeto

```
Agente Caminho Minimo/
├── romania_environment.py    # Ambiente: cidades e distâncias do mapa
├── romania_problem.py        # Formulação: Node, estados, ações, custo
├── ucs_search.py             # Algoritmo: Busca de Custo Uniforme
├── shortest_path_agent.py    # Agente: orquestrador Formular→Buscar→Executar
├── main.py                   # Ponto de entrada
└── tests/
    └── test_shortest_path.py # Testes unitários e de integração
```

---

## Arquitetura

O agente segue o ciclo clássico do **Agente Solucionador de Problemas** (AIMA, Cap. 3):

```
┌──────────────────────────────────────────────────────────┐
│                    ShortestPathAgent                     │
│                                                          │
│  [1] FORMULAR  →  [2] BUSCAR  →  [3] EXECUTAR/REPORTAR  │
│        │                │                                │
│  RomaniaEnvironment  ShortestPathProblem  UniformCostSearch│
│  (cidades + km)      (Node, ações, g(n)) (heap + closed) │
└──────────────────────────────────────────────────────────┘
```

---

## Componentes Principais

### `romania_environment.py` — Ambiente
- Grafo bidirecional com **20 cidades** e todas as distâncias reais (km).
- Interface: `neighbors(city)` → `List[Neighbor(city, distance)]`.

### `romania_problem.py` — Formulação do Problema
- **`Node`**: armazena `state`, `parent` e `path_cost` (g(n)).
- **`ShortestPathProblem`**: define `initial_state()`, `actions()`, `result()`, `goal_test()`, `step_cost()`.

### `ucs_search.py` — Algoritmo UCS
- **Fila de Prioridade** (`heapq`) para a Borda — expande sempre o nó com menor g(n).
- **Lista Fechada** (`set`) para evitar re-expansão de estados já explorados.
- Suporte a **atualização de custo** na borda (lazy deletion).

### `shortest_path_agent.py` — Agente
- Orquestra os três módulos nas fases Formular → Buscar → Executar.

---

## Como Executar

```bash
# Caso principal: Arad → Bucharest
python main.py
```

**Saída esperada (caso Arad → Bucharest):**
```
════════════════════════════════════════════════════════════
  AGENTE DE CAMINHO MÍNIMO — MAPA DA ROMÊNIA
  Algoritmo: Busca de Custo Uniforme (UCS)
════════════════════════════════════════════════════════════
  Origem    : Arad
  Destino   : Bucharest

[1/3] FORMULANDO O PROBLEMA...
[2/3] EXECUTANDO A BUSCA UCS...
[3/3] SOLUÇÃO ENCONTRADA
──────────────────────────────────────────────────────────
  ✔ Solução encontrada! Arad → Bucharest com custo 418 km.

  CAMINHO MÍNIMO (4 etapas):
  ──────────────────────────────────────────────────────
    Etapa  1: Arad                 →  Sibiu                [140 km]
    Etapa  2: Sibiu                →  Rimnicu Vilcea       [ 80 km]
    Etapa  3: Rimnicu Vilcea       →  Pitesti              [ 97 km]
  ★ Etapa  4: Pitesti              →  Bucharest            [101 km]
  ──────────────────────────────────────────────────────

  ROTA    : Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest
  CUSTO   : 418 km
════════════════════════════════════════════════════════════
```

---

## Testes

```bash
# Rodar todos os testes
python -m pytest tests/ -v
```

---

## Referência Teórica

| Conceito         | Implementação                                 |
|------------------|-----------------------------------------------|
| Estado           | Nome da cidade (`str`)                        |
| Nó               | `Node(state, parent, path_cost)`              |
| Borda            | `heapq` (Fila de Prioridade por `g(n)`)       |
| Lista Fechada    | `set` de estados expandidos                   |
| Custo g(n)       | Soma das distâncias reais acumuladas (km)     |
| Critério UCS     | Expansão do nó com menor `path_cost`          |
| Garantia         | **Ótimo** se todos os custos de passo ≥ 0     |

> **Resultado canônico AIMA**: `Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest = 418 km`
