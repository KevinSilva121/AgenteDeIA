# Agente Tabuleiro Deslizante — 8-Puzzle com A*

Solução do clássico **Quebra-Cabeça de 8 Peças** (8-puzzle) em Python
usando **Busca A\*** com heurística da **Distância de Manhattan (h₂)**,
conforme apresentado na Aula 7.

---

## Índice

- [O que é o 8-puzzle](#o-que-é-o-8-puzzle)
- [Por que A*](#por-que-a)
- [A heurística de Manhattan (h₂)](#a-heurística-de-manhattan-h)
- [Como funciona o algoritmo](#como-funciona-o-algoritmo)
- [Requisitos](#requisitos)
- [Como rodar](#como-rodar)
- [Como ler a saída](#como-ler-a-saída)
- [Anatomia do código](#anatomia-do-código)
- [Comparação com outras buscas](#comparação-com-outras-buscas)
- [FAQ](#faq)

---

## O que é o 8-puzzle

Tabuleiro **3x3** com 8 peças numeradas de 1 a 8 e um espaço vazio.
A cada jogada, uma peça adjacente ao espaço vazio pode "deslizar"
para ocupá-lo. O objetivo é organizar as peças em ordem:

```
Estado qualquer:        Estado objetivo:

  8  7  2                  1  2  3
  5  3  6                  4  5  6
  _  1  4                  7  8  _
```

### Representação no código
Tupla de tuplas (imutável, **hashável**):
```python
((1, 2, 3),
 (4, 5, 6),
 (7, 8, 0))   # 0 representa o espaço vazio
```

### Espaço de estados
- **9!/2 = 181.440** estados alcançáveis (metade do total — só uma das
  duas paridades é resolvível).
- **Profundidade média da solução**: ~22 movimentos para um tabuleiro
  embaralhado.
- **Profundidade máxima**: 31 movimentos (pior caso conhecido).

---

## Por que A*

A* combina o **melhor da busca informada** (usa heurística) com a
**garantia da busca uniforme** (encontra solução ótima):

```
f(n) = g(n) + h(n)
```

- `g(n)` = custo real do início até o nó `n` (= número de movimentos).
- `h(n)` = estimativa do custo de `n` até o objetivo (heurística).
- A fila de prioridade sempre expande o nó com menor `f(n)`.

### Garantias do A*

| Propriedade da heurística | Garantia do A* |
| ------------------------- | -------------- |
| **Admissível** (nunca superestima) | Solução **ótima** |
| **Consistente** (nunca diminui ao avançar) | Solução ótima **sem reabrir nós** |

Manhattan é **admissível e consistente** → A* encontra o caminho
mínimo sem desperdício.

---

## A heurística de Manhattan (h₂)

> Para cada peça (exceto o 0), distância **horizontal + vertical** até
> sua posição objetivo. Soma de todas essas distâncias = `h(n)`.

### Por que é admissível?
Cada peça precisa **no mínimo** percorrer essa distância para chegar
ao seu lugar — e cada movimento desloca apenas **uma** peça em **uma**
casa. Logo, h₂ nunca superestima o custo real.

### Comparação com h₁ (peças fora do lugar)

| Heurística | Como calcula | Qualidade |
| ---------- | ------------ | --------- |
| **h₁** (peças fora do lugar) | Conta peças que não estão no destino | Admissível, **fraca** |
| **h₂ (Manhattan)** ✓ | Soma das distâncias |||x| + ||y|| | Admissível, **dominante** |

Como `h₂(n) ≥ h₁(n)` sempre, **A\* com h₂ expande menos nós** que
com h₁ — é estritamente melhor.

---

## Como funciona o algoritmo

```
1. Coloca o estado inicial na fila com f = 0 + h(inicial).
2. Repete:
     a. Remove da fila o estado com menor f(n).
     b. Se for o objetivo, reconstrói e devolve o caminho.
     c. Marca como visitado.
     d. Para cada vizinho (1 movimento de distância):
         - Calcula novo g = g(atual) + 1
         - Se for um caminho melhor que o já conhecido para esse vizinho,
           registra o predecessor e adiciona à fila com f = g + h(vizinho).
3. Se a fila esvaziar sem achar o objetivo, retorna falha.
```

A reconstrução do caminho usa um dicionário `veio_de` que mapeia
cada estado ao seu predecessor — isso evita armazenar o caminho
completo em cada nó da fila.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas (apenas `heapq`, `random`, `sys`).

---

## Como rodar

```
cd C:\Projetos\kevin\Agente_Tabuleiro_Deslizante
python main.py
```

### Opções

| Comando | O que faz |
| ------- | --------- |
| `python main.py` | 30 embaralhamentos a partir do objetivo |
| `python main.py --passos 10` | Tabuleiro mais fácil |
| `python main.py --passos 50` | Tabuleiro mais difícil |
| `python main.py --passos 20 --semente 42` | Reproduzível |

> Embaralhar 30+ movimentos costuma gerar tabuleiros próximos do pior
> caso (28-31 movimentos pra resolver). Para testes rápidos, use 10-15.

### Por que embaralhar e não sortear aleatoriamente?
Cerca de **50% dos tabuleiros 3x3 aleatórios são INSOLÚVEIS** (paridade
da permutação). Para garantir solubilidade, partimos do objetivo e
aplicamos `N` movimentos aleatórios — o resultado **sempre tem
solução** (basta inverter a sequência).

---

## Como ler a saída

### 1) Cabeçalho com estado inicial e objetivo
```
Estado inicial:
   8  7  2
   5  3  6
   _  1  4

  h(inicial) = 16 (distancia de Manhattan)
```

### 2) Caminho passo a passo
Cada passo mostra o **movimento** aplicado (Cima/Baixo/Esquerda/Direita
do **espaço vazio**) e o tabuleiro resultante:

```
  Passo 1 (Direita):
     8  7  2
     5  3  6
     1  _  4
```

### 3) Estatísticas finais
```
Movimentos ate a solucao   : 20
Nos expandidos pelo A*     : 228
Tamanho maximo da fronteira: 135
Solucao OTIMA garantida    : sim (Manhattan e admissivel)
```

- **Movimentos**: comprimento do caminho ótimo encontrado.
- **Nós expandidos**: quantos estados foram retirados da fila.
- **Fronteira máxima**: maior tamanho atingido pela fila durante a busca.

---

## Anatomia do código

Tudo está em [main.py](main.py):

| Seção | Função(ões) |
| ----- | ----------- |
| Configuração | `OBJETIVO`, `POSICAO_OBJETIVO`, `MOVIMENTOS` |
| **Heurística h₂** | `manhattan` |
| Vizinhos | `encontrar_zero`, `vizinhos` |
| **Algoritmo A\*** | `a_estrela` |
| Estado inicial solúvel | `embaralhar` |
| Visualização | `imprimir_tabuleiro` |

### Pontos-chave do código

```python
# Heurística h₂ — Distância de Manhattan
soma = 0
for i in range(3):
    for j in range(3):
        valor = estado[i][j]
        if valor == 0:
            continue
        ti, tj = POSICAO_OBJETIVO[valor]
        soma += abs(i - ti) + abs(j - tj)
```

```python
# Núcleo do A*
heapq.heappush(fronteira, (manhattan(inicial), 0, contador, inicial))
while fronteira:
    f, g, _, estado = heapq.heappop(fronteira)
    if estado in visitados: continue
    visitados.add(estado)
    if estado == OBJETIVO:
        return reconstruir_caminho(...)
    for vizinho, movimento in vizinhos(estado):
        novo_g = g + 1
        if vizinho not in g_score or novo_g < g_score[vizinho]:
            g_score[vizinho] = novo_g
            heapq.heappush(fronteira, (novo_g + manhattan(vizinho), novo_g, c, vizinho))
```

> **Tiebreaker no heap**: o `contador` incremental evita que `heapq`
> tente comparar tuplas de estados (válido, mas mais lento e
> não-determinístico) quando `f` e `g` são iguais.

---

## Comparação com outras buscas

| Algoritmo | Ótimo? | Completo? | Custo típico (8-puzzle) |
| --------- | ------ | --------- | ----------------------- |
| **A\* + Manhattan** (este) | Sim | Sim | ~200-2.000 nós |
| **A\* + h₁** (peças fora do lugar) | Sim | Sim | ~500-10.000 nós |
| **BFS** | Sim (passos = custo) | Sim | ~10.000-100.000 nós |
| **DFS** | **Não** | **Não** (sem limite) | Pode não terminar |
| **Greedy** (só h, ignora g) | **Não** | Sim | Rápido mas sub-ótimo |

A* com Manhattan é a escolha **canônica** para 8-puzzle — combina
otimalidade com excelente desempenho.

---

## FAQ

**Por que o número de movimentos finais é exatamente igual ao `--passos`?**
Não é uma coincidência: o caminho ótimo de volta ao objetivo é, em
média, igual à profundidade do embaralhamento. Para alguns embaralhamentos
ele pode ser **menor** (se houver um atalho), mas nunca maior.

**Posso aumentar para um 15-puzzle (4x4)?**
Sim, mas seria preciso generalizar `OBJETIVO`, `manhattan` e `MOVIMENTOS`
para `N=4`. O 15-puzzle tem ~10¹³ estados — A* ainda funciona, mas pode
levar segundos com Manhattan e minutos com h₁.

**Por que a fronteira (135) é maior que os nós expandidos (228)?**
Engano comum: 135 é o **pico** instantâneo da fila, 228 é o **total**
retirado dela ao longo da busca. A fila atinge picos altos enquanto
muitos caminhos disputam atenção, mas a maioria deles nunca é expandida
(são descartados quando se descobre um caminho melhor).

**Por que "Manhattan e admissivel"?**
Porque cada peça precisa de **no mínimo** `|Δlinha| + |Δcoluna|`
movimentos para chegar ao destino — e cada movimento move só uma peça
em uma casa. Logo, h₂(n) é sempre ≤ ao custo real, ou seja, jamais
superestima.

**Por que evitar desfazer o último movimento no embaralhamento?**
Se um movimento aleatório for o inverso do anterior, ele "desembaralha".
Filtrar isso evita ciclos de comprimento 2 e gera tabuleiros mais
embaralhados de fato. É uma prática comum em geradores de quebra-cabeças.

**Como reproduzir o mesmo tabuleiro inicial?**
Use `--semente N` com qualquer inteiro:
```
python main.py --passos 20 --semente 42
```

**O agente garante a solução ótima?**
Sim. A* com heurística admissível **sempre** encontra a solução ótima
(menor número de movimentos). Manhattan é admissível, então o caminho
retornado é o **mais curto possível**.
