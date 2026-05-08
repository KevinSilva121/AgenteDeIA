# Agente Aspirador Baseado em Tabela

Implementação em Python do **Agente Baseado em Tabela** (Aula 2 de IA),
no clássico **Mundo do Aspirador** com 2 locais. Inclui demonstração
explícita do **crescimento exponencial** da tabela citado nos slides.

---

## Índice

- [O que é um Agente Baseado em Tabela](#o-que-é-um-agente-baseado-em-tabela)
- [O Mundo do Aspirador](#o-mundo-do-aspirador)
- [Estrutura da tabela](#estrutura-da-tabela)
- [O problema do crescimento exponencial](#o-problema-do-crescimento-exponencial)
- [Requisitos](#requisitos)
- [Como rodar](#como-rodar)
- [Como ler a saída](#como-ler-a-saída)
- [Anatomia do código](#anatomia-do-código)
- [Comparação com o Reativo Simples](#comparação-com-o-reativo-simples)
- [FAQ](#faq)

---

## O que é um Agente Baseado em Tabela

É a forma **mais primitiva** de agente racional possível. Ele não tem
regras nem raciocínio: apenas uma **tabela de consulta gigante** onde
cada **sequência de percepções** mapeia para uma **ação**.

### Pseudocódigo (AIMA, capítulo 2)
```
function TABLE-DRIVEN-AGENT(percept) returns an action
    persistent: percepts, a sequence, initially empty
                table, a table of actions, indexed by percept sequences
    append percept to the end of percepts
    action <- LOOKUP(percepts, table)
    return action
```

### Características

- **Tem memória completa**: armazena todo o histórico de percepções.
- **Não tem inteligência embutida**: a tabela é fixa, especificada pelo
  projetista a priori.
- **Determinístico**: a mesma sequência de percepções sempre dá a mesma
  ação.
- **Inviável na prática**: a tabela cresce exponencialmente (veja abaixo).

---

## O Mundo do Aspirador

Mesmo cenário do agente reflexo simples:

```
+-------+-------+
|       |       |
|   A   |   B   |
|       |       |
+-------+-------+
```

- **2 locais**: `A` (esquerda) e `B` (direita).
- Cada local pode estar `Limpo` ou `Sujo`.
- **4 percepções possíveis** por passo:
  `(A,Limpo)`, `(A,Sujo)`, `(B,Limpo)`, `(B,Sujo)`.

### Ações possíveis

| Ação | Efeito |
| ---- | ------ |
| `Aspirar` | Limpa o local atual |
| `Direita` | Move o agente para B |
| `Esquerda` | Move o agente para A |

---

## Estrutura da tabela

A tabela é um **dicionário** Python onde:

- **Chave** = tupla com o histórico **inteiro** de percepções até agora.
- **Valor** = ação a ser tomada.

### Fragmento manual (escrito à mão)
```python
TABELA_MANUAL = {
    (('A', 'Sujo'),):                      'Aspirar',
    (('A', 'Limpo'),):                     'Direita',
    (('B', 'Sujo'),):                      'Aspirar',
    (('B', 'Limpo'),):                     'Esquerda',

    (('A', 'Limpo'), ('B', 'Sujo')):       'Aspirar',
    (('A', 'Limpo'), ('B', 'Limpo')):      'Esquerda',
    (('B', 'Limpo'), ('A', 'Sujo')):       'Aspirar',
    (('B', 'Limpo'), ('A', 'Limpo')):      'Direita',
    # ... e mais ~1,4 milhões de entradas
}
```

> Note como cada chave **inclui o histórico completo** — não apenas a
> percepção atual. Essa é a diferença fundamental para o Agente Reflexo
> Simples.

---

## O problema do crescimento exponencial

Com `P` percepções possíveis e `T` passos, a tabela precisa cobrir:

$$
\sum_{n=1}^{T} P^n = \frac{P^{T+1} - P}{P - 1}
$$

No mundo do aspirador (`P = 4`):

| Passos T | Entradas para esse T | Total acumulado |
| -------- | -------------------- | --------------- |
| 1 | 4 | 4 |
| 2 | 16 | 20 |
| 3 | 64 | 84 |
| 4 | 256 | 340 |
| 5 | 1.024 | 1.364 |
| 6 | 4.096 | 5.460 |
| 7 | 16.384 | 21.844 |
| 8 | 65.536 | 87.380 |
| 9 | 262.144 | 349.524 |
| **10** | **1.048.576** | **1.398.100** |

> **Para apenas 10 passos a tabela já tem ~1,4 milhões de entradas.**
> Para 20 passos: 1,5 trilhões. Para 100 passos: número astronômico.
>
> Especificar essas entradas **manualmente** é impossível — e essa é
> exatamente a motivação para os agentes baseados em **regras**
> (próximas aulas).

### Por que o código consegue rodar 10 passos então?
Porque ele **gera a tabela programaticamente** (com uma regrinha
implícita: aspirar se sujo, alternar se limpo). Em um Agente Baseado
em Tabela "puro", cada entrada teria que ser hard-coded — o que é
inviável.

A geração programática **aqui é só pra demonstrar o conceito** —
contradiz o espírito da abordagem original.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas.

---

## Como rodar

```
cd C:\Projetos\kevin\Agente_Aspirador_Tabela
python main.py
```

### Opções

| Comando | O que faz |
| ------- | --------- |
| `python main.py` | 10 passos, ambiente aleatório |
| `python main.py 20` | 20 passos (gera ~366 bi entradas — vai travar) |
| `python main.py 5 --semente 7` | 5 passos, ambiente reproduzível |

> Não tente `python main.py 15` ou mais — a geração da tabela
> programática vai consumir gigabytes de RAM. Mantenha em até 12.

---

## Como ler a saída

A execução tem 4 partes:

### 1) Tabela do crescimento exponencial
Mostra quantas entradas seriam necessárias para cada `T`:
```
Passos (T) | Entradas para esse T |   Total acumulado
        10 |             1,048,576 |         1,398,100  <-- impossivel manualmente
```

### 2) Fragmento manual da tabela
Mostra 8 entradas escritas à mão para você ver a estrutura
`(sequência) → ação`.

### 3) Geração da tabela completa
```
Gerando tabela completa para suportar ate 10 passos...
Tabela gerada com 1,398,100 entradas.
```

### 4) Simulação
```
Passo  1 | Percepcao: [B, Limpo] -> Acao: [Esquerda]  | Ambiente: ...  | Histor.: 1
Passo  2 | Percepcao: [A, Sujo]  -> Acao: [Aspirar]   | Ambiente: ...  | Histor.: 2
...
```

A coluna **`Histor.: N`** mostra o tamanho do histórico de percepções
crescendo. É essa lista inteira (não só o último item) que vira a
chave consultada na tabela.

---

## Anatomia do código

Tudo está em [main.py](main.py):

| Seção | Função(ões) |
| ----- | ----------- |
| Percepções possíveis | constantes `LOCAIS`, `ESTADOS` |
| Tabela manual | `TABELA_MANUAL` (didático) |
| Geração da tabela | `construir_tabela_completa` |
| **Agente** | `AgenteBaseadoTabela` (classe) |
| Demonstração exponencial | `demonstrar_crescimento_exponencial` |
| Ambiente / simulação | `simular` |

### Pontos-chave do código

```python
# Classe do agente: histórico interno + lookup na tabela
class AgenteBaseadoTabela:
    def __init__(self, tabela):
        self.percepts = []     # histórico (vazio inicialmente)
        self.tabela = tabela

    def __call__(self, percepcao):
        self.percepts.append(percepcao)        # 1) anexa
        chave = tuple(self.percepts)           # 2) usa histórico inteiro
        return self.tabela.get(chave)          # 3) consulta tabela
```

```python
# Geração programática (apenas para a simulação rodar)
for n in range(1, max_passos + 1):
    for sequencia in product(PERCEPCOES_POSSIVEIS, repeat=n):
        # ... preenche cada entrada
```

---

## Comparação com o Reativo Simples

Este agente e o [Agente_Aspirador_Reativo_Simples](../Agente_Aspirador_Reativo_Simples/)
resolvem o **mesmo problema** com filosofias opostas:

| Aspecto | Reflexo Simples | Baseado em Tabela (este) |
| ------- | --------------- | ------------------------ |
| Tamanho do "código" | 3 regras | 1,4 milhões de entradas (T=10) |
| Memória do agente | Nenhuma | Histórico completo |
| Decisão usa | Só a percepção atual | Toda a sequência de percepções |
| Comportamento | Idêntico (em prática) | Idêntico (em prática) |
| Escalabilidade | Excelente | **Catastrófica** |
| Implementação real | Simples e viável | Inviável |

> **Moral da história**: para problemas determinísticos como o
> aspirador, ambos chegam ao mesmo resultado, mas a tabela é
> **infinitamente mais cara**. As regras compactam a mesma decisão
> em poucas linhas.

---

## FAQ

**Por que a tabela é "exponencial" e não "linear"?**
Porque o número de **sequências distintas** de comprimento `T` é `P^T`
(escolhas independentes em cada posição). Mesmo com poucas percepções
por passo, a combinatória explode rápido.

**E se eu só guardar a percepção mais recente?**
Aí você acabou de inventar o **Agente Reflexo Simples** — a tabela
deixa de ser de sequências e vira de percepções únicas. O custo cai de
`P^T` para `P`. (Mas você perde a capacidade teórica de diferenciar
por histórico.)

**A tabela manual cobre o suficiente para rodar a simulação?**
Não — só cobre as 4 sequências de tamanho 1 e 4 sequências de tamanho
2. Por isso o código gera o resto programaticamente (com a
"trapaça" de uma regra implícita).

**Por que aparece `Histor.: N` aumentando?**
Para mostrar visualmente que a **chave consultada na tabela cresce a
cada passo**. No passo 10, o agente está procurando uma tupla de 10
percepções no dicionário — e essa tupla é única entre as 1,4 milhões
possíveis.

**E se a sequência atual não estiver na tabela?**
A função retorna `None` e o agente trava. O código detecta isso e
imprime "Acao: [INDEFINIDA - sequencia nao existe na tabela]". Em um
Agente Baseado em Tabela "verdadeiro", você teria que prever **todas**
as sequências possíveis de antemão.

**Por que dizem que esse agente "não tem inteligência"?**
Porque toda a "inteligência" foi colocada **na tabela** pelo
projetista, não no agente. O agente em si é um simples lookup. Já um
agente baseado em regras tem a inteligência **explicitada** no código.
