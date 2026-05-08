# Agente 8 Rainhas — DFS com Formulação Incremental Reduzida

Resolução do **Problema das 8 Rainhas** em Python usando **Busca em
Profundidade (DFS)** com **Formulação Incremental Reduzida** —
posicionando uma rainha por coluna e podando estados inválidos antes
mesmo de gerá-los.

---

## Índice

- [O que é o problema](#o-que-é-o-problema)
- [Formulação Incremental Reduzida](#formulação-incremental-reduzida)
- [O algoritmo DFS com backtracking](#o-algoritmo-dfs-com-backtracking)
- [Requisitos](#requisitos)
- [Como rodar](#como-rodar)
- [Anatomia do código](#anatomia-do-código)
- [Como ler a saída](#como-ler-a-saída)
- [Comparação com os outros agentes](#comparação-com-os-outros-agentes)
- [FAQ](#faq)

---

## O que é o problema

Posicionar **8 rainhas** em um tabuleiro 8x8 de forma que **nenhuma
ataque outra**. Uma rainha ataca em linha, coluna e ambas as diagonais.

Existem 92 soluções válidas. Este agente encontra **uma diferente a cada
execução** — o DFS testa as linhas em **ordem aleatória**, então a árvore
de busca é explorada em ordem diferente em cada run.

---

## Formulação Incremental Reduzida

Existem três formas clássicas de formular este problema:

| Formulação | Descrição | Tamanho do espaço |
| ---------- | --------- | ----------------- |
| **Completa** | Começa com 8 rainhas e move-as | 8⁸ = 16.777.216 |
| **Incremental ingênua** | Adiciona rainhas, testa só no final | 8⁸ = 16.777.216 |
| **Incremental reduzida** | Adiciona rainhas, **poda no momento** | ~2.057 estados |

A versão **reduzida** é exatamente o que este agente faz:

> Ao adicionar a rainha da coluna `k`, **só consideramos linhas que não
> são atacadas pelas rainhas das colunas 0..k-1**. Estados inválidos
> nunca são gerados.

### Representação (estado)
Lista de N inteiros. `estado[i]` = linha (1..N) da rainha na coluna `i`,
ou `0` se a coluna ainda não foi preenchida.

Exemplo de estado parcial: `[1, 5, 8, 0, 0, 0, 0, 0]` (3 rainhas
colocadas, 5 colunas vazias).

### Teste de segurança
Como cada coluna tem **no máximo uma** rainha (pela representação),
**não há ataque por coluna**. Restam:
- **Mesma linha**: `estado[col_ant] == linha`
- **Mesma diagonal**: `|estado[col_ant] - linha| == |col_ant - coluna|`

---

## O algoritmo DFS com backtracking

```
dfs(estado, coluna):
    incrementa contador de nós
    se coluna == N:
        retorna SUCESSO   # 8 rainhas posicionadas
    embaralha as linhas 1..N            # ORDEM ALEATÓRIA
    para cada linha embaralhada:
        se eh_seguro(estado, coluna, linha):
            estado[coluna] = linha           # ação
            se dfs(estado, coluna + 1):      # aprofunda
                retorna SUCESSO
            estado[coluna] = 0               # backtracking
    retorna FALHA
```

A busca é em **profundidade** porque sempre tenta avançar para a próxima
coluna antes de explorar outra linha na coluna atual. Quando bate em um
beco sem saída (nenhuma linha segura na coluna corrente), faz
**backtracking** para a coluna anterior e tenta outra linha lá.

A **ordem aleatória das linhas** torna o algoritmo um *Randomized DFS*:
ainda completo (sempre acha solução), mas não-determinístico — cada
execução pode encontrar uma das 92 soluções existentes.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas.

---

## Como rodar

```
cd C:\Projetos\kevin\Agente_8_Rainhas_Form_Reduzida
python main.py
```

### Modo verboso (mostra a árvore de busca)
```
python main.py -v
```

### Reprodutibilidade (mesmo resultado em toda execução)
Use uma semente fixa para o gerador aleatório:
```
python main.py --semente 42
python main.py --semente 7 -v
```

Cada chamada recursiva imprime indentada conforme a profundidade,
permitindo visualizar a expansão da árvore de busca:
```
[no   1] coluna=0 estado=[_,_,_,_,_,_,_,_]
  [no   2] coluna=1 estado=[1,_,_,_,_,_,_,_]
    [no   3] coluna=2 estado=[1,3,_,_,_,_,_,_]
      [no   4] coluna=3 estado=[1,3,5,_,_,_,_,_]
        [no   5] coluna=4 estado=[1,3,5,7,_,_,_,_]
          ...
```

---

## Anatomia do código

Tudo está em [main.py](main.py), organizado em seções comentadas:

| Seção | Função(ões) |
| ----- | ----------- |
| Teste de segurança | `eh_seguro` |
| **DFS recursivo** | `dfs` |
| Visualização | `imprimir_tabuleiro` |
| Main / wrapper | `resolver` |

### Pontos-chave do código

```python
# Teste de segurança - só verifica colunas anteriores (REDUÇÃO)
for col_ant in range(coluna):
    linha_ant = estado[col_ant]
    if linha_ant == linha:                              # mesma linha
        return False
    if abs(linha_ant - linha) == abs(col_ant - coluna): # diagonal
        return False
```

```python
# DFS com backtracking + ordem aleatória de linhas
linhas = list(range(1, N + 1))
random.shuffle(linhas)               # cada execução, ordem diferente
for linha in linhas:
    if eh_seguro(estado, coluna, linha):
        estado[coluna] = linha          # ação
        if dfs(estado, coluna + 1, ...):
            return True
        estado[coluna] = 0              # backtracking
```

---

## Como ler a saída

### Modo padrão
```
============================================================
 8 Rainhas - Busca Incremental com Formulacao Reduzida
 Algoritmo: Busca em Profundidade (DFS)
============================================================

============================================================
 RESULTADO
============================================================
Solucao encontrada!
Estado solucao    : [4, 8, 1, 3, 6, 2, 7, 5]
Nos visitados     : 19
```

(Em outra execução você verá um cromossomo diferente — sempre uma das
92 soluções válidas: `[5, 1, 8, 4, 2, 7, 3, 6]`,
`[2, 4, 6, 8, 3, 1, 7, 5]`, etc.)

- **Estado solução**: `[col1=linha1, col2=linha2, ...]`
- **Nós visitados**: número de estados parciais explorados (cada
  chamada de `dfs`).
- **Tabuleiro**: linhas de 8 (topo) a 1 (base), colunas de 1 a 8.

### Por que o número de nós varia tanto entre execuções?
Porque a ordem em que as linhas são testadas é **aleatória**. Em uma
execução de sorte, os primeiros galhos da árvore já levam a uma
solução (~9 nós). Em outras execuções, o DFS pode bater em alguns
becos sem saída antes (30, 50, 100+ nós).

> Explorar **todas** as 92 soluções (DFS completo) visita **2.057** nós.
> Ainda assim, é ~8.000x menor que o espaço bruto de 8⁸.

---

## Comparação com os outros agentes

Este projeto resolve o mesmo problema das outras pastas com técnicas
**fundamentalmente diferentes**:

| Pasta | Técnica | Tipo | Tamanho do espaço | Métrica |
| ----- | ------- | ---- | ----------------- | ------- |
| **Form_Reduzida** (este) | DFS aleatorizado + Backtracking | Busca **sistemática** | 9-100 nós (varia) | Estados visitados |
| [Agente8Rainhas_Formulacao](../Agente8Rainhas_Formulacao/) | Hill-Climbing | Busca **local** | 56 vizinhos/iter | Iterações + reinícios |
| [Agente_8Rainhas](../Agente_8Rainhas/) | Algoritmo Genético | Busca **evolutiva** | População 100 | Gerações |

### Filosofia de cada um

- **DFS reduzido (este)**: explora a árvore de soluções válidas em
  **ordem aleatória**, com poda lógica. Garante encontrar **uma** das
  92 soluções, e a cada execução produz uma diferente.
- **Hill-Climbing**: parte de um estado completo aleatório e melhora
  localmente. **Pode ficar preso**, precisa de reinícios.
- **Genético**: evolui uma população. **Mais lento** mas mais robusto
  para problemas onde o espaço é mal-comportado.

Para 8 rainhas, **DFS é objetivamente o melhor** — encontra solução
com poucas centenas de operações. Hill-Climbing e GA são úteis para
demonstrar técnicas que escalam para problemas onde DFS é inviável.

---

## FAQ

**Como o agente gera soluções diferentes a cada execução?**
A cada chamada recursiva, as linhas a serem testadas são embaralhadas
com `random.shuffle()`. Como o DFS explora a árvore na ordem em que
os galhos são apresentados, embaralhar essa ordem faz com que cada
execução siga um caminho diferente — encontrando uma das 92 soluções
existentes. Para encontrar **todas** as 92, troque o `return True`
por `solucoes.append(estado.copy())` e remova o curto-circuito.

**Como reproduzir o mesmo resultado em duas execuções?**
Use a flag `--semente` com qualquer inteiro:
```
python main.py --semente 42
```
A mesma semente sempre gera a mesma sequência de embaralhamentos e,
portanto, a mesma solução.

**Posso usar para N rainhas?**
Sim, mude a constante `N = 8` no topo de [main.py](main.py). Funciona
para qualquer N ≥ 4. Para N = 20+, considere DFS iterativo (sem
recursão) ou aumente o limite de pilha com `sys.setrecursionlimit`.

**Por que "redução" e não "redução máxima"?**
Esta versão verifica linha + diagonais a cada inserção (custo O(k) por
teste). Versões ainda mais otimizadas usam **conjuntos** auxiliares
(`linhas_ocupadas`, `diag1_ocupadas`, `diag2_ocupadas`) para teste
O(1). Optei pela versão didática que deixa as três regras explícitas.

**E se eu quiser BFS em vez de DFS?**
Para 8 rainhas, BFS desperdiça memória (precisa armazenar a fronteira
inteira) e dá a mesma resposta. DFS é canônica para este problema.
Mude para BFS apenas se quiser a solução com **profundidade mínima**
(o que aqui não faz sentido, pois toda solução tem profundidade 8).

**O que conta como um "nó visitado"?**
Cada chamada recursiva de `dfs` — ou seja, cada **estado parcial** que
foi expandido. Estados podados pelo `eh_seguro` (que retornam `False`
sem chamar `dfs` novamente) **não** contam, porque nunca chegam a ser
"visitados" no sentido de explorados.
