"""
Agente Baseado em Tabela (Table-Driven Agent) - Aula 2 de IA.

CONCEITO:
    O agente NAO tem regras: ele tem uma TABELA gigantesca onde cada
    entrada e (sequencia_de_percepcoes -> acao). A cada passo:
      1. Recebe a percepcao atual.
      2. Anexa-a ao seu HISTORICO de percepcoes (lista 'percepts').
      3. Consulta a tabela usando o historico COMPLETO como chave.
      4. Devolve a acao correspondente.

PROBLEMA FUNDAMENTAL (CRESCIMENTO EXPONENCIAL):
    Se P = numero de percepcoes possiveis e T = numero de passos,
    a tabela precisa ter SUM_{n=1..T} P^n entradas.

    No mundo do aspirador: P = 2 locais x 2 estados = 4 percepcoes.
    Para T = 10 passos:
        4^1 + 4^2 + ... + 4^10 = (4^11 - 4) / 3 = 1.398.100 entradas.

    Especificar essas 1,4 milhoes de entradas a mao e inviavel.
    Esta limitacao motiva o uso de agentes BASEADOS EM REGRAS
    (reflexo simples, baseado em modelo, etc.) nas aulas seguintes.
"""

import random
import sys
from itertools import product


# =====================================================================
# PERCEPCOES POSSIVEIS
# =====================================================================

LOCAIS = ['A', 'B']
ESTADOS = ['Limpo', 'Sujo']
PERCEPCOES_POSSIVEIS = [(l, s) for l in LOCAIS for s in ESTADOS]
# = [('A','Limpo'), ('A','Sujo'), ('B','Limpo'), ('B','Sujo')]


# =====================================================================
# A TABELA (DICIONARIO)
# =====================================================================
#
# Em um Agente Baseado em Tabela "puro", o projetista definiria CADA
# entrada da tabela manualmente. Para fins didaticos vamos exibir um
# pequeno fragmento ESCRITO A MAO (cobrindo as primeiras percepcoes)
# e depois GERAR PROGRAMATICAMENTE o resto - reforcando justamente o
# motivo pelo qual essa abordagem nao escala.
# =====================================================================

# ---- Fragmento manual: as 4 primeiras entradas (T = 1) ----
TABELA_MANUAL = {
    # Sequencia de percepcoes (tupla de tuplas) -> Acao
    (('A', 'Sujo'),):  'Aspirar',
    (('A', 'Limpo'),): 'Direita',
    (('B', 'Sujo'),):  'Aspirar',
    (('B', 'Limpo'),): 'Esquerda',

    # Algumas entradas para T = 2 (apenas para mostrar a estrutura)
    (('A', 'Limpo'), ('B', 'Sujo')):  'Aspirar',
    (('A', 'Limpo'), ('B', 'Limpo')): 'Esquerda',
    (('B', 'Limpo'), ('A', 'Sujo')):  'Aspirar',
    (('B', 'Limpo'), ('A', 'Limpo')): 'Direita',
    # ... ainda faltariam 4^2 - 4 = 12 entradas so para T=2.
    # ... e para T=10 faltariam ~1,4 MILHOES.
}


def construir_tabela_completa(max_passos):
    """
    Gera uma tabela completa cobrindo TODAS as sequencias de percepcoes
    de tamanho 1 ate max_passos.

    NOTA: a regra usada aqui (aspirar se sujo; senao alternar lado) e
    apenas para preencher a tabela e fazer a simulacao funcionar.
    Em um "Agente Baseado em Tabela" verdadeiro, cada um desses
    valores seria HARD-CODED pelo projetista - inviavel para max_passos
    grande.
    """
    tabela = {}
    for n in range(1, max_passos + 1):
        for sequencia in product(PERCEPCOES_POSSIVEIS, repeat=n):
            local_atual, status_atual = sequencia[-1]
            if status_atual == 'Sujo':
                acao = 'Aspirar'
            elif local_atual == 'A':
                acao = 'Direita'
            else:
                acao = 'Esquerda'
            tabela[sequencia] = acao
    return tabela


# =====================================================================
# AGENTE BASEADO EM TABELA
# =====================================================================

class AgenteBaseadoTabela:
    """
    Implementacao classica (AIMA, capitulo 2):

        function TABLE-DRIVEN-AGENT(percept) returns an action
            persistent: percepts, a sequence, initially empty
                        table, a table of actions, indexed by percept sequences
            append percept to the end of percepts
            action <- LOOKUP(percepts, table)
            return action
    """

    def __init__(self, tabela):
        self.percepts = []   # historico de percepcoes
        self.tabela = tabela

    def __call__(self, percepcao):
        # 1) Anexa a percepcao ao historico
        self.percepts.append(percepcao)
        # 2) Usa o historico inteiro como chave
        chave = tuple(self.percepts)
        # 3) Consulta a tabela
        return self.tabela.get(chave)


# =====================================================================
# DEMONSTRACAO DO CRESCIMENTO EXPONENCIAL
# =====================================================================

def demonstrar_crescimento_exponencial(passos_max=10):
    """
    Imprime quantas entradas a tabela precisaria para suportar
    sequencias de 1 ate N passos. Mostra explicitamente o caso N = 10
    citado nos slides.
    """
    P = len(PERCEPCOES_POSSIVEIS)  # 4 percepcoes possiveis
    print("=" * 65)
    print(" CRESCIMENTO EXPONENCIAL DA TABELA (Limitacao da Aula 2)")
    print("=" * 65)
    print(f" Percepcoes possiveis por passo: P = {P}")
    print(f" Locais  : {LOCAIS}")
    print(f" Estados : {ESTADOS}")
    print()
    print(f" {'Passos (T)':>10} | {'Entradas para esse T':>24} | "
          f"{'Total acumulado':>17}")
    print(" " + "-" * 63)
    acumulado = 0
    for t in range(1, passos_max + 1):
        nesse_t = P ** t
        acumulado += nesse_t
        marca = "  <-- impossivel manualmente" if t >= 5 else ""
        print(f" {t:>10} | {nesse_t:>24,} | {acumulado:>17,}{marca}")
    print()
    print(f" => Para T = {passos_max} passos, seriam necessarias")
    print(f"    {acumulado:,} entradas na tabela. Hard-coding e inviavel.")
    print(f"    Esta e a razao pela qual agentes baseados em REGRAS")
    print(f"    (proxima aula) sao preferidos.")
    print("=" * 65)
    print()


# =====================================================================
# AMBIENTE E SIMULACAO
# =====================================================================

def simular(agente, passos=10, semente=None):
    """Simula o agente em um ambiente com 2 locais e sujeira aleatoria."""
    if semente is not None:
        random.seed(semente)

    ambiente = {
        'A': random.choice(['Limpo', 'Sujo']),
        'B': random.choice(['Limpo', 'Sujo']),
    }
    local_atual = random.choice(['A', 'B'])

    print(f"Estado inicial do ambiente: A={ambiente['A']}, B={ambiente['B']}")
    print(f"Posicao inicial do agente : {local_atual}")
    print("-" * 65)

    for passo in range(1, passos + 1):
        # Percepcao
        status = ambiente[local_atual]
        percepcao = (local_atual, status)

        # Agente consulta a tabela usando o HISTORICO inteiro
        acao = agente(percepcao)

        if acao is None:
            print(f"Passo {passo:2d} | Percepcao: [{local_atual}, {status}] "
                  f"-> Acao: [INDEFINIDA - sequencia nao existe na tabela]")
            print("\n   ^^ Essa e a falha do Agente Baseado em Tabela:")
            print("      a sequencia atual nao foi previamente catalogada.")
            break

        print(f"Passo {passo:2d} | Percepcao: [{local_atual}, {status}] "
              f"-> Acao: [{acao}]  | Ambiente: A={ambiente['A']}, "
              f"B={ambiente['B']}  | Histor.: {len(agente.percepts)}")

        # Aplica a acao no ambiente
        if acao == 'Aspirar':
            ambiente[local_atual] = 'Limpo'
        elif acao == 'Direita':
            local_atual = 'B'
        elif acao == 'Esquerda':
            local_atual = 'A'

    print("-" * 65)
    print(f"Estado final do ambiente : A={ambiente['A']}, B={ambiente['B']}")
    print(f"Posicao final do agente  : {local_atual}")
    print(f"Tamanho final do historico (percepts): {len(agente.percepts)}")


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    # Argumentos opcionais:
    #   python main.py              -> 10 passos, ambiente aleatorio
    #   python main.py 20           -> 20 passos
    #   python main.py 15 --semente 7
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

    # 1) Mostra o problema do crescimento exponencial
    demonstrar_crescimento_exponencial(passos_max=10)

    # 2) Mostra um pedaco da tabela manual (didatico)
    print("Fragmento ESCRITO A MAO da tabela (mostrando a estrutura):")
    for chave, valor in list(TABELA_MANUAL.items())[:8]:
        print(f"  {chave}  ->  {valor}")
    print(f"  (... + faltariam ~1,4 milhoes de entradas para 10 passos)")
    print()

    # 3) Constroi a tabela COMPLETA programaticamente para a simulacao
    #    funcionar (em um agente real isso nao seria possivel sem regras)
    print(f"Gerando tabela completa para suportar ate {passos} passos...")
    tabela = construir_tabela_completa(passos)
    print(f"Tabela gerada com {len(tabela):,} entradas.")
    print()

    # 4) Cria o agente e roda a simulacao
    agente = AgenteBaseadoTabela(tabela)
    print("=" * 65)
    print(" SIMULACAO DO AGENTE BASEADO EM TABELA")
    print("=" * 65)
    simular(agente, passos=passos, semente=semente)
