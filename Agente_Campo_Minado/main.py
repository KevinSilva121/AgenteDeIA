"""
Agente Logico para o Campo Minado (Aula 9 - Agentes Logicos).

MODELAGEM LOGICA:
    Cada celula (i,j) e uma variavel proposicional M_{i,j}:
        M_{i,j} = True  <=> ha mina em (i,j)
        M_{i,j} = False <=> celula segura

    Quando uma celula com numero N e revelada, adicionamos a BC a
    sentenca "exatamente N das suas 8 vizinhas sao minas". Em logica:
        |{ M_{a,b} : (a,b) vizinha de (i,j) e M_{a,b}=True }| = N

INFERENCIA:
    - Se uma sentenca {C1, ..., Ck} = N tem N == k, todas sao MINAS.
    - Se N == 0, todas sao SEGURAS.
    - Regra de subconjunto (sound): se S1 subset S2, entao
      (S2 - S1) = (count2 - count1). Permite derivar novas sentencas.
    - A funcao checar_seguranca(celula) prova se uma celula e segura
      ou mina pelas sentencas da BC.

ESTRATEGIA DO AGENTE:
    1) Joga em qualquer celula provadamente segura (ainda nao jogada).
    2) Se nenhuma e segura, escolhe a celula com MENOR probabilidade
       estimada de ser mina (estatistica + regras locais).
"""

import random
import sys


# =====================================================================
# CLASSE Sentence
# =====================================================================

class Sentence:
    """
    Sentenca logica: 'exatamente self.count das celulas em self.cells
    sao minas'. Equivalente a uma restricao numerica em variaveis
    booleanas.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __hash__(self):
        return hash((frozenset(self.cells), self.count))

    def __str__(self):
        return f"{sorted(self.cells)} = {self.count}"

    def __repr__(self):
        return self.__str__()

    # ---- Inferencia local (sobre uma unica sentenca) ----

    def known_mines(self):
        """Se count == |cells|, todas as celulas sao minas."""
        if len(self.cells) == self.count and self.count > 0:
            return set(self.cells)
        return set()

    def known_safes(self):
        """Se count == 0, todas as celulas sao seguras."""
        if self.count == 0:
            return set(self.cells)
        return set()

    # ---- Atualizacoes quando descobrimos algo ----

    def mark_mine(self, cell):
        """Sabendo que `cell` e mina, removemos e diminuimos count."""
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """Sabendo que `cell` e segura, apenas removemos do conjunto."""
        if cell in self.cells:
            self.cells.discard(cell)


# =====================================================================
# CLASSE MinesweeperAI (Agente Logico)
# =====================================================================

class MinesweeperAI:

    def __init__(self, altura=8, largura=8, verbose=True):
        self.altura = altura
        self.largura = largura
        self.verbose = verbose

        self.movimentos_feitos = set()
        self.mines = set()      # celulas provadas como mina
        self.safes = set()      # celulas provadas como seguras
        self.knowledge = []     # base de conhecimento (lista de Sentence)

    # -----------------------------------------------------------------
    # Marcacoes propagam para todas as sentencas
    # -----------------------------------------------------------------

    def mark_mine(self, cell):
        self.mines.add(cell)
        for s in self.knowledge:
            s.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for s in self.knowledge:
            s.mark_safe(cell)

    # -----------------------------------------------------------------
    # Adicionar conhecimento + Inferencia
    # -----------------------------------------------------------------

    def vizinhos(self, cell):
        """Retorna ate 8 celulas vizinhas dentro do tabuleiro."""
        i0, j0 = cell
        viz = set()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ni, nj = i0 + di, j0 + dj
                if 0 <= ni < self.altura and 0 <= nj < self.largura:
                    viz.add((ni, nj))
        return viz

    def add_knowledge(self, cell, count):
        """
        Chamado quando o ambiente revela `cell` com numero `count`:
          1) marca cell como movimento feito e como segura;
          2) constroi a sentenca a partir dos vizinhos ainda nao
             determinados (descontando minas conhecidas);
          3) aplica inferencia ate atingir um ponto fixo.
        """
        self.movimentos_feitos.add(cell)
        self.mark_safe(cell)

        viz = self.vizinhos(cell)
        novo_count = count
        novos_celulas = set()
        for v in viz:
            if v in self.mines:
                novo_count -= 1
            elif v not in self.safes:
                novos_celulas.add(v)

        if novos_celulas:
            sent = Sentence(novos_celulas, novo_count)
            self.knowledge.append(sent)
            self._log(f"Nova sentenca pela regra de {cell}: {sent}")

        # Inferencia ate ponto fixo
        self._inferir()

    def _inferir(self):
        """
        Aplica as regras de inferencia logica:
          R1: count == |cells|  =>  todas sao minas
          R2: count == 0         =>  todas sao seguras
          R3: S1 subset S2       =>  (S2 - S1) = (count2 - count1)
        Repete ate que nenhuma sentenca nova ou conclusao seja derivada.
        """
        mudou = True
        while mudou:
            mudou = False

            # R1 e R2: extrai conclusoes diretas das sentencas existentes
            minas_novas = set()
            seguras_novas = set()
            for sent in self.knowledge:
                minas_novas |= sent.known_mines()
                seguras_novas |= sent.known_safes()

            for m in minas_novas:
                if m not in self.mines:
                    self.mark_mine(m)
                    self._log(f"  >> Inferido: {m} e MINA "
                              f"(sentenca com count == |cells|)")
                    mudou = True
            for s in seguras_novas:
                if s not in self.safes:
                    self.mark_safe(s)
                    self._log(f"  >> Inferido: {s} e SEGURA "
                              f"(sentenca com count == 0)")
                    mudou = True

            # Limpa sentencas vazias ou triviais
            self.knowledge = [s for s in self.knowledge if s.cells]

            # R3: regra de subconjunto - gera novas sentencas
            novas = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 is s2 or not s1.cells or not s2.cells:
                        continue
                    if s1.cells.issubset(s2.cells) and s1.cells != s2.cells:
                        nova = Sentence(s2.cells - s1.cells,
                                        s2.count - s1.count)
                        if (nova not in self.knowledge
                                and nova not in novas
                                and nova.cells):
                            novas.append(nova)
                            self._log(f"  >> Subset: ({s2}) - ({s1}) "
                                      f"=> {nova}")
            if novas:
                self.knowledge.extend(novas)
                mudou = True

    # -----------------------------------------------------------------
    # Funcao logica obrigatoria: checar_seguranca
    # -----------------------------------------------------------------

    def checar_seguranca(self, celula):
        """
        Determina o status logico de `celula` segundo a BC:
            'segura'        - provada segura (negar a hipotese 'segura'
                              gera contradicao com alguma sentenca)
            'mina'          - provada mina   (negar 'mina' gera contradicao)
            'desconhecida'  - BC nao prova nada sobre esta celula

        Equivale a 'BC |= ~M(celula)' (segura) ou 'BC |= M(celula)' (mina).
        Como a inferencia ja foi aplicada, basta consultar os conjuntos.
        """
        if celula in self.safes:
            return 'segura'
        if celula in self.mines:
            return 'mina'
        # Verificacao adicional via sentencas (forca a regra local)
        for sent in self.knowledge:
            if celula in sent.cells:
                if sent.count == 0:
                    return 'segura'
                if sent.count == len(sent.cells):
                    return 'mina'
        return 'desconhecida'

    # -----------------------------------------------------------------
    # Decisao: jogada segura ou heuristica de risco
    # -----------------------------------------------------------------

    def jogada_segura(self):
        """Retorna uma celula provadamente segura ainda nao jogada."""
        for c in self.safes:
            if c not in self.movimentos_feitos:
                return c
        return None

    def jogada_arriscada(self):
        """
        Heuristica: escolhe a celula desconhecida com MENOR probabilidade
        estimada de ser mina, baseada nas sentencas que a contem.

        Probabilidade local de uma celula c em uma sentenca {C}=k:
            P(c e mina | sentenca) = k / |C|
        Tomamos o MAXIMO entre as sentencas que a contem (pior caso),
        e escolhemos a celula com o MENOR pior-caso.
        """
        candidatos = []
        for i in range(self.altura):
            for j in range(self.largura):
                c = (i, j)
                if c in self.movimentos_feitos or c in self.mines:
                    continue
                prob = 0.0
                for sent in self.knowledge:
                    if c in sent.cells and len(sent.cells) > 0:
                        p_local = sent.count / len(sent.cells)
                        if p_local > prob:
                            prob = p_local
                candidatos.append((prob, c))

        if not candidatos:
            return None

        candidatos.sort(key=lambda x: (x[0], x[1]))
        prob, escolhida = candidatos[0]
        self._log(f"  >> Heuristica: {escolhida} tem prob. estimada "
                  f"{prob:.0%} de ser mina (menor entre desconhecidas).")
        return escolhida

    # -----------------------------------------------------------------
    # Log
    # -----------------------------------------------------------------

    def _log(self, msg):
        if self.verbose:
            print(msg)


# =====================================================================
# AMBIENTE DO JOGO
# =====================================================================

class Minesweeper:
    """Tabuleiro do Campo Minado. Apenas o ambiente - separado da AI."""

    def __init__(self, altura=8, largura=8, n_minas=8, semente=None,
                 primeira_celula=None):
        if semente is not None:
            random.seed(semente)
        self.altura = altura
        self.largura = largura
        self.n_minas = n_minas
        self.minas = set()
        self.reveladas = set()

        # Sorteia minas, evitando a primeira celula (pratica padrao
        # do Minesweeper para o primeiro clique nao matar)
        proibidas = {primeira_celula} if primeira_celula else set()
        while len(self.minas) < n_minas:
            i = random.randrange(altura)
            j = random.randrange(largura)
            if (i, j) not in proibidas:
                self.minas.add((i, j))

    def eh_mina(self, cell):
        return cell in self.minas

    def contagem(self, cell):
        """Numero de minas nas 8 vizinhas."""
        c = 0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ni, nj = cell[0] + di, cell[1] + dj
                if 0 <= ni < self.altura and 0 <= nj < self.largura:
                    if (ni, nj) in self.minas:
                        c += 1
        return c

    def venceu(self):
        return len(self.reveladas) == self.altura * self.largura - self.n_minas


# =====================================================================
# VISUALIZACAO
# =====================================================================

def imprimir_tabuleiro(jogo, ai, revelar_minas=False):
    """
    Mostra o tabuleiro:
      - numero  -> celula revelada com aquela contagem
      - .       -> celula revelada com 0 vizinhas (vazia)
      - ?       -> celula desconhecida
      - F       -> celula que a AI marcou como mina (flag logico)
      - *       -> mina REAL (so se revelar_minas=True)
    """
    print()
    print("    " + " ".join(f"{j:>2}" for j in range(jogo.largura)))
    print("   +" + "-" * (jogo.largura * 3) + "+")
    for i in range(jogo.altura):
        linha = f" {i:>2}|"
        for j in range(jogo.largura):
            cell = (i, j)
            if cell in jogo.reveladas:
                n = jogo.contagem(cell)
                ch = str(n) if n > 0 else "."
            elif cell in ai.mines:
                ch = "F"
            elif revelar_minas and cell in jogo.minas:
                ch = "*"
            else:
                ch = "?"
            linha += f" {ch:>2}"
        linha += " |"
        print(linha)
    print("   +" + "-" * (jogo.largura * 3) + "+")


# =====================================================================
# LOOP PRINCIPAL
# =====================================================================

def jogar(altura=8, largura=8, n_minas=10, semente=None, verbose=True):
    # Primeiro clique sera no canto (0,0); evitamos mina la
    primeira = (0, 0)
    jogo = Minesweeper(altura, largura, n_minas, semente=semente,
                       primeira_celula=primeira)
    ai = MinesweeperAI(altura, largura, verbose=verbose)

    print("=" * 60)
    print(" Campo Minado - Agente Logico Proposicional")
    print("=" * 60)
    print(f"Tabuleiro {altura}x{largura} com {n_minas} minas. "
          f"Primeira jogada: {primeira}.")
    imprimir_tabuleiro(jogo, ai)

    rodada = 0
    while True:
        rodada += 1
        print(f"\n----- Rodada {rodada} -----")

        # Decide a jogada
        if rodada == 1:
            jogada = primeira
            print(f"Jogada inicial obrigatoria: {jogada}")
        else:
            jogada = ai.jogada_segura()
            if jogada is not None:
                print(f"Jogada SEGURA (provada pela BC): {jogada}")
            else:
                print("Nenhuma celula provadamente segura. "
                      "Aplicando heuristica de risco...")
                jogada = ai.jogada_arriscada()
                if jogada is None:
                    print("Sem jogadas disponiveis. Encerrando.")
                    return False
                print(f"Jogada arriscada: {jogada}")

        # Aplica no ambiente
        if jogo.eh_mina(jogada):
            print(f"\nDERROTA! Pisou em mina em {jogada}.")
            imprimir_tabuleiro(jogo, ai, revelar_minas=True)
            return False

        n = jogo.contagem(jogada)
        jogo.reveladas.add(jogada)
        print(f"Revelado {jogada} -> contagem = {n}")
        ai.add_knowledge(jogada, n)

        imprimir_tabuleiro(jogo, ai)

        if jogo.venceu():
            print(f"\nVITORIA em {rodada} rodadas! Todas as casas seguras "
                  f"foram reveladas.")
            return True


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    altura = 8
    largura = 8
    n_minas = 10
    semente = None

    if "--altura" in sys.argv:
        idx = sys.argv.index("--altura")
        try: altura = int(sys.argv[idx + 1])
        except (IndexError, ValueError): pass
    if "--largura" in sys.argv:
        idx = sys.argv.index("--largura")
        try: largura = int(sys.argv[idx + 1])
        except (IndexError, ValueError): pass
    if "--minas" in sys.argv:
        idx = sys.argv.index("--minas")
        try: n_minas = int(sys.argv[idx + 1])
        except (IndexError, ValueError): pass
    if "--semente" in sys.argv:
        idx = sys.argv.index("--semente")
        try: semente = int(sys.argv[idx + 1])
        except (IndexError, ValueError): pass
    silencioso = "--silencioso" in sys.argv

    jogar(altura=altura, largura=largura, n_minas=n_minas,
          semente=semente, verbose=not silencioso)
