# Agente 8 Rainhas — Hill-Climbing (Formulação de Estados Completos)

Resolução do **Problema das 8 Rainhas** em Python usando **Busca Local:
Subida de Encosta** (Hill-Climbing) sobre uma **Formulação de Estados
Completos**, com Reinício Aleatório para tratamento de máximos locais.

---

## Índice

- [O que é o problema](#o-que-é-o-problema)
- [Formulação de Estados Completos](#formulação-de-estados-completos)
- [O algoritmo Hill-Climbing](#o-algoritmo-hill-climbing)
- [Requisitos](#requisitos)
- [Como rodar](#como-rodar)
- [Anatomia do código](#anatomia-do-código)
- [Como ler a saída](#como-ler-a-saída)
- [Comparação com o Algoritmo Genético](#comparação-com-o-algoritmo-genético)
- [FAQ](#faq)

---

## O que é o problema

Posicionar **8 rainhas** em um tabuleiro 8x8 de forma que **nenhuma ataque
outra**. Uma rainha ataca em linha, coluna e ambas as diagonais.

Existem 92 soluções válidas. Este agente encontra **uma** delas via
busca local.

---

## Formulação de Estados Completos

Diferente da **formulação incremental** (em que rainhas são adicionadas
uma a uma), aqui:

> O estado **sempre** contém as 8 rainhas no tabuleiro. A busca consiste
> em **mover** essas rainhas para reduzir os ataques.

### Representação (cromossomo / estado)
Lista de **8 inteiros** entre 1 e 8:
- O **índice** (0..7) representa a **coluna**.
- O **valor** representa a **linha** da rainha naquela coluna.

Exemplo: `[2, 6, 1, 7, 4, 8, 3, 5]`

> Como cada coluna tem exatamente uma rainha, **nunca há ataque por
> coluna** — a representação já elimina esse caso.

### Heurística `h(estado)`
Conta o número de **pares de rainhas que se atacam**:
- **Ataque direto**: mesma linha → `estado[i] == estado[j]`
- **Ataque indireto**: mesma diagonal → `|estado[i] - estado[j]| == |i - j|`

Objetivo: **minimizar `h` até zero**.

---

## O algoritmo Hill-Climbing

```
1. Gera estado inicial aleatório (8 rainhas em linhas sorteadas).
2. Repete:
     a. Gera todos os 56 vizinhos (mover cada rainha para outra linha
        em sua coluna: 8 colunas × 7 linhas restantes = 56).
     b. Pega o vizinho com menor h.
     c. Se h(vizinho) < h(atual)  →  move para o vizinho.
        Senão                     →  máximo local, reinicia.
3. Para quando h == 0 (solução encontrada).
```

### Por que precisa do Reinício Aleatório?
Hill-Climbing puro **trava em máximos locais** — estados onde nenhum
movimento melhora a heurística, mas que **não são** a solução. O
**Reinício Aleatório** abandona o estado travado e tenta novamente do
zero. Para 8 rainhas, em média são necessárias ~4 reinicializações.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas.

---

## Como rodar

```
cd C:\Projetos\kevin\Agente8Rainhas_Formulacao
python main.py
```

---

## Anatomia do código

Tudo está em [main.py](main.py), organizado em seções comentadas:

| Seção | Função(ões) |
| ----- | ----------- |
| Estado e Heurística | `criar_estado_aleatorio`, `contar_ataques` |
| Geração de vizinhos | `melhor_vizinho` |
| **Algoritmo Hill-Climbing** | `hill_climbing` |
| Visualização | `imprimir_tabuleiro` |

### Pontos-chave do código

```python
# Heurística: pares atacantes (linha + diagonal)
mesma_linha = estado[i] == estado[j]
mesma_diagonal = abs(estado[i] - estado[j]) == abs(i - j)
```

```python
# Movimento: avalia todos os 56 vizinhos
for col in range(N):
    for nova_linha in range(1, N + 1):
        if nova_linha == linha_atual:
            continue
        # ... avalia cada vizinho
```

```python
# Tratamento de máximo local
if novo_h >= h:
    # Nenhum vizinho melhora -> reinicia
    break
```

---

## Como ler a saída

### Durante a execução
Cada tentativa imprime o estado inicial, depois cada iteração mostra
o `h` do melhor vizinho:
```
=== Tentativa 1 ===
Estado inicial: [2, 4, 4, 7, 4, 8, 6, 5] | ataques h = 7
  Iter  1: melhor vizinho h = 4  -> [2, 4, 1, 7, 4, 8, 6, 5]
  Iter  2: melhor vizinho h = 2  -> [2, 4, 1, 7, 4, 8, 3, 5]
  Iter  3: melhor vizinho h = 0  -> [2, 6, 1, 7, 4, 8, 3, 5]
  Solucao encontrada! h = 0.
```

Se travar em máximo local:
```
  Maximo local atingido com h = 1 (nenhum vizinho melhora). Reiniciando.
```

### Resultado final
```
============================================================
 RESULTADO FINAL
============================================================
Estado solucao    : [2, 6, 1, 7, 4, 8, 3, 5]
Ataques (h)       : 0
Iteracoes totais  : 3
Reinicios feitos  : 0

Tabuleiro final:
    1 2 3 4 5 6 7 8
   +----------------+
 8 | . . . . . X . . |
 7 | . . . X . . . . |
 6 | . X . . . . . . |
 5 | . . . . . . . X |
 4 | . . . . X . . . |
 3 | . . . . . . X . |
 2 | X . . . . . . . |
 1 | . . X . . . . . |
   +----------------+
```

- Linhas numeradas de **8 (topo)** a **1 (base)**.
- Colunas numeradas de **1 a 8** da esquerda para a direita.
- `X` = rainha; `.` = casa vazia.

---

## Comparação com o Algoritmo Genético

Este projeto resolve o mesmo problema que [Agente_8Rainhas](../Agente_8Rainhas/),
mas com uma técnica **diferente**:

| Aspecto | Hill-Climbing (este) | Algoritmo Genético |
| ------- | -------------------- | ------------------ |
| Tipo de busca | **Busca local** | **Busca evolutiva populacional** |
| Quantidade de estados | 1 estado por vez | População (100 indivíduos) |
| Métrica | **Minimiza** ataques (objetivo: 0) | **Maximiza** pares não-atacantes (objetivo: 28) |
| Movimento | Determinístico — sempre o melhor vizinho | Estocástico — seleção/crossover/mutação |
| Saída de máximo local | Reinício aleatório | Mutação preserva diversidade |
| Tempo típico | < 0.1s (poucas iterações) | ~1s (centenas de gerações) |
| Convergência | Rápida, mas com reinícios | Mais lenta, mais robusta |

> Ambas as abordagens chegam à mesma família de soluções. A diferença é
> filosófica: Hill-Climbing **escala uma colina**, GA **evolui uma
> população**.

---

## FAQ

**Por que aparece "Tentativa 1" e às vezes "Tentativa 2, 3..."?**
Cada tentativa é uma execução do Hill-Climbing partindo de um estado
aleatório. Quando a tentativa trava em máximo local sem chegar a `h=0`,
o código **reinicia** (nova tentativa) com outro estado inicial.

**Quantas iterações são necessárias?**
Cada subida de encosta termina em **3 a 4 iterações** em média (cada
movimento reduz `h` em 1-3). O número total de **reinicializações**
varia: ~86% das tentativas travam em máximo local antes de chegar à
solução, então em média são ~4 reinicializações.

**Por que não aceita movimentos laterais (h igual)?**
A versão clássica de Hill-Climbing exige melhoria **estrita**. Aceitar
movimentos laterais (sideways moves) reduz o número de reinícios, mas
pode entrar em loop em platôs. Optei por seguir a definição estrita.
Para tentar a variante com sideways, mude `>=` para `>` em
[main.py:127](main.py#L127) e adicione um contador de movimentos
laterais consecutivos.

**Posso usar para N rainhas?**
Sim, mude a constante `N = 8` no topo de [main.py](main.py) para
qualquer N ≥ 4 (não há solução para N=2 e N=3). O algoritmo é genérico.

**E se eu quiser uma execução reproduzível?**
Adicione `random.seed(42)` no início de `main.py` (ou outro inteiro).
A mesma semente sempre gera a mesma sequência de tentativas.

**Por que nunca vejo "ataque por coluna" na heurística?**
Porque a representação `[col]→linha` garante que cada coluna tem
**exatamente uma** rainha — então é matematicamente impossível haver
duas rainhas na mesma coluna. Só restam ataques por linha e diagonal.
