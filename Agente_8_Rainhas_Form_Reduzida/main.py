"""
Problema das 8 Rainhas - Busca Incremental com Formulacao Reduzida
Algoritmo: Busca em Profundidade (DFS) com Backtracking.

FORMULACAO INCREMENTAL REDUZIDA:
    - Estado inicial: tabuleiro VAZIO.
    - Acao: adicionar uma rainha na proxima coluna disponivel.
    - REDUCAO: ao escolher onde colocar a rainha da coluna k, so
      consideramos posicoes que NAO sejam atacadas pelas rainhas
      ja colocadas nas colunas anteriores (0..k-1).
    - Isso poda drasticamente o espaco de busca: em vez de testar
      todas as 8^8 = 16.777.216 configuracoes (formulacao completa),
      o DFS reduzido visita apenas algumas centenas de nos.

REPRESENTACAO:
    Lista de N inteiros. estado[i] = linha (1..N) da rainha na coluna i.
    Valor 0 = coluna ainda nao preenchida.
    Exemplo de solucao: [1, 5, 8, 6, 3, 7, 2, 4]

TESTE DE OBJETIVO:
    Coluna atual == N -> todas as 8 rainhas foram posicionadas com
    sucesso seguindo a regra de seguranca.

SAIDA:
    Tabuleiro final + numero total de estados (nos) visitados.
"""

import random
import sys


N = 8  # Tamanho do tabuleiro


# =====================================================================
# TESTE DE SEGURANCA (FORMULACAO REDUZIDA)
# =====================================================================

def eh_seguro(estado, coluna, linha):
    """
    Verifica se a rainha na posicao (coluna, linha) e segura
    considerando APENAS as rainhas ja colocadas nas colunas
    ANTERIORES (0..coluna-1). Esta e a essencia da formulacao
    REDUZIDA: nao geramos estados invalidos.

    Como cada coluna tem no maximo uma rainha (pela representacao),
    nao precisamos verificar ataque por coluna - apenas:
      - mesma linha
      - mesma diagonal (|delta_linha| == |delta_coluna|)
    """
    for col_ant in range(coluna):
        linha_ant = estado[col_ant]
        # Ataque direto (mesma linha)
        if linha_ant == linha:
            return False
        # Ataque indireto (diagonal)
        if abs(linha_ant - linha) == abs(col_ant - coluna):
            return False
    return True


# =====================================================================
# BUSCA EM PROFUNDIDADE (DFS) COM BACKTRACKING
# =====================================================================

def dfs(estado, coluna, contador, verbose=False):
    """
    DFS recursivo. A cada chamada:
      1. Incrementa o contador de nos visitados (estado parcial atual).
      2. Se 'coluna' == N, todas as rainhas foram posicionadas -> objetivo.
      3. Caso contrario, tenta cada linha (em ordem ALEATORIA) na coluna:
          - Se a posicao e segura, fixa a rainha e recursa.
          - Se a recursao retorna True, propaga o sucesso.
          - Senao, faz backtracking (limpa a posicao) e tenta outra linha.

    A ordem das linhas e EMBARALHADA a cada chamada para que cada execucao
    encontre uma solucao diferente. O algoritmo continua sendo um DFS
    completo - apenas explora a arvore em ordem aleatoria.
    """
    contador['nos'] += 1

    if verbose:
        prefixo = "  " * coluna
        parciais = [str(l) if l > 0 else '_' for l in estado]
        print(f"{prefixo}[no {contador['nos']:3d}] coluna={coluna} "
              f"estado=[{','.join(parciais)}]")

    # ---- TESTE DE OBJETIVO ----
    if coluna == N:
        return True

    # ---- EXPANSAO: tenta cada linha na coluna atual (ordem ALEATORIA) ----
    linhas = list(range(1, N + 1))
    random.shuffle(linhas)
    for linha in linhas:
        if eh_seguro(estado, coluna, linha):
            # Acao: posiciona a rainha
            estado[coluna] = linha

            # Aprofunda na arvore (DFS)
            if dfs(estado, coluna + 1, contador, verbose):
                return True

            # Backtracking: nao deu certo, desfaz a jogada
            estado[coluna] = 0

    return False


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

def resolver(verbose=False):
    """Executa o DFS e devolve (estado_solucao, nos_visitados)."""
    estado = [0] * N           # tabuleiro vazio (formulacao incremental)
    contador = {'nos': 0}      # contador de estados visitados
    sucesso = dfs(estado, 0, contador, verbose=verbose)
    return estado, contador['nos'], sucesso


if __name__ == "__main__":
    # Argumentos:
    #   -v          : modo verboso (imprime a arvore de busca)
    #   --semente N : fixa a semente do random (reproducibilidade)
    verbose = "-v" in sys.argv
    if "--semente" in sys.argv:
        idx = sys.argv.index("--semente")
        try:
            semente = int(sys.argv[idx + 1])
            random.seed(semente)
            print(f"(Semente fixada em {semente} - resultado reproduzivel)")
        except (IndexError, ValueError):
            print("Erro: --semente exige um numero inteiro.")
            sys.exit(1)

    print("=" * 60)
    print(" 8 Rainhas - Busca Incremental com Formulacao Reduzida")
    print(" Algoritmo: Busca em Profundidade (DFS)")
    print("=" * 60)

    estado, nos_visitados, sucesso = resolver(verbose=verbose)

    print()
    print("=" * 60)
    print(" RESULTADO")
    print("=" * 60)
    if sucesso:
        print(f"Solucao encontrada!")
        print(f"Estado solucao    : {estado}")
        print(f"Nos visitados     : {nos_visitados}")
        imprimir_tabuleiro(estado)
    else:
        print("Nenhuma solucao encontrada (nao deveria acontecer para N=8).")
