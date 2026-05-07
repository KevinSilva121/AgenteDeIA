"""
Problema das 8 Rainhas - Formulacao de Estados Completos
com Busca Local: Subida de Encosta (Hill-Climbing) + Reinicio Aleatorio.

FORMULACAO DE ESTADOS COMPLETOS:
    O estado e SEMPRE uma configuracao com 8 rainhas no tabuleiro
    (uma por coluna), e a busca consiste em mover essas rainhas para
    melhorar a heuristica. Diferente da formulacao incremental, em que
    rainhas sao adicionadas uma a uma.

REPRESENTACAO:
    Lista de 8 inteiros entre 1 e 8.
    indice = coluna (0..7), valor = linha da rainha (1..8).
    Exemplo: [4, 1, 5, 8, 2, 7, 3, 6]

HEURISTICA h(estado):
    Numero de pares de rainhas que se atacam (diretos e indiretos).
    Diretos:   mesma linha ou mesma coluna.
    Indiretos: mesma diagonal.
    Como cada coluna tem so uma rainha (pela representacao), nao ha
    ataque por coluna. Objetivo: minimizar h ate ZERO.

ALGORITMO (Subida de Encosta com Reinicio Aleatorio):
    1. Gera estado inicial aleatorio.
    2. Avalia TODOS os vizinhos (mover cada rainha para qualquer linha
       diferente da atual em sua coluna -> 8*7 = 56 vizinhos).
    3. Se o melhor vizinho tem h MENOR que o atual, move-se para ele.
    4. Senao, esta em um maximo local: reinicia com um estado aleatorio.
    5. Para quando h == 0.
"""

import random


N = 8  # Tamanho do tabuleiro


# =====================================================================
# ESTADO E HEURISTICA
# =====================================================================

def criar_estado_aleatorio():
    """
    Estado inicial: 8 rainhas, uma por coluna, em linhas aleatorias.
    Cada gene em [1..N].
    """
    return [random.randint(1, N) for _ in range(N)]


def contar_ataques(estado):
    """
    Heuristica h(estado): conta pares de rainhas que se atacam.
    - Ataque direto:   mesma linha (estado[i] == estado[j])
    - Ataque indireto: mesma diagonal (|estado[i]-estado[j]| == |i-j|)
    Objetivo: h == 0.
    """
    ataques = 0
    for i in range(N):
        for j in range(i + 1, N):
            mesma_linha = estado[i] == estado[j]
            mesma_diagonal = abs(estado[i] - estado[j]) == abs(i - j)
            if mesma_linha or mesma_diagonal:
                ataques += 1
    return ataques


# =====================================================================
# GERACAO E AVALIACAO DE VIZINHOS
# =====================================================================

def melhor_vizinho(estado):
    """
    Avalia TODOS os vizinhos do estado atual.
    Vizinho = mover UMA rainha para outra linha em sua propria coluna.
    Total de vizinhos: N * (N-1) = 56 para N=8.
    Retorna (melhor_vizinho, h_do_melhor).
    """
    melhor_estado = estado.copy()
    melhor_h = contar_ataques(estado)

    for col in range(N):
        linha_atual = estado[col]
        for nova_linha in range(1, N + 1):
            if nova_linha == linha_atual:
                continue
            vizinho = estado.copy()
            vizinho[col] = nova_linha
            h = contar_ataques(vizinho)
            if h < melhor_h:
                melhor_h = h
                melhor_estado = vizinho

    return melhor_estado, melhor_h


# =====================================================================
# HILL-CLIMBING COM REINICIO ALEATORIO
# =====================================================================

def hill_climbing(verbose=True, max_reinicios=1000):
    """
    Subida de Encosta com Reinicio Aleatorio.
    Retorna (estado_solucao, total_iteracoes, total_reinicios).
    """
    total_iteracoes = 0

    for reinicio in range(max_reinicios):
        # ---- Estado inicial completo (aleatorio) ----
        estado = criar_estado_aleatorio()
        h = contar_ataques(estado)

        if verbose:
            print(f"\n=== Tentativa {reinicio + 1} ===")
            print(f"Estado inicial: {estado} | ataques h = {h}")

        # Caso raro: estado inicial ja e solucao
        if h == 0:
            if verbose:
                print(f"Estado inicial ja e solucao!")
            return estado, total_iteracoes, reinicio

        iteracao = 0
        while True:
            iteracao += 1
            total_iteracoes += 1

            # ---- Avalia todos os vizinhos e escolhe o melhor ----
            novo_estado, novo_h = melhor_vizinho(estado)

            if verbose:
                print(f"  Iter {iteracao:2d}: melhor vizinho h = {novo_h}  "
                      f"-> {novo_estado}")

            # ---- Tratamento de Maximo Local ----
            # Se o melhor vizinho NAO melhora h, estamos em um maximo
            # local (ou plato). Reiniciar com estado aleatorio.
            if novo_h >= h:
                if verbose:
                    print(f"  Maximo local atingido com h = {h} "
                          f"(nenhum vizinho melhora). Reiniciando.")
                break

            # ---- Move-se para o melhor vizinho ----
            estado = novo_estado
            h = novo_h

            # ---- Verifica objetivo ----
            if h == 0:
                if verbose:
                    print(f"  Solucao encontrada! h = 0.")
                return estado, total_iteracoes, reinicio

    raise RuntimeError(
        f"Nao convergiu em {max_reinicios} reinicios. "
        f"Tente aumentar 'max_reinicios'."
    )


# =====================================================================
# VISUALIZACAO
# =====================================================================

def imprimir_tabuleiro(estado):
    """
    Imprime o tabuleiro NxN com 'X' para rainhas e '.' para casas vazias.
    Linhas exibidas de cima (N) para baixo (1).
    """
    print()
    print("Tabuleiro final:")
    print("    " + " ".join(str(c) for c in range(1, N + 1)))
    print("   +" + "--" * N + "+")
    for linha in range(N, 0, -1):
        casas = []
        for coluna in range(N):
            if estado[coluna] == linha:
                casas.append("X")
            else:
                casas.append(".")
        print(f" {linha} | " + " ".join(casas) + " |")
    print("   +" + "--" * N + "+")


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" 8 Rainhas - Hill-Climbing com Reinicio Aleatorio")
    print("=" * 60)

    estado, iteracoes, reinicios = hill_climbing(verbose=True)

    print()
    print("=" * 60)
    print(" RESULTADO FINAL")
    print("=" * 60)
    print(f"Estado solucao    : {estado}")
    print(f"Ataques (h)       : {contar_ataques(estado)}")
    print(f"Iteracoes totais  : {iteracoes}")
    print(f"Reinicios feitos  : {reinicios}")
    imprimir_tabuleiro(estado)
