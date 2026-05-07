# Agente Wumpus — Agente Baseado em Conhecimento

Implementação em Python de um agente lógico que resolve o **Mundo de Wumpus**
(grade 4x4) usando **Lógica Proposicional** para inferir células seguras,
localizar o ouro e voltar em segurança para `[1,1]`.

---

## Índice

- [O que é o jogo](#o-que-é-o-jogo)
- [Requisitos](#requisitos)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como rodar](#como-rodar)
- [Como ler o que aparece na tela](#como-ler-o-que-aparece-na-tela)
- [Regras lógicas implementadas](#regras-lógicas-implementadas)
- [Exemplos prontos para testar](#exemplos-prontos-para-testar)
- [Resultados possíveis](#resultados-possíveis)
- [FAQ](#faq)

---

## O que é o jogo

O agente vive em uma caverna 4x4. Em algum lugar da caverna há:

- 1 **Wumpus** (criatura mortal)
- vários **Poços** (mortais)
- 1 pedaço de **Ouro**

A casa `[1,1]` (canto inferior esquerdo) é sempre **segura** e é onde o agente
começa. Em cada sala visitada o agente recebe três sensores:

| Sensor | Significado |
| ------ | ----------- |
| **Fedor** | Há um Wumpus em uma sala adjacente |
| **Brisa** | Há um Poço em uma sala adjacente |
| **Brilho** | O Ouro está nesta sala |

O agente possui **uma flecha** que pode disparar em linha reta para tentar
matar o Wumpus.

**Objetivo:** pegar o ouro e voltar para `[1,1]` vivo.

---

## Requisitos

- Python **3.8+**
- Nenhuma dependência externa (apenas a biblioteca padrão).

Para verificar a versão do Python:
```
python --version
```

---

## Estrutura do projeto

```
Agente_Wumpus/
├── mundo_wumpus.py        # Ambiente: grade, Wumpus, poços, ouro, sensores
├── base_conhecimento.py   # Base de Conhecimento + inferência lógica (R1..R4)
├── agente.py              # Loop do agente: percebe, infere, decide, age
├── main.py                # CLI para rodar simulações
└── README.md              # Este arquivo
```

---

## Como rodar

Abra o terminal dentro da pasta `Agente_Wumpus`:

```
cd C:\Projetos\kevin\Agente_Wumpus
```

### 1) Mundo aleatório com semente reproduzível
A mesma semente sempre gera o mesmo mundo:
```
python main.py --semente 3 --prob-poco 0.1
python main.py --semente 42
```

### 2) Mundo manual (você escolhe as posições)
Coordenadas: `x` = coluna (1..4), `y` = linha (1..4). `[1,1]` é o canto
inferior esquerdo.

```
python main.py --wumpus 1,3 --ouro 2,3 --pocos "3,1;3,3;4,4"
```

- `--wumpus x,y` — uma posição (não pode ser `1,1`)
- `--ouro x,y` — uma posição
- `--pocos "x1,y1;x2,y2;..."` — lista separada por `;` (use **aspas**)

### 3) Modo misto (fixa só o essencial e sorteia o resto)
```
python main.py --wumpus 2,3 --semente 5
python main.py --wumpus 4,2 --ouro 4,4 --semente 11
```

### Outras opções

| Flag | Descrição |
| ---- | --------- |
| `--prob-poco 0.15` | Probabilidade de cada célula virar poço (sorteio) |
| `--silencioso` | Esconde o passo a passo do raciocínio |
| `--help` | Mostra a ajuda completa |

---

## Como ler o que aparece na tela

A execução imprime três coisas:

### 1. O mapa real (apenas para você acompanhar)
```
  Mapa real do mundo (W=Wumpus, P=Poco, G=Ouro, A=Agente):
  4 |  P  |  .  |  G  |  .  |
  3 |  P  |  .  |  .  |  .  |
  2 |  .  |  W  |  .  |  .  |
  1 |  A  |  .  |  .  |  .  |
      1     2     3     4
```
O agente **não** vê esse mapa — ele só vê o que sente.

### 2. O raciocínio passo a passo
A cada passo o agente imprime:
- A sala atual e o que sentiu (`Percepcoes: fedor, brisa`)
- Cada conclusão lógica (`> R3b: fedor em [(1,2),(2,1)] -> Wumpus em (2,2).`)
- A ação escolhida (`Acao: mover de (1,2) para (2,2) (deduzido como Segura).`)

### 3. O mapa inferido pelo agente
Ao final, o mapa de acordo com o que **o agente sabe**:

| Símbolo | Significado |
| ------- | ----------- |
| `OK` | Provada **Segura** |
| `.V` | **Visitada** (logo, segura) |
| `W!` | **Wumpus confirmado** |
| `P!` | **Poço confirmado** |
| `??` | Desconhecida — não dá para provar |
| `A`  | Posição final do agente |

---

## Regras lógicas implementadas

Cada sala `(x,y)` tem átomos: `S(x,y)` (Fedor), `B(x,y)` (Brisa),
`W(x,y)` (Wumpus), `P(x,y)` (Poço), `OK(x,y)` (Segura).

| Regra | Descrição |
| ----- | --------- |
| **R1** | `¬S(c) ⇒ ¬W(adj)` — sem fedor numa sala, **nenhum** vizinho tem Wumpus |
| **R2** | `¬B(c) ⇒ ¬P(adj)` — sem brisa numa sala, **nenhum** vizinho tem Poço |
| **R3a** | Se há fedor numa sala e só **um** vizinho ainda é candidato, ele **é** o Wumpus |
| **R3b** | Como o Wumpus é único, ele está na **interseção** dos vizinhos suspeitos das salas com fedor |
| **R4** | Se há brisa numa sala e só **um** vizinho ainda é candidato, ali **há** um Poço |
| **R5** | `¬W(c) ∧ ¬P(c) ⇒ OK(c)` — provadamente sem Wumpus e sem Poço = Segura |

A função `deduzir_seguranca(sala)` em [base_conhecimento.py](base_conhecimento.py)
classifica cada sala como:

- `Segura`
- `Possivel Poco`
- `Possivel Wumpus`
- `Possivel Wumpus/Poco`
- `Perigo Confirmado (Wumpus)` ou `Perigo Confirmado (Poco)`

A inferência é aplicada **até atingir um ponto fixo** (nada mais a deduzir)
após cada percepção nova.

---

## Exemplos prontos para testar

| Comando | Demonstra |
| ------- | --------- |
| `python main.py --semente 3 --prob-poco 0.1` | Vitória completa (21 passos) com R3b deduzindo Wumpus por interseção |
| `python main.py --wumpus 1,3 --ouro 2,3 --pocos "3,1;3,3;4,4"` | R3a deduzindo Wumpus diretamente + R4 confirmando poço |
| `python main.py --semente 42` | Cenário onde o agente **se recusa a mover** (poço a 1 sala de distância sem prova de saída) |
| `python main.py --wumpus 4,4 --ouro 4,3 --pocos ""` | Mundo sem poços, foco no Wumpus |

---

## Resultados possíveis

Ao final, a simulação imprime um destes desfechos:

| Mensagem | O que aconteceu |
| -------- | --------------- |
| `VITORIA!` | Agente pegou o ouro e voltou a `[1,1]` |
| `DERROTA!` | O agente entrou numa sala com Wumpus ou Poço |
| `Agente parou sem encontrar caminho seguro` | Não há **prova lógica** de movimento seguro — o agente prefere ficar parado a arriscar |
| `Agente pegou o ouro mas nao conseguiu provar caminho seguro de volta` | Conseguiu o ouro, mas o caminho de volta não é mais provadamente seguro |

> O agente **nunca arrisca** uma sala sem prova lógica de segurança. Isso é
> intencional: ele é um agente de **raciocínio lógico**, não probabilístico.

---

## FAQ

**O agente vai sempre ganhar?**
Não. Em mundos onde a primeira jogada já é cercada por brisas/fedores sem
informação suficiente para concluir nada, o agente prefere **parar** a morrer.
Use `--prob-poco` mais baixo (ex: `0.1`) para mundos mais "jogáveis".

**Quando ele atira a flecha?**
Quando deduz a posição exata do Wumpus **e** não há nenhuma sala segura
inexplorada para avançar **e** o Wumpus está na linha de tiro. Na prática, se
existe um caminho seguro alternativo, o agente prefere desviar a gastar a
flecha.

**Posso mudar o tamanho da grade?**
A constante `MundoWumpus.TAMANHO = 4` está em [mundo_wumpus.py](mundo_wumpus.py).
Pode aumentar — toda a inferência funciona genericamente para `NxN`.

**Como uso isso na minha aula/trabalho?**
- A função `DEDUZIR_SEGURANCA` está em
  [base_conhecimento.py](base_conhecimento.py) com o nome
  `deduzir_seguranca(celula)`.
- O log do raciocínio (printado a cada passo) já cobre os exemplos clássicos
  dos slides de IA (R1 a R4).
- Para gerar saídas para um relatório, redirecione: `python main.py > log.txt`.
