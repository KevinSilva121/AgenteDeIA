"""
Problema das 8 Rainhas resolvido com Algoritmo Genetico.

Representacao do cromossomo:
    Lista de 8 inteiros entre 1 e 8.
    O indice da lista representa a COLUNA (0..7).
    O valor armazenado representa a LINHA da rainha (1..8).
    Exemplo: [2, 4, 7, 4, 8, 5, 5, 2]

Funcao de aptidao (fitness):
    Conta pares de rainhas que NAO se atacam.
    Total de pares possiveis = C(8,2) = 28 -> fitness maximo = 28.

Operadores geneticos:
    - Selecao   : metodo da Roleta (probabilidade proporcional ao fitness)
    - Crossover : um ponto de corte aleatorio
    - Mutacao   : pequena taxa que troca um gene por valor aleatorio em [1,8]
"""

import random


# =====================================================================
# REPRESENTACAO E POPULACAO
# =====================================================================

def criar_individuo():
    """Cria um cromossomo aleatorio de 8 genes em [1..8]."""
    return [random.randint(1, 8) for _ in range(8)]


def criar_populacao(tamanho):
    """Gera a populacao inicial com individuos aleatorios."""
    return [criar_individuo() for _ in range(tamanho)]


# =====================================================================
# FUNCAO DE APTIDAO (FITNESS)
# =====================================================================

def fitness(individuo):
    """
    Conta o numero de pares de rainhas que NAO se atacam.
    - Como cada gene esta em uma coluna unica (pelo indice), nunca
      ha ataque por coluna.
    - Ataque por linha:    individuo[i] == individuo[j]
    - Ataque por diagonal: |individuo[i] - individuo[j]| == |i - j|
    Maximo possivel = C(8,2) = 28.
    """
    nao_ataques = 0
    for i in range(8):
        for j in range(i + 1, 8):
            mesma_linha = individuo[i] == individuo[j]
            mesma_diagonal = abs(individuo[i] - individuo[j]) == abs(i - j)
            if not mesma_linha and not mesma_diagonal:
                nao_ataques += 1
    return nao_ataques


# =====================================================================
# OPERADOR 1: SELECAO (METODO DA ROLETA)
# =====================================================================

def selecao_roleta(populacao, aptidoes):
    """
    Seleciona UM individuo com probabilidade proporcional ao seu fitness.

    Visualmente: imagine uma roleta onde cada individuo ocupa uma fatia
    proporcional ao seu fitness. Sorteamos um ponto aleatorio e devolvemos
    o individuo cuja fatia contem esse ponto.
    """
    total = sum(aptidoes)
    # Caso degenerado: todos com fitness 0 -> sorteio uniforme
    if total == 0:
        return random.choice(populacao)
    sorteio = random.uniform(0, total)
    acumulado = 0
    for individuo, apt in zip(populacao, aptidoes):
        acumulado += apt
        if acumulado >= sorteio:
            return individuo
    return populacao[-1]  # fallback por arredondamento


# =====================================================================
# OPERADOR 2: CROSSOVER (UM PONTO DE CORTE)
# =====================================================================

def crossover_um_ponto(pai1, pai2):
    """
    Cruzamento de um ponto de corte aleatorio.
    Sorteia uma posicao 'ponto' entre 1 e 7 e gera dois descendentes:
      filho1 = pai1[:ponto] + pai2[ponto:]
      filho2 = pai2[:ponto] + pai1[ponto:]
    """
    ponto = random.randint(1, 7)
    filho1 = pai1[:ponto] + pai2[ponto:]
    filho2 = pai2[:ponto] + pai1[ponto:]
    return filho1, filho2


# =====================================================================
# OPERADOR 3: MUTACAO
# =====================================================================

def mutacao(individuo, taxa):
    """
    Para cada gene, com probabilidade 'taxa', troca-o por um valor
    aleatorio entre 1 e 8. Mutacao mantem diversidade genetica e evita
    convergencia prematura para minimos locais.
    """
    novo = individuo.copy()
    for i in range(8):
        if random.random() < taxa:
            novo[i] = random.randint(1, 8)
    return novo


# =====================================================================
# LOOP PRINCIPAL DO ALGORITMO GENETICO
# =====================================================================

def algoritmo_genetico(tamanho_pop=100, taxa_mutacao=0.05,
                       max_geracoes=10000, semente=None):
    """
    Executa o AG ate encontrar fitness = 28 ou atingir max_geracoes.
    Retorna (melhor_individuo, geracao_em_que_encontrou, fitness_final).
    """
    if semente is not None:
        random.seed(semente)

    # 1) Populacao inicial aleatoria
    populacao = criar_populacao(tamanho_pop)

    for geracao in range(max_geracoes):
        # Avalia toda a populacao
        aptidoes = [fitness(ind) for ind in populacao]
        melhor_idx = aptidoes.index(max(aptidoes))
        melhor_apt = aptidoes[melhor_idx]
        melhor_ind = populacao[melhor_idx]

        # Log a cada 100 geracoes
        if geracao % 100 == 0:
            print(f"Geracao {geracao:5d} | melhor fitness = {melhor_apt}/28 "
                  f"| individuo = {melhor_ind}")

        # Criterio de parada: solucao otima encontrada
        if melhor_apt == 28:
            print(f"\nSolucao encontrada na geracao {geracao}!")
            return melhor_ind, geracao, melhor_apt

        # Constroi a nova geracao
        nova_populacao = []
        while len(nova_populacao) < tamanho_pop:
            # ---- ETAPA 1: SELECAO ----
            pai1 = selecao_roleta(populacao, aptidoes)
            pai2 = selecao_roleta(populacao, aptidoes)

            # ---- ETAPA 2: CROSSOVER ----
            filho1, filho2 = crossover_um_ponto(pai1, pai2)

            # ---- ETAPA 3: MUTACAO ----
            filho1 = mutacao(filho1, taxa_mutacao)
            filho2 = mutacao(filho2, taxa_mutacao)

            nova_populacao.append(filho1)
            if len(nova_populacao) < tamanho_pop:
                nova_populacao.append(filho2)

        populacao = nova_populacao

    # Nao convergiu dentro do limite
    aptidoes = [fitness(ind) for ind in populacao]
    melhor_idx = aptidoes.index(max(aptidoes))
    print(f"\nLimite de {max_geracoes} geracoes atingido sem solucao otima.")
    return populacao[melhor_idx], max_geracoes, aptidoes[melhor_idx]


# =====================================================================
# VISUALIZACAO DO TABULEIRO
# =====================================================================

def imprimir_tabuleiro(individuo):
    """
    Imprime o tabuleiro 8x8 com 'X' para rainhas e '.' para casas vazias.
    Linhas exibidas de cima (8) para baixo (1).
    """
    print()
    print("Tabuleiro da solucao:")
    print("    " + " ".join(str(c) for c in range(1, 9)))
    print("   +" + "--" * 8 + "+")
    for linha in range(8, 0, -1):
        casas = []
        for coluna in range(8):
            if individuo[coluna] == linha:
                casas.append("X")
            else:
                casas.append(".")
        print(f" {linha} | " + " ".join(casas) + " |")
    print("   +" + "--" * 8 + "+")


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    melhor, geracao, apt = algoritmo_genetico(
        tamanho_pop=100,
        taxa_mutacao=0.05,
        max_geracoes=10000,
    )
    print()
    print(f"Melhor cromossomo : {melhor}")
    print(f"Fitness           : {apt}/28")
    print(f"Geracao final     : {geracao}")
    imprimir_tabuleiro(melhor)
