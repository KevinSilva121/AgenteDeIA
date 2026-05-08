# Agente Campo Minado — Lógica Proposicional

Agente em Python que joga **Campo Minado** usando **Lógica Proposicional**
(Aula 9 — Agentes Lógicos). Cada célula vira uma variável booleana, cada
número revelado vira uma restrição numérica, e a Base de Conhecimento
deduz quais células são seguras ou minas.

---

## Índice

- [O que é o problema](#o-que-é-o-problema)
- [Modelagem lógica](#modelagem-lógica)
- [A classe `Sentence`](#a-classe-sentence)
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
M_{i,j} = True   <=>  há mina em (i,j)
M_{i,j} = False  <=>  célula segura
```

### Sentenças (restrições)
Quando o ambiente revela `(i, j)` com número `N`, o agente adiciona à
Base de Conhecimento (BC) a sentença:

> "Exatamente `N` das células vizinhas de `(i,j)` são minas"

Em forma compacta:

```
{C₁, C₂, ..., Cₖ} = N    onde Cᵢ são as vizinhas ainda desconhecidas
```

Antes de adicionar, o agente já desconta as minas que **já conhece**
do número `N` e remove as células já provadas seguras do conjunto.

---

## A classe `Sentence`

```python
class Sentence:
    def __init__(self, cells, count):
        self.cells = set(cells)   # conjunto de células
        self.count = count        # quantas delas são minas
```

Operações principais:

| Método | O que faz |
| ------ | --------- |
| `known_mines()` | Se `count == len(cells)` → todas são minas |
| `known_safes()` | Se `count == 0` → todas são seguras |
| `mark_mine(c)` | Remove `c` do conjunto e diminui `count` |
| `mark_safe(c)` | Remove `c` do conjunto (não mexe em `count`) |

> A representação `(conjunto, contagem)` é equivalente a uma fórmula
> proposicional do tipo "exatamente `count` literais positivos entre
> esses". É a forma mais compacta possível — uma única sentença encapsula
> o que seriam dezenas de cláusulas em CNF puro.

---

## Regras de inferência

A função `_inferir()` aplica três regras até atingir um **ponto fixo**:

### R1 — todas são minas
```
{a, b, c} = 3   ⇒   a, b, c são todas MINAS
```

### R2 — todas são seguras
```
{a, b, c} = 0   ⇒   a, b, c são todas SEGURAS
```

### R3 — regra de subconjunto (a mais poderosa)
```
Se S₁ ⊂ S₂  então  (S₂ - S₁) = (count₂ - count₁)

Exemplo:
  {a, b}    = 1
  {a, b, c} = 1
  ⇒  {c} = 0  (c é segura!)
```

Esta regra permite o agente "ver através" de configurações que à primeira
vista parecem indeterminadas, mas têm dedução lógica oculta.

---

## A função `checar_seguranca`

Determina o status lógico de uma célula consultando a BC:

```python
def checar_seguranca(self, celula):
    if celula in self.safes:    return 'segura'
    if celula in self.mines:    return 'mina'
    for sent in self.knowledge:
        if celula in sent.cells:
            if sent.count == 0:                     return 'segura'
            if sent.count == len(sent.cells):       return 'mina'
    return 'desconhecida'
```

### Princípio lógico
Equivale a perguntar `BC ⊨ ¬M(celula)` (segura) ou `BC ⊨ M(celula)` (mina).

A versão "negar a hipótese e checar contradição" mencionada na Aula 9
é equivalente: assumir que `(celula)` é segura e ver se isso entra em
contradição com alguma sentença é o mesmo que verificar se a sentença
já força a célula a ser mina.

---

## Estratégia do agente

```
A cada rodada:
  1. Tenta jogada SEGURA: alguma célula em `safes` ainda não jogada?
  2. Se não houver → heurística de risco:
       - para cada célula desconhecida c:
           prob(c) = max(count/|cells|) entre as sentenças que contêm c
       - escolhe a célula com MENOR probabilidade.
```

A heurística de risco é uma rede de segurança: o agente **só adivinha
quando a lógica não consegue provar nada**. Mesmo nas adivinhações,
ele escolhe a opção menos arriscada com base nas restrições conhecidas.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas.

---

## Como rodar

```
cd C:\Projetos\kevin\Agente_Campo_Minado
python main.py
```

### Opções

| Comando | O que faz |
| ------- | --------- |
| `python main.py` | 8x8 com 10 minas |
| `python main.py --semente 7 --minas 8` | Reproduzível, dificuldade média |
| `python main.py --altura 10 --largura 10 --minas 15` | Tabuleiro maior |
| `python main.py --silencioso` | Sem log das deduções |

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
Nova sentenca pela regra de (3, 4): [(2, 3), (2, 4), (2, 5), (3, 3), (3, 5), (4, 3), (4, 4), (4, 5)] = 2
  >> Inferido: (2, 3) e SEGURA (sentenca com count == 0)
  >> Subset: ({(0, 1), (1, 0), (1, 1)} = 1) - ({(1, 1)} = 1) => {(0, 1), (1, 0)} = 0
  >> Inferido: (3, 0) e MINA (sentenca com count == |cells|)
  >> Heuristica: (4, 0) tem prob. estimada 33% de ser mina (menor entre desconhecidas).
```

### Resultado final

- **VITORIA em N rodadas!** → todas as casas seguras reveladas.
- **DERROTA! Pisou em mina em (i, j).** → o agente teve que adivinhar
  e errou (ou perdeu logo no primeiro clique sem informação).

---

## Anatomia do código

Tudo está em [main.py](main.py):

| Classe / Função | Responsabilidade |
| --------------- | ---------------- |
| **`Sentence`** | Restrição lógica `{células} = count` |
| **`MinesweeperAI`** | Base de conhecimento + inferência + decisão |
| **`Minesweeper`** | Ambiente do jogo (mantém minas e revelações) |
| `imprimir_tabuleiro` | Visualização |
| `jogar` | Loop principal do jogo |

### Fluxo principal

```python
ai.add_knowledge(celula, count)   # 1. Adiciona sentença e infere
                                  #    (chama mark_safe, _inferir)
jogada = ai.jogada_segura()       # 2. Tenta jogada provada segura
if jogada is None:
    jogada = ai.jogada_arriscada() # 3. Heurística probabilística
```

### Por que dois loops aninhados em `_inferir()`?

A inferência é em **ponto fixo**: cada nova conclusão pode habilitar
outras. Por exemplo:
1. Sentença `{a,b}=2` ⇒ R1 → `a` e `b` são minas.
2. `mark_mine(a)` propaga em todas as sentenças.
3. Outra sentença `{a,c,d}=1` vira `{c,d}=0` ⇒ R2 → `c, d` seguras.
4. Isso pode habilitar mais R3 (subset), e assim por diante.

O `while mudou` garante que ele só termina quando nada mais pode ser
deduzido.

---

## Comparação com o Wumpus

Este agente compartilha princípios com [Agente_Wumpus](../Agente_Wumpus/):
ambos usam **lógica proposicional** para um agente em ambiente
parcialmente observável.

| Aspecto | Wumpus | Campo Minado (este) |
| ------- | ------ | ------------------- |
| Sensores | Fedor / Brisa / Brilho (booleanos) | Número de minas vizinhas (inteiro) |
| Forma da sentença | Cláusulas disjuntivas | `{cells} = N` (restrição numérica) |
| Inferência principal | Resolução + interseção | Subconjunto + contagem |
| Decisão segura | Provar `OK(célula)` | `cell ∈ safes` |
| Quando arrisca? | Nunca (para se travado) | Quando lógica falha |

Ambos demonstram a tese da Aula 9: **agentes inteligentes podem ser
construídos como provadores de teoremas sobre o ambiente**.

---

## FAQ

**Por que o agente perde às vezes?**
Porque há momentos em Campo Minado onde **nenhuma jogada é provadamente
segura** — só restam adivinhações. Mesmo a melhor adivinhação pode dar
errado. Em tabuleiros 8x8 com 10 minas, ~40% das partidas são vencidas
mesmo com jogo perfeito.

**Por que o primeiro clique é sempre `(0,0)`?**
Convenção: o ambiente não coloca mina nessa célula, então o primeiro
clique é seguro. Sem isso, o agente perderia 10/64 ≈ 16% das partidas
no primeiro clique sem chance de raciocinar.

**A regra de subconjunto é completa?**
Para a maioria dos casos práticos, sim. Mas existe a chamada **dedução
global** (envolvendo múltiplas sentenças simultaneamente) que pode
provar mais do que o subset rule sozinho. Para resolver Campo Minado
de forma 100% completa, seria preciso usar **SAT solving** ou modelar
como problema NP-completo.

**O que é "estratégia de risco"?**
Quando a BC não consegue provar nada, o agente calcula para cada
célula desconhecida a probabilidade de ser mina baseada nas sentenças
que a contêm. Escolhe a célula com **menor** probabilidade. É uma
heurística — não garante segurança, mas evita as piores escolhas.

**Por que `count` pode ficar negativo?**
Não pode (e isso seria um bug). Se você ver isso, significa que a BC
está inconsistente — provavelmente um erro na contagem do ambiente.
A implementação atual evita isso descontando minas conhecidas **antes**
de criar a sentença.

**Como adicionar mais regras de inferência?**
Acrescente métodos no `_inferir()` que percorram a `self.knowledge`
e gerem novas conclusões. Por exemplo:
- Regra do "número total de minas restantes" (sabe quantas minas faltam).
- Regra de "fronteira" (analisa só as células na borda do conhecido).
