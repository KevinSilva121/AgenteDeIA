# Agente 8 Rainhas — Algoritmo Genético

Resolução do clássico **Problema das 8 Rainhas** em Python usando um
**Algoritmo Genético (AG)** com Seleção por Roleta, Crossover de um
ponto e Mutação aleatória.

---

## Índice

- [O que é o problema](#o-que-é-o-problema)
- [Como o AG resolve](#como-o-ag-resolve)
- [Requisitos](#requisitos)
- [Como rodar](#como-rodar)
- [Anatomia do código](#anatomia-do-código)
- [Como ler a saída](#como-ler-a-saída)
- [Parâmetros que você pode ajustar](#parâmetros-que-você-pode-ajustar)
- [FAQ](#faq)

---

## O que é o problema

Posicionar **8 rainhas** em um tabuleiro 8x8 de forma que **nenhuma ataque
outra**. Uma rainha ataca em linha, coluna e ambas as diagonais.

Existem 92 soluções distintas (12 essencialmente diferentes, considerando
simetrias).

---

## Como o AG resolve

### Representação (cromossomo)
Lista de **8 inteiros** entre 1 e 8:
- O **índice** (0..7) representa a **coluna** do tabuleiro.
- O **valor** representa a **linha** onde a rainha está naquela coluna.

Exemplo: `[2, 4, 7, 4, 8, 5, 5, 2]` → rainha da coluna 1 na linha 2,
da coluna 2 na linha 4, etc.

> Como cada coluna tem exatamente uma rainha (uma posição na lista),
> **nunca há ataque por coluna** — a representação já elimina esse caso.

### Função de aptidão (fitness)
Conta o número de **pares de rainhas que NÃO se atacam**.

- Total de pares possíveis: `C(8,2) = 28`.
- **Fitness máximo = 28** → solução ótima (nenhum ataque).

### Operadores genéticos

| Operador | Implementação |
| -------- | ------------- |
| **Seleção** | Método da Roleta — probabilidade proporcional ao fitness |
| **Crossover** | Um ponto de corte aleatório entre genes 1 e 7 |
| **Mutação** | Para cada gene, com probabilidade `taxa`, troca por valor aleatório em [1,8] |

### Loop evolutivo
1. Cria população inicial aleatória.
2. Avalia o fitness de cada indivíduo.
3. A cada **100 gerações**, imprime o melhor fitness atual.
4. Para quando algum indivíduo atinge **fitness = 28**.
5. Caso contrário, gera nova população aplicando **Seleção → Crossover → Mutação**.

---

## Requisitos

- **Python 3.8+**
- Sem dependências externas.

---

## Como rodar

```
cd C:\Projetos\kevin\Agente_8Rainhas
python main.py
```

---

## Anatomia do código

Tudo está em [main.py](main.py), organizado por seções marcadas com
cabeçalhos comentados:

| Seção | Função(ões) |
| ----- | ----------- |
| Representação e População | `criar_individuo`, `criar_populacao` |
| Função de Aptidão | `fitness` |
| **Operador 1: Seleção** | `selecao_roleta` |
| **Operador 2: Crossover** | `crossover_um_ponto` |
| **Operador 3: Mutação** | `mutacao` |
| Loop principal | `algoritmo_genetico` |
| Visualização | `imprimir_tabuleiro` |

Dentro de `algoritmo_genetico`, as três etapas estão **explicitamente comentadas**:

```python
# ---- ETAPA 1: SELECAO ----
pai1 = selecao_roleta(populacao, aptidoes)
pai2 = selecao_roleta(populacao, aptidoes)

# ---- ETAPA 2: CROSSOVER ----
filho1, filho2 = crossover_um_ponto(pai1, pai2)

# ---- ETAPA 3: MUTACAO ----
filho1 = mutacao(filho1, taxa_mutacao)
filho2 = mutacao(filho2, taxa_mutacao)
```

---

## Como ler a saída

### Durante a execução
A cada 100 gerações é impressa uma linha como:
```
Geracao   400 | melhor fitness = 26/28 | individuo = [4, 1, 1, 8, 6, 2, 2, 5]
```

### Quando converge
```
Solucao encontrada na geracao 762!

Melhor cromossomo : [6, 3, 5, 7, 1, 4, 2, 8]
Fitness           : 28/28
Geracao final     : 762

Tabuleiro da solucao:
    1 2 3 4 5 6 7 8
   +----------------+
 8 | . . . . . . . X |
 7 | . . . X . . . . |
 6 | X . . . . . . . |
 5 | . . X . . . . . |
 4 | . . . . . X . . |
 3 | . X . . . . . . |
 2 | . . . . . . X . |
 1 | . . . . X . . . |
   +----------------+
```

- Linhas numeradas de **8 (topo)** a **1 (base)**.
- Colunas numeradas de **1 a 8** da esquerda para a direita.
- `X` = rainha; `.` = casa vazia.

---

## Parâmetros que você pode ajustar

Edite o bloco `if __name__ == "__main__":` no final de [main.py](main.py),
ou chame `algoritmo_genetico(...)` diretamente:

| Parâmetro | Default | Efeito |
| --------- | ------- | ------ |
| `tamanho_pop` | `100` | População maior = mais diversidade, mais lento |
| `taxa_mutacao` | `0.05` | Maior = mais exploração, pode atrapalhar convergência |
| `max_geracoes` | `10000` | Limite máximo de gerações |
| `semente` | `None` | Fixa o gerador para resultados reproduzíveis |

Exemplo customizado:
```python
melhor, ger, apt = algoritmo_genetico(
    tamanho_pop=200,
    taxa_mutacao=0.03,
    max_geracoes=5000,
    semente=42,
)
```

---

## FAQ

**Por que o número de gerações varia tanto entre execuções?**
Porque a população inicial e os operadores são aleatórios. Em alguns runs
o AG acha em ~100 gerações, em outros pode levar 2000+. Use `semente=42`
(ou qualquer inteiro) para reproduzir a mesma execução.

**Por que o fitness máximo é 28?**
São `C(8,2) = 8*7/2 = 28` pares possíveis de rainhas no tabuleiro. Quando
nenhum par se ataca, o fitness é 28.

**O que é fitness 25, 26 ou 27?**
São soluções **quase boas** — restam 3, 2 ou 1 pares atacando. O AG não
para até atingir 28.

**Posso usar isso para 16 rainhas, 32 rainhas, etc?**
Sim, mas teria que generalizar o código (substituir `8` por `N` nas funções
e ajustar `C(N,2)`). O método é o mesmo.

**Por que Seleção por Roleta e não Torneio?**
Porque o enunciado pediu seleção **probabilística** (Roleta). Torneio é
mais robusto a outliers, mas Roleta é a definição clássica em livros como
Goldberg (1989).

**O algoritmo poderia ficar preso em ótimo local?**
Sim, sem mutação ele convergeria rápido para uma solução subótima. A
mutação serve exatamente para evitar isso — por isso a `taxa_mutacao` é
um parâmetro crítico.
