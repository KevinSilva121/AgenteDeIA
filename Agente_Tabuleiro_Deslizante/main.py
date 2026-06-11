"""
Quebra-cabeca de 8 Pecas (8-puzzle) resolvido com Busca A* (Aula 7).

REPRESENTACAO:
    Tabuleiro 3x3 representado como tupla de tuplas (imutavel, hashavel).
    Numeros 1..8 sao as pecas; 0 representa o espaco vazio.
    Objetivo:
        ((1, 2, 3),
         (4, 5, 6),
         (7, 8, 0))

HEURISTICA h2 (Distancia de Manhattan):
    Para cada peca (exceto o 0), soma da distancia |dx| + |dy| ate a
    sua posicao objetivo. E admissivel (nunca superestima) e consistente,
    o que garante que A* encontra a solucao OTIMA.

ALGORITMO A*:
    f(n) = g(n) + h(n)
        g(n) = numero de movimentos feitos ate o estado n
        h(n) = distancia de Manhattan do estado n ao objetivo
    - Fila de prioridade (heap) ordenada por f(n).
    - Conjunto de estados visitados para evitar revisitar.
    - Reconstroi o caminho via dicionario 'veio_de'.
"""

import heapq
import random
import sys


# =====================================================================
# CONFIGURACAO DO PROBLEMA
# =====================================================================

OBJETIVO = (
    (5, 8, 4),
    (0, 7, 6),
    (2, 3, 1),
)

# Mapeia cada peca a sua posicao (linha, coluna) no objetivo.
# Pre-calculado para acelerar a heuristica.
POSICAO_OBJETIVO = {}
for i in range(3):
    for j in range(3):
        POSICAO_OBJETIVO[OBJETIVO[i][j]] = (i, j)

MOVIMENTOS = [
    (-1, 0, 'Cima'),
    (1, 0, 'Baixo'),
    (0, -1, 'Esquerda'),
    (0, 1, 'Direita'),
]


# =====================================================================
# HEURISTICA: DISTANCIA DE MANHATTAN (h2)
# =====================================================================

def manhattan(estado):
    """
    h2(n): soma das distancias de Manhattan de cada peca (exceto 0)
    ate sua posicao no estado objetivo.
    """
    soma = 0
    for i in range(3):
        for j in range(3):
            valor = estado[i][j]
            if valor == 0:
                continue
            ti, tj = POSICAO_OBJETIVO[valor]
            soma += abs(i - ti) + abs(j - tj)
    return soma


# =====================================================================
# GERACAO DE VIZINHOS (FUNCAO SUCESSORA)
# =====================================================================

def encontrar_zero(estado):
    """Retorna (linha, coluna) do espaco vazio (0)."""
    for i in range(3):
        for j in range(3):
            if estado[i][j] == 0:
                return i, j
    raise ValueError("Estado invalido: sem espaco vazio.")


def vizinhos(estado):
    """
    Gera todos os estados acessiveis em UM movimento, deslizando
    uma peca adjacente para o espaco vazio.
    Retorna lista de (estado_novo, nome_do_movimento).
    """
    i, j = encontrar_zero(estado)
    resultado = []
    for di, dj, nome in MOVIMENTOS:
        ni, nj = i + di, j + dj
        if 0 <= ni < 3 and 0 <= nj < 3:
            # Cria nova matriz com a peca movida para o espaco vazio
            grid = [list(linha) for linha in estado]
            grid[i][j], grid[ni][nj] = grid[ni][nj], grid[i][j]
            novo = tuple(tuple(linha) for linha in grid)
            resultado.append((novo, nome))
    return resultado


# =====================================================================
# ALGORITMO A*
# =====================================================================

def a_estrela(inicial):
    """
    Busca A* com heuristica de Manhattan.
    Retorna (caminho, nos_expandidos, fronteira_max) onde:
      caminho: lista de (movimento, estado) do inicio ao objetivo
      nos_expandidos: quantos nos foram retirados da fila
      fronteira_max: tamanho maximo atingido pela fila de prioridade
    """
    if inicial == OBJETIVO:
        return [], 0, 0

    # Fila de prioridade: (f, g, contador, estado)
    # contador serve como desempate quando f e g sao iguais
    fronteira = []
    contador = 0
    heapq.heappush(fronteira,
                   (manhattan(inicial), 0, contador, inicial))

    g_score = {inicial: 0}      # melhor g(n) conhecido para cada estado
    veio_de = {}                # estado -> estado anterior
    movimento_de = {}           # estado -> nome do movimento que chegou nele
    visitados = set()           # estados ja expandidos (fechados)

    nos_expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(fronteira))
        f, g, _, estado = heapq.heappop(fronteira)

        # Pula estados ja fechados (heap pode ter copias desatualizadas)
        if estado in visitados:
            continue
        visitados.add(estado)
        nos_expandidos += 1

        # ---- TESTE DE OBJETIVO ----
        if estado == OBJETIVO:
            # Reconstroi o caminho do inicio ate o objetivo
            caminho = []
            atual = estado
            while atual in veio_de:
                anterior = veio_de[atual]
                mov = movimento_de[atual]
                caminho.append((mov, atual))
                atual = anterior
            caminho.reverse()
            return caminho, nos_expandidos, fronteira_max

        # ---- EXPANSAO ----
        for vizinho, movimento in vizinhos(estado):
            if vizinho in visitados:
                continue
            novo_g = g + 1
            # So adiciona se for um caminho melhor que o ja conhecido
            if vizinho not in g_score or novo_g < g_score[vizinho]:
                g_score[vizinho] = novo_g
                veio_de[vizinho] = estado
                movimento_de[vizinho] = movimento
                novo_f = novo_g + manhattan(vizinho)
                contador += 1
                heapq.heappush(fronteira,
                               (novo_f, novo_g, contador, vizinho))

    return None, nos_expandidos, fronteira_max


# =====================================================================
# GERACAO DE ESTADO INICIAL ALEATORIO (SEMPRE SOLUVEL)
# =====================================================================

def embaralhar(passos=50, semente=None):
    """
    Gera um estado inicial aplicando 'passos' movimentos aleatorios
    a partir do objetivo. Isso garante que o estado e SOLUVEL
    (50% dos estados aleatorios sao insoluveis no 8-puzzle).
    """
    if semente is not None:
        random.seed(semente)

    estado = OBJETIVO
    anterior = None
    for _ in range(passos):
        opcoes = vizinhos(estado)
        # Evita desfazer imediatamente o movimento anterior
        if anterior is not None:
            opcoes = [(s, m) for s, m in opcoes if s != anterior]
        anterior = estado
        estado, _ = random.choice(opcoes)
    return estado


# =====================================================================
# VISUALIZACAO
# =====================================================================

def imprimir_tabuleiro(estado, prefixo=""):
    """Imprime o tabuleiro 3x3 de forma visual ('_' para espaco vazio)."""
    for linha in estado:
        celulas = [str(v) if v != 0 else "_" for v in linha]
        print(prefixo + " ".join(f"{c:>2}" for c in celulas))


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    # Argumentos opcionais:
    #   python main.py                  -> 30 embaralhamentos, aleatorio
    #   python main.py --passos 50      -> 50 embaralhamentos
    #   python main.py --semente 42     -> reproduzivel
    passos_emb = 30
    semente = None

    if "--passos" in sys.argv:
        idx = sys.argv.index("--passos")
        try:
            passos_emb = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            pass
    if "--semente" in sys.argv:
        idx = sys.argv.index("--semente")
        try:
            semente = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("Erro: --semente exige um numero inteiro.")
            sys.exit(1)

    print("=" * 60)
    print(" 8-puzzle - Busca A* com heuristica de Manhattan (h2)")
    print("=" * 60)

    # ---- Gera estado inicial soluvel ----
    inicial = embaralhar(passos=passos_emb, semente=semente)

    print("\nEstado inicial:")
    imprimir_tabuleiro(inicial, prefixo="  ")
    print(f"\n  h(inicial) = {manhattan(inicial)} (distancia de Manhattan)")
    print(f"  (estado obtido por {passos_emb} movimentos aleatorios "
          f"a partir do objetivo)")

    print("\nEstado objetivo:")
    imprimir_tabuleiro(OBJETIVO, prefixo="  ")

    # ---- Resolve com A* ----
    print("\n" + "-" * 60)
    print(" Executando A*...")
    print("-" * 60)
    caminho, nos_expandidos, fronteira_max = a_estrela(inicial)

    if caminho is None:
        print("\nNao foi possivel encontrar solucao.")
        sys.exit(1)

    # ---- Mostra o caminho passo a passo ----
    print(f"\nCaminho ate o objetivo ({len(caminho)} movimentos):\n")
    print("  Passo 0 (inicial):")
    imprimir_tabuleiro(inicial, prefixo="    ")

    for n, (movimento, estado) in enumerate(caminho, start=1):
        print(f"\n  Passo {n} ({movimento}):")
        imprimir_tabuleiro(estado, prefixo="    ")

    # ---- Estatisticas finais ----
    print("\n" + "=" * 60)
    print(" RESULTADO")
    print("=" * 60)
    print(f"Movimentos ate a solucao   : {len(caminho)}")
    print(f"Nos expandidos pelo A*     : {nos_expandidos}")
    print(f"Tamanho maximo da fronteira: {fronteira_max}")
    print(f"Solucao OTIMA garantida    : sim (Manhattan e admissivel)")
