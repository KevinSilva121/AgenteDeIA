"""
Agente Aspirador Reativo Simples (Aula 2 de IA).

CONCEITO:
    Um agente reativo simples (ou de reflexo simples) escolhe a acao
    com base APENAS na percepcao atual, ignorando todo o historico.
    Ele segue uma TABELA DE REGRAS condicao -> acao.

AMBIENTE:
    Mundo com 2 locais: 'A' (esquerda) e 'B' (direita).
    Cada local pode estar 'Limpo' ou 'Sujo'.

PERCEPCAO:
    Tupla (local, status), por exemplo ('A', 'Sujo').

ACAO:
    Uma de: 'Aspirar', 'Direita', 'Esquerda'.

TABELA DE REGRAS (estritamente como nos slides):
    Se status == 'Sujo'  -> 'Aspirar'
    Se local  == 'A'     -> 'Direita'
    Se local  == 'B'     -> 'Esquerda'
"""

import random
import sys


# =====================================================================
# FUNCAO DO AGENTE (TABELA DE REGRAS)
# =====================================================================

def agente_aspirador(percepcao):
    """
    Recebe a percepcao (local, status) e retorna a acao.
    Implementa estritamente a tabela de regras dos slides.
    """
    local, status = percepcao

    # Regra 1: se ha sujeira, aspirar (independente do local)
    if status == 'Sujo':
        return 'Aspirar'
    # Regra 2: se esta em A (limpo), ir para a direita
    if local == 'A':
        return 'Direita'
    # Regra 3: se esta em B (limpo), ir para a esquerda
    if local == 'B':
        return 'Esquerda'


# =====================================================================
# AMBIENTE E SIMULACAO
# =====================================================================

def simular(passos=10, semente=None):
    """
    Simula o agente reativo simples por 'passos' iteracoes em um
    ambiente com 2 locais cuja sujeira inicial e aleatoria.
    """
    if semente is not None:
        random.seed(semente)

    # Estado inicial do ambiente (sujeira aleatoria em cada local)
    ambiente = {
        'A': random.choice(['Limpo', 'Sujo']),
        'B': random.choice(['Limpo', 'Sujo']),
    }
    # Posicao inicial do agente tambem aleatoria
    local_atual = random.choice(['A', 'B'])

    print("=" * 60)
    print(" Agente Aspirador Reativo Simples")
    print("=" * 60)
    print(f"Estado inicial do ambiente: A={ambiente['A']}, B={ambiente['B']}")
    print(f"Posicao inicial do agente : {local_atual}")
    print("-" * 60)

    for passo in range(1, passos + 1):
        # 1) PERCEPCAO: o agente le o estado do local atual
        status = ambiente[local_atual]
        percepcao = (local_atual, status)

        # 2) DECISAO: aplica a tabela de regras
        acao = agente_aspirador(percepcao)

        # 3) IMPRESSAO no formato pedido
        print(f"Passo {passo:2d} | Percepcao: [{local_atual}, {status}] "
              f"-> Acao: [{acao}]  | Ambiente: A={ambiente['A']}, B={ambiente['B']}")

        # 4) ATUACAO: aplica a acao no ambiente
        if acao == 'Aspirar':
            ambiente[local_atual] = 'Limpo'
        elif acao == 'Direita':
            local_atual = 'B'
        elif acao == 'Esquerda':
            local_atual = 'A'

    print("-" * 60)
    print(f"Estado final do ambiente  : A={ambiente['A']}, B={ambiente['B']}")
    print(f"Posicao final do agente   : {local_atual}")


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    # Argumentos opcionais:
    #   python main.py              -> 10 passos, ambiente aleatorio
    #   python main.py 20           -> 20 passos
    #   python main.py 15 --semente 7   -> 15 passos com semente fixa
    passos = 10
    semente = None

    if len(sys.argv) > 1:
        try:
            passos = int(sys.argv[1])
        except ValueError:
            pass
    if "--semente" in sys.argv:
        idx = sys.argv.index("--semente")
        try:
            semente = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("Erro: --semente exige um numero inteiro.")
            sys.exit(1)

    simular(passos=passos, semente=semente)
