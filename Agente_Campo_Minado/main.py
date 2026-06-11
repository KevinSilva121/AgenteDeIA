"""
Agente Logico para o Campo Minado (Aula 9 - Agentes Logicos).

MODELAGEM LOGICA PROPOSICIONAL:
    Cada celula (i,j) possui uma variavel proposicional M(i,j):
        M(i,j) = True  <=> ha mina em (i,j)
        M(i,j) = False <=> celula segura (NOT M(i,j))

    Quando uma celula com numero N e revelada, adicionamos sentencas
    logicas formais a Base de Conhecimento usando os operadores:
        AND, OR, NOT, IMPLIES, IFF (Bicondicional)

    Regras formalizadas:
        R1: contagem(i,j) == 0 IMPLIES (NOT M(v1) AND NOT M(v2) AND ...)
            "Se contagem e zero, todos vizinhos sao seguros"

        R2: contagem(i,j) == |vizinhos| IMPLIES (M(v1) AND M(v2) AND ...)
            "Se contagem igual ao numero de vizinhos, todos sao minas"

        R3: Restricao de contagem (exatamente N dos vizinhos sao minas)
            Usada para inferencia por subconjunto:
            Se S1 SUBSET S2, entao (S2 - S1) tem (count2 - count1) minas

        R4: NOT M(i,j) provado IMPLIES celula e segura
            M(i,j) provado IMPLIES celula e mina

INFERENCIA:
    - Modus Ponens: Se A e True, e (A IMPLIES B) na BC, entao B e True
    - Resolucao: Eliminacao de clausulas por subconjunto
    - Ponto fixo: Repete ate nenhuma nova inferencia ser possivel

ESTRATEGIA DO AGENTE:
    1) Joga em qualquer celula provadamente segura (NOT M(i,j) na BC).
    2) Se nenhuma e segura, escolhe a celula com MENOR probabilidade
       estimada de ser mina (heuristica estatistica).
"""

import random
import sys


# =====================================================================
# SENTENCAS LOGICAS PROPOSICIONAIS
# =====================================================================

class Sentenca:
    """Classe base abstrata para sentencas logicas proposicionais."""

    def avaliar(self, modelo):
        """Avalia a sentenca dado um modelo (dicionario simbolo -> bool)."""
        raise NotImplementedError

    def simbolos(self):
        """Retorna o conjunto de todos os simbolos atomicos na sentenca."""
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, self.__class__) and repr(self) == repr(other)

    def __hash__(self):
        return hash(repr(self))


class Simbolo(Sentenca):
    """Simbolo atomico proposicional (ex: M(1,2), S(3,4))."""

    def __init__(self, nome):
        self.nome = nome

    def avaliar(self, modelo):
        if self.nome in modelo:
            return modelo[self.nome]
        return None

    def simbolos(self):
        return {self.nome}

    def __repr__(self):
        return self.nome


class Not(Sentenca):
    """Negacao logica: NOT operando."""

    def __init__(self, operando):
        if not isinstance(operando, Sentenca):
            raise TypeError(f"NOT requer uma Sentenca, recebeu {type(operando)}")
        self.operando = operando

    def avaliar(self, modelo):
        val = self.operando.avaliar(modelo)
        if val is None:
            return None
        return not val

    def simbolos(self):
        return self.operando.simbolos()

    def __repr__(self):
        return f"NOT({self.operando})"


class And(Sentenca):
    """Conjuncao logica: operando1 AND operando2 AND ..."""

    def __init__(self, *operandos):
        for op in operandos:
            if not isinstance(op, Sentenca):
                raise TypeError(f"AND requer Sentencas, recebeu {type(op)}")
        self.operandos = list(operandos)

    def avaliar(self, modelo):
        resultados = [op.avaliar(modelo) for op in self.operandos]
        if any(r is False for r in resultados):
            return False
        if any(r is None for r in resultados):
            return None
        return True

    def simbolos(self):
        s = set()
        for op in self.operandos:
            s |= op.simbolos()
        return s

    def __repr__(self):
        return "(" + " AND ".join(repr(op) for op in self.operandos) + ")"


class Or(Sentenca):
    """Disjuncao logica: operando1 OR operando2 OR ..."""

    def __init__(self, *operandos):
        for op in operandos:
            if not isinstance(op, Sentenca):
                raise TypeError(f"OR requer Sentencas, recebeu {type(op)}")
        self.operandos = list(operandos)

    def avaliar(self, modelo):
        resultados = [op.avaliar(modelo) for op in self.operandos]
        if any(r is True for r in resultados):
            return True
        if any(r is None for r in resultados):
            return None
        return False

    def simbolos(self):
        s = set()
        for op in self.operandos:
            s |= op.simbolos()
        return s

    def __repr__(self):
        return "(" + " OR ".join(repr(op) for op in self.operandos) + ")"


class Implies(Sentenca):
    """Implicacao logica: antecedente IMPLIES consequente."""

    def __init__(self, antecedente, consequente):
        if not isinstance(antecedente, Sentenca):
            raise TypeError(f"IMPLIES requer Sentencas, recebeu {type(antecedente)}")
        if not isinstance(consequente, Sentenca):
            raise TypeError(f"IMPLIES requer Sentencas, recebeu {type(consequente)}")
        self.antecedente = antecedente
        self.consequente = consequente

    def avaliar(self, modelo):
        val_ant = self.antecedente.avaliar(modelo)
        val_con = self.consequente.avaliar(modelo)
        if val_ant is False:
            return True
        if val_con is True:
            return True
        if val_ant is True and val_con is False:
            return False
        return None

    def simbolos(self):
        return self.antecedente.simbolos() | self.consequente.simbolos()

    def __repr__(self):
        return f"({self.antecedente} IMPLIES {self.consequente})"


class Bicondicional(Sentenca):
    """Bicondicional logico: esquerda IFF direita (se e somente se)."""

    def __init__(self, esquerda, direita):
        if not isinstance(esquerda, Sentenca):
            raise TypeError(f"IFF requer Sentencas, recebeu {type(esquerda)}")
        if not isinstance(direita, Sentenca):
            raise TypeError(f"IFF requer Sentencas, recebeu {type(direita)}")
        self.esquerda = esquerda
        self.direita = direita

    def avaliar(self, modelo):
        val_e = self.esquerda.avaliar(modelo)
        val_d = self.direita.avaliar(modelo)
        if val_e is None or val_d is None:
            return None
        return val_e == val_d

    def simbolos(self):
        return self.esquerda.simbolos() | self.direita.simbolos()

    def __repr__(self):
        return f"({self.esquerda} IFF {self.direita})"


# =====================================================================
# RESTRICAO DE CONTAGEM (sentenca composta para regra de subconjunto)
# =====================================================================

class RestricaoContagem(Sentenca):
    """
    Sentenca logica composta: 'exatamente self.count das celulas em
    self.cells sao minas (M(i,j) = True)'.

    Internamente representa:
        (M(c1) OR M(c2) OR ...) com exatamente 'count' verdadeiros

    Quando count == 0:
        equivale a NOT M(c1) AND NOT M(c2) AND ... (todos seguros)
    Quando count == |cells|:
        equivale a M(c1) AND M(c2) AND ... (todos minas)

    Usada para inferencia por subconjunto (Resolucao).
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def avaliar(self, modelo):
        """Avalia se exatamente count celulas sao True no modelo."""
        verdadeiros = 0
        nao_definidos = 0
        for c in self.cells:
            nome = f"M({c[0]},{c[1]})"
            if nome in modelo:
                if modelo[nome]:
                    verdadeiros += 1
            else:
                nao_definidos += 1
        if nao_definidos > 0:
            return None
        return verdadeiros == self.count

    def simbolos(self):
        return {f"M({c[0]},{c[1]})" for c in self.cells}

    def como_sentenca_logica(self):
        """
        Converte a restricao de contagem para uma sentenca logica
        formal usando AND, OR, NOT quando possivel.

        count == 0:  NOT M(c1) AND NOT M(c2) AND ...
        count == |cells|: M(c1) AND M(c2) AND ...
        outros: retorna a representacao textual da restricao
        """
        simbolos = [Simbolo(f"M({c[0]},{c[1]})") for c in sorted(self.cells)]
        if self.count == 0:
            negs = [Not(s) for s in simbolos]
            return And(*negs) if len(negs) > 1 else negs[0] if negs else None
        if self.count == len(self.cells):
            return And(*simbolos) if len(simbolos) > 1 else simbolos[0] if simbolos else None
        return None  # Caso generico, nao reduzivel a AND/OR simples

    def __eq__(self, other):
        return (isinstance(other, RestricaoContagem)
                and self.cells == other.cells
                and self.count == other.count)

    def __hash__(self):
        return hash((frozenset(self.cells), self.count))

    def __str__(self):
        cells_str = ", ".join(f"M({c[0]},{c[1]})" for c in sorted(self.cells))
        if self.count == 0:
            negs = " AND ".join(f"NOT M({c[0]},{c[1]})" for c in sorted(self.cells))
            return f"({negs})"
        if self.count == len(self.cells):
            conjs = " AND ".join(f"M({c[0]},{c[1]})" for c in sorted(self.cells))
            return f"({conjs})"
        return f"ExatamenteN({{{cells_str}}}, {self.count})"

    def __repr__(self):
        return self.__str__()

    # ---- Inferencia local ----

    def known_mines(self):
        """
        R2: count == |cells| IMPLIES (M(c1) AND M(c2) AND ...)
        Se count == |cells|, todas as celulas sao minas.
        """
        if len(self.cells) == self.count and self.count > 0:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        R1: count == 0 IMPLIES (NOT M(c1) AND NOT M(c2) AND ...)
        Se count == 0, todas as celulas sao seguras.
        """
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Sabendo que M(cell) = True (mina provada):
            Remove cell do conjunto e decrementa count.
            Equivale a simplificar: (A AND B AND rest) com A=True => (B AND rest)
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Sabendo que NOT M(cell) (segura provada):
            Remove cell do conjunto (sem mudar count).
            Equivale a simplificar: (A OR rest) com A=False => (rest)
        """
        if cell in self.cells:
            self.cells.discard(cell)


# =====================================================================
# CLASSE MinesweeperAI (Agente Logico com Sentencas Proposicionais)
# =====================================================================

class MinesweeperAI:
    """
    Agente baseado em logica proposicional para o Campo Minado.

    A Base de Conhecimento (BC) armazena:
      - Sentencas logicas formais (AND, OR, NOT, IMPLIES)
      - Restricoes de contagem (que sao sentencas compostas)

    Inferencia usa:
      - Modus Ponens: Se A e (A IMPLIES B), entao B
      - Resolucao por subconjunto: Se S1 SUBSET S2, deriva nova restricao
      - Ponto fixo: Repete ate nenhuma conclusao nova
    """

    def __init__(self, altura=8, largura=8, verbose=True):
        self.altura = altura
        self.largura = largura
        self.verbose = verbose

        self.movimentos_feitos = set()
        self.mines = set()      # celulas provadas como mina: M(i,j) = True
        self.safes = set()      # celulas provadas como seguras: NOT M(i,j)
        self.knowledge = []     # restricoes de contagem (lista de RestricaoContagem)

        # Base de sentencas logicas formais (AND, OR, NOT, IMPLIES)
        self.sentencas_logicas = []

        # Cache de simbolos
        self._simbolos_cache = {}

    # -----------------------------------------------------------------
    # Fabrica de simbolos
    # -----------------------------------------------------------------

    def _simbolo(self, i, j):
        """Cria/recupera um Simbolo proposicional M(i,j)."""
        nome = f"M({i},{j})"
        if nome not in self._simbolos_cache:
            self._simbolos_cache[nome] = Simbolo(nome)
        return self._simbolos_cache[nome]

    def _adicionar_sentenca(self, sentenca, descricao=None):
        """Adiciona uma sentenca logica formal a BC."""
        self.sentencas_logicas.append(sentenca)
        if self.verbose and descricao:
            print(f"  [BC] {sentenca}  |  {descricao}")

    # -----------------------------------------------------------------
    # Marcacoes propagam para todas as sentencas
    # -----------------------------------------------------------------

    def mark_mine(self, cell):
        """
        Registra M(cell) = True na BC.
        Sentenca: M(i,j) (atomo verdadeiro)
        Propaga para todas as restricoes de contagem.
        """
        if cell not in self.mines:
            self.mines.add(cell)
            i, j = cell
            self._adicionar_sentenca(
                self._simbolo(i, j),
                f"M({i},{j}) e MINA [provado]"
            )
        for s in self.knowledge:
            s.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Registra NOT M(cell) na BC.
        Sentenca: NOT M(i,j)
        Propaga para todas as restricoes de contagem.
        """
        if cell not in self.safes:
            self.safes.add(cell)
            i, j = cell
            self._adicionar_sentenca(
                Not(self._simbolo(i, j)),
                f"NOT M({i},{j}) e SEGURA [provado]"
            )
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
        Chamado quando o ambiente revela `cell` com numero `count`.

        Constroi sentencas logicas formais:
          1) NOT M(cell) - celula revelada e segura
          2) Restricao de contagem com sentencas IMPLIES:
             - count == 0: Contagem(cell)==0 IMPLIES (NOT M(v1) AND NOT M(v2) AND ...)
             - count == |viz|: Contagem(cell)==|viz| IMPLIES (M(v1) AND M(v2) AND ...)
             - Geral: ExatamenteN({vizinhos_desconhecidos}, count_ajustado)
          3) Aplica inferencia ate ponto fixo
        """
        self.movimentos_feitos.add(cell)
        i, j = cell

        # Sentenca: NOT M(cell) - revelada, logo segura
        self.mark_safe(cell)

        # Construir restricao de contagem para os vizinhos
        viz = self.vizinhos(cell)
        novo_count = count
        novos_celulas = set()
        for v in viz:
            if v in self.mines:
                novo_count -= 1
            elif v not in self.safes:
                novos_celulas.add(v)

        if novos_celulas:
            restricao = RestricaoContagem(novos_celulas, novo_count)
            self.knowledge.append(restricao)

            # Adicionar a sentenca logica formal correspondente
            vizinhos_simb = [self._simbolo(vi, vj) for vi, vj in sorted(novos_celulas)]

            if novo_count == 0:
                # R1: Contagem == 0 IMPLIES (NOT M(v1) AND NOT M(v2) AND ...)
                negs = [Not(s) for s in vizinhos_simb]
                if len(negs) > 1:
                    consequente = And(*negs)
                else:
                    consequente = negs[0]
                regra = Implies(
                    Simbolo(f"Contagem({i},{j})==0"),
                    consequente
                )
                self._adicionar_sentenca(regra,
                    f"contagem {cell}=0 implica todos vizinhos seguros")
                self._adicionar_sentenca(Simbolo(f"Contagem({i},{j})==0"),
                    f"Fato: contagem de {cell} e 0")

            elif novo_count == len(novos_celulas):
                # R2: Contagem == |viz| IMPLIES (M(v1) AND M(v2) AND ...)
                if len(vizinhos_simb) > 1:
                    consequente = And(*vizinhos_simb)
                else:
                    consequente = vizinhos_simb[0]
                regra = Implies(
                    Simbolo(f"Contagem({i},{j})=={novo_count}"),
                    consequente
                )
                self._adicionar_sentenca(regra,
                    f"contagem {cell}={novo_count} implica todos vizinhos sao minas")
                self._adicionar_sentenca(Simbolo(f"Contagem({i},{j})=={novo_count}"),
                    f"Fato: contagem de {cell} e {novo_count}")

            else:
                # Caso geral: ExatamenteN({vizinhos}, count)
                # Adicionar como disjuncao: pelo menos um e mina
                if len(vizinhos_simb) > 1:
                    disjuncao = Or(*vizinhos_simb)
                else:
                    disjuncao = vizinhos_simb[0]
                regra = Implies(
                    Simbolo(f"Contagem({i},{j})>0"),
                    disjuncao
                )
                self._adicionar_sentenca(regra,
                    f"contagem {cell}={novo_count} implica algum vizinho e mina")
                self._adicionar_sentenca(Simbolo(f"Contagem({i},{j})>0"),
                    f"Fato: contagem de {cell} e {novo_count} (>0)")

                # E a restricao formal de que nao mais que count sao minas
                viz_str = ", ".join(f"M({vi},{vj})" for vi, vj in sorted(novos_celulas))
                self._adicionar_sentenca(
                    Simbolo(f"ExatamenteN({{{viz_str}}}, {novo_count})"),
                    f"Restricao: exatamente {novo_count} de {len(novos_celulas)} vizinhos sao minas"
                )

            self._log(f"Nova restricao por {cell}: {restricao}")

        # Inferencia ate ponto fixo
        self._inferir()

    def _inferir(self):
        """
        Aplica as regras de inferencia logica proposicional:

        R1: count == 0 IMPLIES (NOT M(v1) AND NOT M(v2) AND ...)
            "Se contagem e zero, nenhum vizinho e mina"
            => Modus Ponens: count==0 e True, logo NOT M(vi) para todos

        R2: count == |cells| IMPLIES (M(v1) AND M(v2) AND ...)
            "Se contagem igual ao numero de vizinhos, todos sao minas"
            => Modus Ponens: count==|cells| e True, logo M(vi) para todos

        R3: Resolucao por subconjunto:
            Se S1 SUBSET S2, entao:
              (S2 - S1) tem (count2 - count1) minas
            Equivale a resolver duas clausulas para eliminar variaveis comuns.

        Repete ate ponto fixo (nenhuma nova conclusao).
        """
        mudou = True
        while mudou:
            mudou = False

            # R1 e R2: extrai conclusoes diretas usando Modus Ponens
            minas_novas = set()
            seguras_novas = set()
            for restricao in self.knowledge:
                minas_novas |= restricao.known_mines()
                seguras_novas |= restricao.known_safes()

            for m in minas_novas:
                if m not in self.mines:
                    mi, mj = m
                    # Modus Ponens: restricao com count == |cells| e True
                    # Logo M(mi,mj) e True
                    self._log(
                        f"  >> R2 [Modus Ponens]: "
                        f"count == |cells| AND "
                        f"(count == |cells| IMPLIES M({mi},{mj})) "
                        f"=> M({mi},{mj})  [MINA]"
                    )
                    self.mark_mine(m)
                    mudou = True

            for s in seguras_novas:
                if s not in self.safes:
                    si, sj = s
                    # Modus Ponens: restricao com count == 0 e True
                    # Logo NOT M(si,sj) e True
                    self._log(
                        f"  >> R1 [Modus Ponens]: "
                        f"count == 0 AND "
                        f"(count == 0 IMPLIES NOT M({si},{sj})) "
                        f"=> NOT M({si},{sj})  [SEGURA]"
                    )
                    self.mark_safe(s)
                    mudou = True

            # Limpa restricoes vazias ou triviais
            self.knowledge = [s for s in self.knowledge if s.cells]

            # R3: Resolucao por subconjunto
            novas = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 is s2 or not s1.cells or not s2.cells:
                        continue
                    if s1.cells.issubset(s2.cells) and s1.cells != s2.cells:
                        nova = RestricaoContagem(s2.cells - s1.cells,
                                                 s2.count - s1.count)
                        if (nova not in self.knowledge
                                and nova not in novas
                                and nova.cells):
                            novas.append(nova)
                            # Log mostrando a resolucao com operadores logicos
                            self._log(
                                f"  >> R3 [Resolucao]: "
                                f"({s1}) AND ({s2})\n"
                                f"      S1 SUBSET S2 IMPLIES "
                                f"(S2 - S1) = nova restricao\n"
                                f"      => {nova}"
                            )
                            # Adicionar sentenca logica formal
                            self._adicionar_sentenca(
                                Simbolo(repr(nova)),
                                "Derivada por Resolucao de subconjunto"
                            )
            if novas:
                self.knowledge.extend(novas)
                mudou = True

    # -----------------------------------------------------------------
    # Funcao logica: checar_seguranca
    # -----------------------------------------------------------------

    def checar_seguranca(self, celula):
        """
        Determina o status logico de `celula` segundo a BC:
            'segura'        - NOT M(celula) provado na BC
                              (Modus Ponens derivou NOT M(i,j))
            'mina'          - M(celula) provado na BC
                              (Modus Ponens derivou M(i,j))
            'desconhecida'  - BC nao implica M(celula) nem NOT M(celula)

        Equivale a verificar:
            BC |= NOT M(celula)  => 'segura'
            BC |= M(celula)      => 'mina'
        """
        if celula in self.safes:
            return 'segura'
        if celula in self.mines:
            return 'mina'
        # Verificacao adicional via restricoes (forca a regra local)
        for restricao in self.knowledge:
            if celula in restricao.cells:
                if restricao.count == 0:
                    return 'segura'
                if restricao.count == len(restricao.cells):
                    return 'mina'
        return 'desconhecida'

    # -----------------------------------------------------------------
    # Decisao: jogada segura ou heuristica de risco
    # -----------------------------------------------------------------

    def jogada_segura(self):
        """
        Retorna uma celula onde NOT M(i,j) foi provado na BC.
        Ou seja, uma celula provadamente segura ainda nao jogada.
        """
        for c in self.safes:
            if c not in self.movimentos_feitos:
                return c
        return None

    def jogada_arriscada(self):
        """
        Heuristica: escolhe a celula desconhecida com MENOR probabilidade
        estimada de ser mina, baseada nas restricoes que a contem.

        Probabilidade local de M(c) = True em uma restricao {C}=k:
            P(M(c) | restricao) = k / |C|
        Tomamos o MAXIMO entre as restricoes (pior caso),
        e escolhemos a celula com o MENOR pior-caso.
        """
        candidatos = []
        for i in range(self.altura):
            for j in range(self.largura):
                c = (i, j)
                if c in self.movimentos_feitos or c in self.mines:
                    continue
                prob = 0.0
                for restricao in self.knowledge:
                    if c in restricao.cells and len(restricao.cells) > 0:
                        p_local = restricao.count / len(restricao.cells)
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
    # Apresentacao
    # -----------------------------------------------------------------

    def imprimir_sentencas(self):
        """Imprime todas as sentencas logicas formais da BC."""
        print(f"\n  === Base de Conhecimento - Sentencas Logicas ===")
        print(f"  Total de sentencas: {len(self.sentencas_logicas)}\n")
        for idx, s in enumerate(self.sentencas_logicas, 1):
            print(f"  [{idx:3d}] {s}")
        print()

    def imprimir_restricoes(self):
        """Imprime as restricoes de contagem ativas na BC."""
        print(f"\n  === Restricoes de Contagem Ativas ===")
        print(f"  Total: {len(self.knowledge)}\n")
        for idx, r in enumerate(self.knowledge, 1):
            print(f"  [{idx:3d}] {r}")
        print()

    def imprimir_resumo_logico(self):
        """Imprime um resumo das inferencias com operadores logicos."""
        print(f"\n  === Resumo Logico da BC ===")
        print(f"  Celulas reveladas: {len(self.movimentos_feitos)}")
        print(f"  Sentencas logicas: {len(self.sentencas_logicas)}")
        print(f"  Restricoes ativas: {len(self.knowledge)}")

        if self.safes:
            safe_str = " AND ".join(
                f"NOT M({c[0]},{c[1]})" for c in sorted(self.safes)
            )
            print(f"  Seguras (provado):  {safe_str}")

        if self.mines:
            mine_str = " AND ".join(
                f"M({c[0]},{c[1]})" for c in sorted(self.mines)
            )
            print(f"  Minas (provado):    {mine_str}")

        total = self.altura * self.largura
        desconhecidas = total - len(self.safes) - len(self.mines)
        print(f"  Desconhecidas:      {desconhecidas} celulas")
        print()

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

def jogar(altura=8, largura=8, n_minas=10, semente=None, verbose=True,
          mostrar_sentencas=False):
    # Primeiro clique sera no canto (0,0); evitamos mina la
    primeira = (0, 0)
    jogo = Minesweeper(altura, largura, n_minas, semente=semente,
                       primeira_celula=primeira)
    ai = MinesweeperAI(altura, largura, verbose=verbose)

    print("=" * 60)
    print(" Campo Minado - Agente Logico Proposicional")
    print(" Operadores: AND, OR, NOT, IMPLIES, IFF")
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
                si, sj = jogada
                print(f"Jogada SEGURA (BC |= NOT M({si},{sj})): {jogada}")
            else:
                print("Nenhuma celula provadamente segura "
                      "(BC nao implica NOT M(i,j) para nenhuma). "
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
            ai.imprimir_resumo_logico()
            if mostrar_sentencas:
                ai.imprimir_sentencas()
            return False

        n = jogo.contagem(jogada)
        jogo.reveladas.add(jogada)
        print(f"Revelado {jogada} -> contagem = {n}")
        ai.add_knowledge(jogada, n)

        imprimir_tabuleiro(jogo, ai)

        if jogo.venceu():
            print(f"\nVITORIA em {rodada} rodadas! Todas as casas seguras "
                  f"foram reveladas.")
            ai.imprimir_resumo_logico()
            if mostrar_sentencas:
                ai.imprimir_sentencas()
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
    mostrar_sentencas = "--sentencas" in sys.argv

    jogar(altura=altura, largura=largura, n_minas=n_minas,
          semente=semente, verbose=not silencioso,
          mostrar_sentencas=mostrar_sentencas)
