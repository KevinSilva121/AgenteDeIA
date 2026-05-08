# Agente Aspirador Reativo Simples

Implementação em Python do **Agente de Reflexo Simples** (Aula 2 de IA),
baseado em uma **tabela de regras condição → ação**, no clássico
**Mundo do Aspirador** com 2 locais.

---

## Índice

- [O que é um Agente Reativo Simples](#o-que-é-um-agente-reativo-simples)
- [O Mundo do Aspirador](#o-mundo-do-aspirador)
- [Tabela de regras](#tabela-de-regras)
- [Requisitos](#requisitos)
- [Como rodar](#como-rodar)
- [Como ler a saída](#como-ler-a-saída)
- [A limitação clássica deste agente](#a-limitação-clássica-deste-agente)
- [Anatomia do código](#anatomia-do-código)
- [FAQ](#faq)

---

## O que é um Agente Reativo Simples

Um **Agente de Reflexo Simples** (também chamado de "Reativo Simples")
escolhe sua ação **com base APENAS na percepção atual**. Ele:

- **Não tem memória** das percepções passadas.
- **Não tem modelo** do ambiente (não sabe que existe um "outro lado").
- **Não tem objetivo** explícito — só reage a estímulos.

Sua "inteligência" está toda em uma **tabela de regras** do tipo:
```
SE  <condição da percepção>  ENTÃO  <ação>
```

É o tipo mais simples de agente racional, mas serve como base para
entender as limitações que motivam agentes mais sofisticados (baseados
em modelo, em objetivo, em utilidade).

---

## O Mundo do Aspirador

Ambiente clássico usado nos livros de IA (Russell & Norvig):

```
+-------+-------+
|       |       |
|   A   |   B   |
|       |       |
+-------+-------+
```

- **2 locais**: `A` (esquerda) e `B` (direita).
- Cada local pode estar `Limpo` ou `Sujo`.
- O agente está sempre em **um** dos dois locais.
- O agente percebe **somente** seu local atual e o status (limpo/sujo)
  daquele local — **não** vê o outro lado.

### Ações possíveis

| Ação | Efeito |
| ---- | ------ |
| `Aspirar` | Limpa o local atual |
| `Direita` | Move o agente para B |
| `Esquerda` | Move o agente para A |

---

## Tabela de regras

Implementação **estrita** da tabela dos slides da Aula 2:

| Percepção (local, status) | Ação |
| ------------------------- | ---- |
| `(qualquer, Sujo)` | `Aspirar` |
| `(A, Limpo)` | `Direita` |
| `(B, Limpo)` | `Esquerda` |

A regra "Aspirar quando sujo" tem **precedência** sobre as outras —
faz sentido, já que limpar é o objetivo do agente.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas.

---

## Como rodar

```
cd C:\Projetos\kevin\Agente_Aspirador_Reativo_Simples
python main.py
```

### Opções

| Comando | O que faz |
| ------- | --------- |
| `python main.py` | 10 passos, ambiente aleatório |
| `python main.py 20` | 20 passos |
| `python main.py 15 --semente 7` | 15 passos, ambiente reproduzível |

---

## Como ler a saída

Exemplo de execução:
```
============================================================
 Agente Aspirador Reativo Simples
============================================================
Estado inicial do ambiente: A=Sujo, B=Sujo
Posicao inicial do agente : B
------------------------------------------------------------
Passo  1 | Percepcao: [B, Sujo]  -> Acao: [Aspirar]  | Ambiente: A=Sujo, B=Sujo
Passo  2 | Percepcao: [B, Limpo] -> Acao: [Esquerda] | Ambiente: A=Sujo, B=Limpo
Passo  3 | Percepcao: [A, Sujo]  -> Acao: [Aspirar]  | Ambiente: A=Sujo, B=Limpo
Passo  4 | Percepcao: [A, Limpo] -> Acao: [Direita]  | Ambiente: A=Limpo, B=Limpo
Passo  5 | Percepcao: [B, Limpo] -> Acao: [Esquerda] | Ambiente: A=Limpo, B=Limpo
Passo  6 | Percepcao: [A, Limpo] -> Acao: [Direita]  | Ambiente: A=Limpo, B=Limpo
...
```

Cada linha tem três partes:

1. **Percepcao**: `[local, status]` que o agente leu.
2. **Acao**: o que ele decidiu fazer.
3. **Ambiente**: estado completo do mundo (mostrado pra você acompanhar
   — o agente **não** vê isso).

> A coluna `Ambiente` mostra o estado **antes** da ação ser aplicada.
> Por isso no Passo 1 vemos `Ambiente: A=Sujo, B=Sujo` mesmo após o
> Aspirar — a limpeza acontece em seguida.

---

## A limitação clássica deste agente

Repare nos passos 5 a 10 do exemplo acima: o ambiente já está **todo
limpo**, mas o agente continua **oscilando** entre A e B
indefinidamente.

**Isso não é um bug** — é a limitação fundamental dos agentes reativos
simples explicada na Aula 2:

> Como o agente decide com base **somente** na percepção atual
> `(local='A', status='Limpo')`, e a regra correspondente é
> `→ Direita`, ele **sempre** vai pra direita ao chegar em A limpo,
> mesmo já tendo limpado tudo antes. Sem memória, ele nunca "sabe"
> que terminou o trabalho.

### Como esse problema é resolvido nas próximas aulas?

| Aula | Tipo de agente | Como resolve |
| ---- | -------------- | ------------ |
| 2 | **Reativo Simples** (este) | Não resolve — oscila para sempre |
| 3 | **Baseado em Modelo** | Mantém estado interno: "já visitei A limpo e B limpo, posso parar" |
| 4 | **Baseado em Objetivo** | Tem o objetivo "tudo limpo" e raciocina sobre como atingí-lo |
| 5 | **Baseado em Utilidade** | Pondera custo de movimento × benefício de limpar |

---

## Anatomia do código

Tudo está em [main.py](main.py), com duas peças centrais:

### 1) A função do agente — a tabela de regras
```python
def agente_aspirador(percepcao):
    local, status = percepcao
    if status == 'Sujo':       # Regra 1
        return 'Aspirar'
    if local == 'A':           # Regra 2
        return 'Direita'
    if local == 'B':           # Regra 3
        return 'Esquerda'
```

### 2) O loop de simulação — percepção → ação → atuação
```python
for passo in range(1, passos + 1):
    # PERCEPCAO
    status = ambiente[local_atual]
    percepcao = (local_atual, status)

    # DECISAO (tabela de regras)
    acao = agente_aspirador(percepcao)

    # IMPRESSAO
    print(f"Passo {passo}: Percepcao: [{local_atual}, {status}] -> Acao: [{acao}]")

    # ATUACAO no ambiente
    if acao == 'Aspirar':
        ambiente[local_atual] = 'Limpo'
    elif acao == 'Direita':
        local_atual = 'B'
    elif acao == 'Esquerda':
        local_atual = 'A'
```

Note como o **agente** e o **ambiente** estão claramente separados:
- O agente só recebe a percepção e devolve a ação.
- O ambiente é quem aplica a ação e atualiza seu estado interno.

Essa separação é essencial em IA: o agente **não pode trapacear**
acessando o estado completo do ambiente.

---

## FAQ

**Por que o agente nunca para?**
Porque ele não tem memória. A função `agente_aspirador` é
**determinística sem estado**: a mesma percepção sempre produz a mesma
ação. Como `(A, Limpo)` ocorre repetidamente, ele sempre faz o mesmo.

**Posso fazer ele parar de mexer quando tudo está limpo?**
Sim, mas aí ele **deixa de ser reativo simples** — vira
**reativo baseado em modelo** (próxima aula). A solução envolve
adicionar variáveis como `ja_visitou_A` e `ja_visitou_B` e raciocinar
sobre elas.

**Como reproduzir o mesmo cenário?**
Use `--semente N` com qualquer inteiro:
```
python main.py 10 --semente 42
```
A mesma semente gera o mesmo estado inicial e a mesma posição do
agente.

**Posso adicionar mais locais (C, D, etc.)?**
Sim, mas a tabela de regras precisa ser estendida. Como o agente
reativo simples não tem mapa do ambiente, com mais locais a estratégia
"sempre vai pro próximo" se torna ambígua. É outra motivação para
agentes mais sofisticados.

**A precedência das regras importa?**
Sim. A regra `Sujo → Aspirar` tem que vir **antes** das regras de
movimento, senão o agente se moveria sem aspirar. No código isso é
garantido pela ordem dos `if`s.
