# Agente Campo Minado — Lógica Proposicional

Agente em Python que joga **Campo Minado** usando **Lógica Proposicional**
(Aula 9 — Agentes Lógicos). Cada célula vira uma variável booleana, cada
número revelado é codificado em **cláusulas CNF** (Forma Normal Conjuntiva)
usando operadores **AND**, **OR** e **NOT**, e a Base de Conhecimento
usa **Propagação Unitária** para deduzir quais células são seguras ou minas.

---

## Índice

- [O que é o problema](#o-que-é-o-problema)
- [Modelagem lógica](#modelagem-lógica)
- [Codificação CNF](#codificação-cnf)
- [Classes de sentenças lógicas](#classes-de-sentenças-lógicas)
- [Regras de inferência](#regras-de-inferência)
- [A função `checar_seguranca`](#a-função-checar_seguranca)
- [Estratégia do agente](#estratégia-do-agente)
- [Requisitos](#requisitos)
- [Como rodar](#como-rodar)
- [Como ler a saída](#como-ler-a-saída)
- [Anatomia do código](#anatomia-do-código)
- [Comparação com o Wumpus](#comparação-com-o-wumpus)
- [FAQ](#faq)

---

## O que é o problema

Tabuleiro N×M com algumas minas escondidas. A cada jogada, o agente
revela uma célula:

- Se a célula tem mina → **derrota**.
- Se não tem → revela um **número** com a quantidade de minas nas até 8
  vizinhas (incluindo diagonais).

**Objetivo**: revelar todas as células seguras sem pisar em mina.

```
?  ?  ?  ?  ?  ?           1  1  1  .  .  1
?  ?  ?  ?  ?  ?           1  F  1  .  .  1
?  ?  ?  ?  ?  ?     →     3  3  2  .  .  1
?  ?  ?  ?  ?  ?           F  F  1  .  .  .
```

---

## Modelagem lógica

### Variáveis proposicionais
Para cada célula `(i, j)` do tabuleiro, criamos um átomo lógico:

```
M(i,j) = True   <=>  há mina em (i,j)
M(i,j) = False  <=>  célula segura  (NOT M(i,j))
```

### Restrições
Quando o ambiente revela `(i, j)` com número `N`, o agente adiciona à
Base de Conhecimento (BC) a restrição:

> "Exatamente `N` das células vizinhas de `(i,j)` são minas"

Antes de adicionar, o agente desconta as minas que **já conhece**
do número `N` e remove as células já provadas seguras do conjunto.

---

## Codificação CNF

A restrição "exatamente N de K vizinhos são minas" é codificada em
**cláusulas CNF** (conjunção de disjunções) usando os operadores `OR` e `NOT`:

### "No máximo N" (upper bound)
Para cada subconjunto de tamanho N+1, pelo menos um **não** é mina:

```
(NOT M(s₁) OR NOT M(s₂) OR ... OR NOT M(s_{N+1}))
```

> "Em qualquer grupo de N+1 vizinhos, pelo menos um NÃO é mina"

### "No mínimo N" (lower bound)
Para cada subconjunto de tamanho K−N+1, pelo menos um **é** mina:

```
(M(s₁) OR M(s₂) OR ... OR M(s_{K-N+1}))
```

> "Em qualquer grupo de K−N+1 vizinhos, pelo menos um É mina"

### Exemplos concretos

| Restrição | Cláusulas CNF geradas |
| --------- | --------------------- |
| Exatamente 0 de {A, B, C} | `(NOT A)`, `(NOT B)`, `(NOT C)` |
| Exatamente 3 de {A, B, C} | `(A)`, `(B)`, `(C)` |
| Exatamente 1 de {A, B, C} | `(NOT A OR NOT B)`, `(NOT A OR NOT C)`, `(NOT B OR NOT C)`, `(A OR B OR C)` |
| Exatamente 2 de {A, B, C, D} | `(NOT A OR NOT B OR NOT C)`, `(NOT A OR NOT B OR NOT D)`, `(NOT A OR NOT C OR NOT D)`, `(NOT B OR NOT C OR NOT D)`, `(A OR B OR C)`, `(A OR B OR D)`, `(A OR C OR D)`, `(B OR C OR D)` |

A função `gerar_clausulas_cnf()` faz essa codificação automaticamente
usando `itertools.combinations`.

---

## Classes de sentenças lógicas

O agente implementa uma hierarquia completa de sentenças proposicionais,
todas com o método `avaliar(modelo)` que é **chamado de verdade** durante
a inferência:

| Classe | Operador | Exemplo | Uso na inferência |
| ------ | -------- | ------- | ----------------- |
| `Simbolo` | Átomo | `M(1,2)` | Literal positivo em cláusulas |
| `Not` | NOT | `NOT M(1,2)` | Literal negativo em cláusulas |
| `Or` | OR | `(M(1,2) OR M(2,3))` | Cláusulas CNF — avaliadas na Propagação Unitária |
| `And` | AND | `(NOT M(1,2) AND NOT M(2,3))` | Conjunção de cláusulas |
| `Implies` | → | `(A IMPLIES B)` | Implicação lógica |
| `Bicondicional` | ↔ | `(A IFF B)` | Se e somente se |

### Como `avaliar()` é usado na inferência

Na **Propagação Unitária**, para cada cláusula `Or(L₁, L₂, ..., Lₙ)`:
1. Chama `Lᵢ.avaliar(modelo)` para cada literal (usa `Simbolo.avaliar` ou `Not.avaliar`)
2. Se todos retornam `False` exceto um `Lₖ` que retorna `None` → `Lₖ` é forçado `True`
3. Se algum retorna `True` → cláusula satisfeita, pula

### A classe `RestricaoContagem`

Representação compacta auxiliar usada para **Resolução por Subconjunto**:

```python
class RestricaoContagem:
    def __init__(self, cells, count):
        self.cells = set(cells)   # conjunto de células
        self.count = count        # quantas delas são minas
```

Cada restrição gera suas cláusulas CNF reais via `gerar_clausulas()`,
que são adicionadas à Base de Conhecimento.

---

## Regras de inferência

A função `_inferir()` aplica duas regras até atingir um **ponto fixo**:

### Passo 1 — Propagação Unitária (sobre cláusulas CNF)

Para cada cláusula `(L₁ OR L₂ OR ... OR Lₙ)` na BC:
- Avalia cada literal `Lᵢ` usando `avaliar(modelo)`
- Se **n−1 literais são False** e sobra **1 não-resolvido** → esse literal é **forçado True**

Isto é uma aplicação direta de **Modus Ponens** sobre cláusulas CNF.

```
Exemplo:
  Cláusula: (NOT M(1,2) OR NOT M(2,3))
  Modelo:   M(1,2) = True  →  NOT M(1,2) avalia como False
  ⇒ NOT M(2,3) é forçado True  →  M(2,3) = False [SEGURA]
```

Os casos triviais (count = 0 e count = |cells|) são resolvidos
automaticamente pela propagação, pois geram cláusulas unitárias:

```
count = 0 de {A, B, C}  →  cláusulas: (NOT A), (NOT B), (NOT C)
  ⇒ Propagação imediata: A=False, B=False, C=False  [todas SEGURAS]

count = 3 de {A, B, C}  →  cláusulas: (A), (B), (C)
  ⇒ Propagação imediata: A=True, B=True, C=True  [todas MINAS]
```

### Passo 2 — Resolução por Subconjunto (regra derivada)

Quando a propagação unitária não consegue derivar mais nada, o agente
aplica resolução sobre as restrições de contagem:

```
Se R₁.cells ⊂ R₂.cells  então:
  R₃ = (R₂.cells − R₁.cells, R₂.count − R₁.count)

Exemplo:
  R₁: {A, B}    = 1
  R₂: {A, B, C} = 1
  ⇒ R₃: {C} = 0  (C é segura!)
```

A nova restrição R₃ é **convertida em cláusulas CNF** e adicionada à BC,
alimentando novas rodadas de Propagação Unitária. Este ciclo continua
até o ponto fixo.

---

## A função `checar_seguranca`

Consulta diretamente o **modelo** da Base de Conhecimento:

```python
def checar_seguranca(self, celula):
    nome = f"M({celula[0]},{celula[1]})"
    if nome in self.bc.modelo:
        return 'mina' if self.bc.modelo[nome] else 'segura'
    return 'desconhecida'
```

### Princípio lógico
Equivale a perguntar `BC ⊨ ¬M(celula)` (segura) ou `BC ⊨ M(celula)` (mina).

O modelo é preenchido pela Propagação Unitária, que só atribui valores
quando eles são **logicamente forçados** pelas cláusulas CNF.

---

## Estratégia do agente

```
A cada rodada:
  1. Tenta jogada SEGURA: alguma célula com M(i,j)=False no modelo
     ainda não jogada?
  2. Se não houver → heurística de risco:
       - para cada célula desconhecida c:
           prob(c) = max(count/|cells|) entre as restrições que contêm c
       - escolhe a célula com MENOR probabilidade.
```

A heurística de risco é uma rede de segurança: o agente **só adivinha
quando a lógica não consegue provar nada**. Mesmo nas adivinhações,
ele escolhe a opção menos arriscada com base nas restrições conhecidas.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas (usa apenas `random`, `sys`, `itertools`).

---

## Como rodar

```
cd C:\Projetos\kevin\Agente_Campo_Minado
python main.py
```

### Opções

| Comando | O que faz |
| ------- | --------- |
| `python main.py` | 8×8 com 10 minas |
| `python main.py --semente 42 --minas 8` | Reproduzível, dificuldade média |
| `python main.py --altura 10 --largura 10 --minas 15` | Tabuleiro maior |
| `python main.py --silencioso` | Sem log das deduções |
| `python main.py --bc` | Mostra todas as cláusulas CNF ao final |

---

## Como ler a saída

### Símbolos do tabuleiro

| Símbolo | Significado |
| ------- | ----------- |
| `?` | Célula desconhecida |
| `.` | Revelada, sem minas vizinhas (count = 0) |
| `1`..`8` | Revelada, com aquela contagem de minas vizinhas |
| `F` | Célula que a AI **provou logicamente** ser mina |
| `*` | Mina **real** (só aparece após derrota, com revelação) |

### Logs de raciocínio durante o jogo

```
  [RESTRICAO] Celula (3,4) com contagem 2:
    ExatamenteN({M(2,3), M(2,4), M(2,5), M(3,3), M(3,5)}, 2)
    Codificada em 13 clausulas CNF:
      (NOT M(2,3) OR NOT M(2,4) OR NOT M(2,5))
      (NOT M(2,3) OR NOT M(2,4) OR NOT M(3,3))
      ...

  >> [Propagacao Unitaria]
     Clausula: (NOT M(1,2) OR NOT M(2,3))
     => M(2,3) = False [SEGURA]

  >> [Resolucao por Subconjunto]
     ExatamenteN({M(0,1), M(1,0)}, 1)
     SUBSET
     ExatamenteN({M(0,1), M(1,0), M(1,1)}, 1)
     => (NOT M(1,1))
     (+1 clausulas CNF)

  >> [Heuristica] (4,0) com prob. estimada 33% de ser mina
```

### Resultado final

- **VITORIA em N rodadas!** → todas as casas seguras reveladas.
- **DERROTA! Pisou em mina em (i, j).** → o agente teve que adivinhar
  e errou.

---

## Anatomia do código

Tudo está em [main.py](main.py):

| Classe / Função | Responsabilidade |
| --------------- | ---------------- |
| **`Sentenca`** | Classe base abstrata para sentenças lógicas |
| **`Simbolo`**, **`Not`**, **`And`**, **`Or`** | Operadores lógicos com `avaliar()` — usados na inferência real |
| **`Implies`**, **`Bicondicional`** | Operadores adicionais (implicação e bicondicional) |
| **`gerar_clausulas_cnf()`** | Codifica "exatamente N de K" em cláusulas CNF |
| **`BaseConhecimento`** | Armazena cláusulas CNF + modelo parcial + Propagação Unitária |
| **`RestricaoContagem`** | Representação compacta para Resolução por Subconjunto + geração CNF |
| **`MinesweeperAI`** | Agente: adiciona conhecimento, infere, decide jogada |
| **`Minesweeper`** | Ambiente do jogo (mantém minas e revelações) |
| `imprimir_tabuleiro` | Visualização |
| `jogar` | Loop principal do jogo |

### Fluxo principal

```python
ai.add_knowledge(celula, count)   # 1. Codifica em CNF, adiciona à BC, infere
                                  #    (Propagação Unitária + Resolução)
jogada = ai.jogada_segura()       # 2. Tenta jogada provada segura
if jogada is None:
    jogada = ai.jogada_arriscada() # 3. Heurística probabilística
```

### Fluxo detalhado da inferência

```
add_knowledge(cell, count):
  ├── mark_safe(cell)  →  modelo[M(i,j)] = False
  ├── Construir RestricaoContagem(vizinhos_desconhecidos, count_ajustado)
  ├── gerar_clausulas_cnf()  →  cláusulas Or/Not reais
  ├── Adicionar cláusulas à BaseConhecimento
  └── _inferir():
       └── while mudou:
            ├── Propagação Unitária:
            │    Para cada cláusula (L₁ OR ... OR Lₙ):
            │      avaliar cada Lᵢ no modelo
            │      se n-1 são False → forçar o restante
            └── Resolução por Subconjunto:
                 Se R₁ ⊂ R₂ → nova RestricaoContagem
                 → gerar cláusulas CNF → adicionar à BC
```

### Por que o loop `while mudou`?

A inferência é em **ponto fixo**: cada nova conclusão pode habilitar
outras. Por exemplo:
1. Propagação força `M(2,3) = False` [SEGURA]
2. Isso satisfaz/simplifica cláusulas que contêm `M(2,3)`
3. Restrições são simplificadas → Resolução gera nova restrição
4. Nova restrição gera cláusulas CNF unitárias → mais propagação
5. Repete até nada mais mudar

---

## Comparação com o Wumpus

Este agente compartilha princípios com [Agente_Wumpus](../Agente_Wumpus/):
ambos usam **lógica proposicional** para um agente em ambiente
parcialmente observável.

| Aspecto | Wumpus | Campo Minado (este) |
| ------- | ------ | ------------------- |
| Sensores | Fedor / Brisa / Brilho (booleanos) | Número de minas vizinhas (inteiro) |
| Forma da sentença | Cláusulas disjuntivas | Cláusulas CNF codificadas de "exatamente N de K" |
| Inferência principal | Resolução + interseção | **Propagação Unitária** sobre CNF + Resolução por Subconjunto |
| Operadores usados | AND, OR, NOT | AND, OR, NOT (avaliados via `avaliar()`) |
| Decisão segura | Provar `OK(célula)` | Consultar `modelo[M(i,j)]` |
| Quando arrisca? | Nunca (para se travado) | Quando lógica falha (heurística de menor risco) |

Ambos demonstram a tese da Aula 9: **agentes inteligentes podem ser
construídos como provadores de teoremas sobre o ambiente**.

---

## FAQ

**Por que o agente perde às vezes?**
Porque há momentos em Campo Minado onde **nenhuma jogada é provadamente
segura** — só restam adivinhações. Mesmo a melhor adivinhação pode dar
errado. Em tabuleiros 8×8 com 10 minas, ~40% das partidas são vencidas
mesmo com jogo perfeito.

**Por que o primeiro clique é sempre `(0,0)`?**
Convenção: o ambiente não coloca mina nessa célula, então o primeiro
clique é seguro. Sem isso, o agente perderia 10/64 ≈ 16% das partidas
no primeiro clique sem chance de raciocinar.

**A Propagação Unitária é completa?**
Para os casos triviais (count = 0 e count = |cells|), sim — gera
cláusulas unitárias que são resolvidas imediatamente. Para casos
intermediários, a Propagação Unitária sozinha pode não ser suficiente,
por isso usamos a **Resolução por Subconjunto** como regra complementar.
A resolução gera novas cláusulas CNF que alimentam mais propagação.

**O que é Propagação Unitária?**
É a regra de inferência principal: se uma cláusula `(L₁ OR L₂ OR ... OR Lₙ)`
tem todos os literais avaliados como `False` exceto um, esse literal é
**forçado** `True`. É uma aplicação direta de Modus Ponens. O método
`avaliar()` de cada operador (`Or`, `Not`, `Simbolo`) é chamado de
verdade a cada passo da inferência.

**O que é "estratégia de risco"?**
Quando a BC não consegue provar nada, o agente calcula para cada
célula desconhecida a probabilidade de ser mina baseada nas restrições
que a contêm. Escolhe a célula com **menor** probabilidade. É uma
heurística — não garante segurança, mas evita as piores escolhas.

**Quantas cláusulas CNF são geradas?**
Depende da restrição. "Exatamente N de K" gera `C(K, N+1) + C(K, K-N+1)`
cláusulas. Para casos comuns (K=3-5, N=1-2), são 4-15 cláusulas.
Em um jogo 8×8 típico, a BC acumula ~100-200 cláusulas no total.

**Como adicionar mais regras de inferência?**
Acrescente passos no `_inferir()`. Por exemplo:
- Regra do "número total de minas restantes" (sabe quantas minas faltam).
- Regra de "fronteira" (analisa só as células na borda do conhecido).
- Resolução binária entre pares de cláusulas CNF.
