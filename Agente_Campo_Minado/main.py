"""
Agente Logico para o Campo Minado (Aula 9 - Agentes Logicos).

MODELAGEM LOGICA PROPOSICIONAL:
    Cada celula (i,j) possui uma variavel proposicional M(i,j):
        M(i,j) = True  <=> ha mina em (i,j)
        M(i,j) = False <=> celula segura (NOT M(i,j))

    Quando uma celula com numero N e revelada, o agente codifica a
    restricao "exatamente N dos vizinhos sao minas" em Forma Normal
    Conjuntiva (CNF) usando os operadores AND, OR e NOT:

        - "No maximo N": Para cada subconjunto S de tamanho N+1:
            (NOT M(s1) OR NOT M(s2) OR ... OR NOT M(s_{N+1}))
            "Em qualquer grupo de N+1 vizinhos, pelo menos um NAO e mina"

        - "No minimo N": Para cada subconjunto S de tamanho K-N+1:
            (M(s1) OR M(s2) OR ... OR M(s_{K-N+1}))
            "Em qualquer grupo de K-N+1 vizinhos, pelo menos um E mina"

    INFERENCIA:
        - Propagacao Unitaria (Unit Propagation):
            Se uma clausula (L1 OR L2 OR ... OR Ln) tem todos os literais
            avaliados como False exceto um Li, entao Li DEVE ser True.
            Isto e uma aplicacao direta de Modus Ponens sobre clausulas.

        - Resolucao por Subconjunto (regra derivada):
            Se restricao R1 envolve um subconjunto das celulas de R2,
            podemos derivar uma nova restricao para as celulas restantes.
            A nova restricao e convertida em clausulas CNF e adicionada a BC.

        - Ponto Fixo: Repete Propagacao + Resolucao ate nenhuma nova
          inferencia ser possivel.

    ESTRATEGIA DO AGENTE:
        1) Joga em qualquer celula provadamente segura (NOT M(i,j) na BC).
        2) Se nenhuma e segura, escolhe a com MENOR probabilidade estimada
           de ser mina (heuristica estatistica).
"""

import random
import sys
from itertools import combinations


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
    """Simbolo atomico proposicional (ex: M(1,2))."""

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
        return f"NOT {self.operando}"


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
# CODIFICACAO CNF PARA RESTRICOES DE CONTAGEM
# =====================================================================

def gerar_clausulas_cnf(simbolos, n):
    """
    Codifica "exatamente N dos simbolos sao verdadeiros" em CNF.

    Gera clausulas em duas partes:

    1) "No maximo N" (upper bound):
       Para cada subconjunto S de tamanho N+1:
           (NOT s1 OR NOT s2 OR ... OR NOT s_{N+1})
       Significado: em qualquer grupo de N+1, pelo menos um e False.

    2) "No minimo N" (lower bound):
       Para cada subconjunto S de tamanho K-N+1:
           (s1 OR s2 OR ... OR s_{K-N+1})
       Significado: em qualquer grupo de K-N+1, pelo menos um e True.

    Retorna lista de clausulas (Or de literais, ou literal unico).

    Exemplos:
        N=0, K=3: [(NOT A), (NOT B), (NOT C)]
            => Propagacao imediata: A=F, B=F, C=F

        N=3, K=3: [(A), (B), (C)]
            => Propagacao imediata: A=T, B=T, C=T

        N=1, K=3: [(NOT A OR NOT B), (NOT A OR NOT C),
                    (NOT B OR NOT C), (A OR B OR C)]
            => Se A=True: (NOT B OR NOT C) e duas clausulas satisfeitas
               e (A OR B OR C) satisfeita. Nenhuma propagacao imediata.
               Mas se tambem B=True: (NOT B OR NOT C) => NOT C => C=False
    """
    clausulas = []
    k = len(simbolos)

    if n < 0 or n > k:
        return clausulas

    # "No maximo N": em cada grupo de N+1, pelo menos um NAO e verdadeiro
    if n + 1 <= k:
        for subset in combinations(simbolos, n + 1):
            literais = [Not(s) for s in subset]
            if len(literais) == 1:
                clausulas.append(literais[0])
            else:
                clausulas.append(Or(*literais))

    # "No minimo N": em cada grupo de K-N+1, pelo menos um E verdadeiro
    if n > 0 and k - n + 1 <= k:
        for subset in combinations(simbolos, k - n + 1):
            literais = list(subset)
            if len(literais) == 1:
                clausulas.append(literais[0])
            else:
                clausulas.append(Or(*literais))

    return clausulas


# =====================================================================
# BASE DE CONHECIMENTO COM PROPAGACAO UNITARIA
# =====================================================================

class BaseConhecimento:
    """
    Base de Conhecimento em logica proposicional com clausulas CNF.

    Armazena:
        - clausulas: lista de clausulas CNF (Or/Not/Simbolo)
        - modelo: atribuicao parcial de valores (simbolo -> bool)

    Inferencia principal: Propagacao Unitaria (Unit Propagation)
        Se uma clausula (L1 OR ... OR Ln) tem n-1 literais False,
        o literal restante DEVE ser True para satisfazer a clausula.

        Isto e uma aplicacao direta do Modus Ponens:
        - Premissa 1: (L1 OR ... OR Ln) e verdadeira (clausula na BC)
        - Premissa 2: L1=F, ..., L_{n-1}=F (fatos no modelo)
        - Conclusao:  Ln=T (unica forma de satisfazer a clausula)
    """

    def __init__(self, verbose=True):
        self.clausulas = []
        self.modelo = {}
        self.verbose = verbose
        self._simbolos_cache = {}

    def simbolo(self, i, j):
        """Cria/recupera um Simbolo proposicional M(i,j)."""
        nome = f"M({i},{j})"
        if nome not in self._simbolos_cache:
            self._simbolos_cache[nome] = Simbolo(nome)
        return self._simbolos_cache[nome]

    def adicionar_clausulas(self, clausulas):
        """Adiciona clausulas CNF a BC (evita duplicatas)."""
        for c in clausulas:
            if c not in self.clausulas:
                self.clausulas.append(c)

    def propagar(self):
        """
        Propagacao Unitaria ate ponto fixo.

        Para cada clausula na BC:
            - Avalia cada literal usando avaliar() dos operadores OR e NOT
            - Se todos os literais sao False exceto um,
              esse literal e FORCADO a ser True

        Retorna lista de derivacoes: [(nome, valor, clausula_origem), ...]
        Cada derivacao representa uma nova atribuicao no modelo,
        derivada por Modus Ponens sobre a clausula.
        """
        derivacoes = []
        mudou = True

        while mudou:
            mudou = False
            for clausula in self.clausulas:
                resultado = self._tentar_propagar(clausula)
                if resultado is not None:
                    nome, valor = resultado
                    if nome not in self.modelo:
                        self.modelo[nome] = valor
                        derivacoes.append((nome, valor, clausula))
                        mudou = True

        return derivacoes

    def _tentar_propagar(self, clausula):
        """
        Tenta extrair uma atribuicao forcada de uma clausula.

        Tres casos:
        1. Clausula unitaria positiva (Simbolo s):
           s.avaliar(modelo) is None => s deve ser True

        2. Clausula unitaria negativa (Not(Simbolo s)):
           s.avaliar(modelo) is None => s deve ser False

        3. Clausula disjuntiva (Or(L1, ..., Ln)):
           Para cada Li, chama Li.avaliar(modelo):
             - Se algum Li e True => clausula satisfeita, nada a fazer
             - Se todos exceto um Li sao False => Li e forcado True
        """
        if isinstance(clausula, Simbolo):
            # Caso 1: clausula unitaria positiva
            if clausula.nome not in self.modelo:
                return (clausula.nome, True)

        elif isinstance(clausula, Not) and isinstance(clausula.operando, Simbolo):
            # Caso 2: clausula unitaria negativa
            nome = clausula.operando.nome
            if nome not in self.modelo:
                return (nome, False)

        elif isinstance(clausula, Or):
            # Caso 3: clausula disjuntiva - propagacao unitaria
            nao_resolvidos = []
            for literal in clausula.operandos:
                # Usa avaliar() do operador (NOT ou Simbolo)
                val = literal.avaliar(self.modelo)
                if val is True:
                    return None  # Clausula ja satisfeita
                if val is None:
                    nao_resolvidos.append(literal)

            # Se sobrou exatamente 1 literal nao-resolvido, ele e forcado
            if len(nao_resolvidos) == 1:
                lit = nao_resolvidos[0]
                if isinstance(lit, Simbolo):
                    return (lit.nome, True)
                elif isinstance(lit, Not) and isinstance(lit.operando, Simbolo):
                    return (lit.operando.nome, False)

        return None

    def clausulas_ativas(self):
        """Retorna clausulas que ainda nao foram satisfeitas pelo modelo."""
        return [c for c in self.clausulas if c.avaliar(self.modelo) is not True]

    def imprimir(self):
        """Imprime as clausulas CNF com seu status no modelo atual."""
        ativas = self.clausulas_ativas()
        print(f"\n  === Base de Conhecimento (CNF) ===")
        print(f"  Total de clausulas: {len(self.clausulas)} "
              f"({len(ativas)} ativas, "
              f"{len(self.clausulas) - len(ativas)} satisfeitas)")
        print(f"  Variaveis no modelo: {len(self.modelo)}\n")
        for idx, c in enumerate(self.clausulas, 1):
            val = c.avaliar(self.modelo)
            if val is True:
                marca = "SAT"
            elif val is None:
                marca = "???"
            else:
                marca = "!!!"
            print(f"  [{idx:3d}] [{marca}] {c}")
        print()


# =====================================================================
# RESTRICAO DE CONTAGEM (para Resolucao por Subconjunto)
# =====================================================================

class RestricaoContagem:
    """
    Representacao compacta: "exatamente count de cells sao minas".

    Usada para:
    1. Gerar clausulas CNF via gerar_clausulas_cnf()
    2. Resolucao por subconjunto: Se R1.cells SUBSET R2.cells,
       deriva nova restricao para (R2.cells - R1.cells)
       com count = R2.count - R1.count.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def gerar_clausulas(self, cache_simbolos):
        """Gera clausulas CNF para esta restricao."""
        simbolos = []
        for c in sorted(self.cells):
            nome = f"M({c[0]},{c[1]})"
            if nome not in cache_simbolos:
                cache_simbolos[nome] = Simbolo(nome)
            simbolos.append(cache_simbolos[nome])
        return gerar_clausulas_cnf(simbolos, self.count)

    def mark_mine(self, cell):
        """Simplifica: M(cell)=True provado, remove e decrementa count."""
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """Simplifica: NOT M(cell) provado, remove sem mudar count."""
        if cell in self.cells:
            self.cells.discard(cell)

    def __eq__(self, other):
        return (isinstance(other, RestricaoContagem)
                and self.cells == other.cells
                and self.count == other.count)

    def __hash__(self):
        return hash((frozenset(self.cells), self.count))

    def __repr__(self):
        cells_str = ", ".join(f"M({c[0]},{c[1]})" for c in sorted(self.cells))
        if self.count == 0:
            return "(" + " AND ".join(
                f"NOT M({c[0]},{c[1]})" for c in sorted(self.cells)) + ")"
        if self.count == len(self.cells):
            return "(" + " AND ".join(
                f"M({c[0]},{c[1]})" for c in sorted(self.cells)) + ")"
        return f"ExatamenteN({{{cells_str}}}, {self.count})"


# =====================================================================
# AGENTE LOGICO (MINESWEEPER AI)
# =====================================================================

class MinesweeperAI:
    """
    Agente baseado em logica proposicional para o Campo Minado.

    Inferencia REAL usando operadores logicos:
        1. Restricoes de contagem sao codificadas em clausulas CNF
           (usando AND, OR, NOT de verdade)
        2. Propagacao Unitaria avalia as clausulas com avaliar()
           dos operadores para derivar novos fatos
        3. Resolucao por Subconjunto gera novas restricoes que
           sao convertidas em clausulas CNF
        4. Ponto fixo: repete ate nenhuma inferencia nova
    """

    def __init__(self, altura=8, largura=8, verbose=True):
        self.altura = altura
        self.largura = largura
        self.verbose = verbose

        self.movimentos_feitos = set()
        self.mines = set()      # celulas provadas como mina: M(i,j) = True
        self.safes = set()      # celulas provadas como seguras: M(i,j) = False

        # Base de Conhecimento com clausulas CNF reais
        self.bc = BaseConhecimento(verbose=verbose)

        # Restricoes de contagem (para resolucao por subconjunto)
        self.restricoes = []

    # -----------------------------------------------------------------
    # Marcacoes (atualizam modelo, sets de conveniencia, e restricoes)
    # -----------------------------------------------------------------

    def mark_mine(self, cell):
        """
        Registra M(cell) = True no modelo da BC.
        Propaga para todas as restricoes de contagem.
        """
        if cell not in self.mines:
            self.mines.add(cell)
            nome = f"M({cell[0]},{cell[1]})"
            self.bc.modelo[nome] = True
            if self.verbose:
                print(f"  [FATO] {nome} = True  [MINA]")
            for r in self.restricoes:
                r.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Registra NOT M(cell) (M(cell) = False) no modelo da BC.
        Propaga para todas as restricoes de contagem.
        """
        if cell not in self.safes:
            self.safes.add(cell)
            nome = f"M({cell[0]},{cell[1]})"
            self.bc.modelo[nome] = False
            if self.verbose:
                print(f"  [FATO] {nome} = False [SEGURA]")
            for r in self.restricoes:
                r.mark_safe(cell)

    # -----------------------------------------------------------------
    # Vizinhos
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

    # -----------------------------------------------------------------
    # Adicionar conhecimento
    # -----------------------------------------------------------------

    def add_knowledge(self, cell, count):
        """
        Chamado quando o ambiente revela 'cell' com numero 'count'.

        1) Adiciona NOT M(cell) ao modelo (celula revelada e segura)
        2) Constroi restricao de contagem para vizinhos desconhecidos
        3) Codifica a restricao em clausulas CNF reais (usando OR, NOT)
        4) Aplica inferencia ate ponto fixo (Propagacao Unitaria + Resolucao)
        """
        self.movimentos_feitos.add(cell)
        i, j = cell

        # 1) Celula revelada e segura: NOT M(i,j)
        self.mark_safe(cell)

        # 2) Construir restricao para vizinhos desconhecidos
        viz = self.vizinhos(cell)
        novo_count = count
        novos_celulas = set()
        for v in viz:
            if v in self.mines:
                novo_count -= 1
            elif v not in self.safes:
                novos_celulas.add(v)

        if novos_celulas and 0 <= novo_count <= len(novos_celulas):
            restricao = RestricaoContagem(set(novos_celulas), novo_count)
            self.restricoes.append(restricao)

            # 3) Codificar em clausulas CNF e adicionar a BC
            clausulas = restricao.gerar_clausulas(self.bc._simbolos_cache)
            self.bc.adicionar_clausulas(clausulas)

            if self.verbose:
                vizinhos_str = ", ".join(
                    f"M({c[0]},{c[1]})" for c in sorted(novos_celulas))
                print(f"\n  [RESTRICAO] Celula ({i},{j}) com contagem {count}:")
                print(f"    ExatamenteN({{{vizinhos_str}}}, {novo_count})")
                print(f"    Codificada em {len(clausulas)} clausulas CNF:")
                for idx_c, c in enumerate(clausulas):
                    if idx_c < 8:
                        print(f"      {c}")
                    elif idx_c == 8:
                        print(f"      ... (+{len(clausulas) - 8} clausulas)")
                        break

        # 4) Inferencia ate ponto fixo
        self._inferir()

    # -----------------------------------------------------------------
    # Motor de Inferencia
    # -----------------------------------------------------------------

    def _inferir(self):
        """
        Aplica inferencia logica ate ponto fixo:

        Passo 1 - Propagacao Unitaria (sobre clausulas CNF):
            Para cada clausula (L1 OR ... OR Ln) na BC:
                - Avalia cada literal Li usando Li.avaliar(modelo)
                  (chama Or.avaliar, Not.avaliar, Simbolo.avaliar)
                - Se n-1 literais sao False, o restante e forcado True
            Isto e Modus Ponens aplicado sobre clausulas CNF.

        Passo 2 - Resolucao por Subconjunto:
            Se R1.cells SUBSET R2.cells, deriva:
                R3 = (R2.cells - R1.cells, R2.count - R1.count)
            Converte R3 em clausulas CNF e adiciona a BC.

        Repete ate nenhuma nova derivacao.
        """
        mudou = True
        while mudou:
            mudou = False

            # --- Passo 1: Propagacao Unitaria ---
            derivacoes = self.bc.propagar()
            if derivacoes:
                mudou = True
                for nome, valor, clausula in derivacoes:
                    coords = self._extrair_coords(nome)
                    if coords:
                        status = "MINA" if valor else "SEGURA"
                        if self.verbose:
                            print(f"  >> [Propagacao Unitaria]")
                            print(f"     Clausula: {clausula}")
                            print(f"     => {nome} = {valor} [{status}]")
                        if valor:
                            self.mines.add(coords)
                            for r in self.restricoes:
                                r.mark_mine(coords)
                        else:
                            self.safes.add(coords)
                            for r in self.restricoes:
                                r.mark_safe(coords)

            # Limpar restricoes vazias ou invalidas
            self.restricoes = [r for r in self.restricoes
                               if r.cells and 0 <= r.count <= len(r.cells)]

            # --- Passo 2: Resolucao por Subconjunto ---
            novas = []
            for s1 in self.restricoes:
                for s2 in self.restricoes:
                    if s1 is s2 or not s1.cells or not s2.cells:
                        continue
                    if s1.cells.issubset(s2.cells) and s1.cells != s2.cells:
                        novo_count = s2.count - s1.count
                        novas_cells = s2.cells - s1.cells
                        if novo_count < 0 or novo_count > len(novas_cells):
                            continue
                        nova = RestricaoContagem(novas_cells, novo_count)
                        if (nova not in self.restricoes
                                and nova not in novas
                                and nova.cells):
                            novas.append(nova)
                            # Gerar clausulas CNF para a restricao derivada
                            clausulas = nova.gerar_clausulas(
                                self.bc._simbolos_cache)
                            self.bc.adicionar_clausulas(clausulas)
                            if self.verbose:
                                print(f"  >> [Resolucao por Subconjunto]")
                                print(f"     {s1}")
                                print(f"     SUBSET")
                                print(f"     {s2}")
                                print(f"     => {nova}")
                                print(f"     (+{len(clausulas)} clausulas CNF)")

            if novas:
                self.restricoes.extend(novas)
                mudou = True

    def _extrair_coords(self, nome):
        """Extrai (i, j) de um nome 'M(i,j)'."""
        if nome.startswith("M(") and nome.endswith(")"):
            try:
                parts = nome[2:-1].split(",")
                return (int(parts[0]), int(parts[1]))
            except (ValueError, IndexError):
                pass
        return None

    # -----------------------------------------------------------------
    # Seguranca de uma celula
    # -----------------------------------------------------------------

    def checar_seguranca(self, celula):
        """
        Consulta o modelo da BC para determinar o status de 'celula':
            'segura'       - M(celula) = False no modelo (NOT M provado)
            'mina'         - M(celula) = True no modelo (M provado)
            'desconhecida' - M(celula) nao esta no modelo
        """
        nome = f"M({celula[0]},{celula[1]})"
        if nome in self.bc.modelo:
            return 'mina' if self.bc.modelo[nome] else 'segura'
        return 'desconhecida'

    # -----------------------------------------------------------------
    # Decisao de jogada
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
        estimada de ser mina.

        P_local(M(c) | restricao) = count / |cells|
        Toma o MAXIMO entre restricoes (pior caso) e escolhe o MENOR.
        """
        candidatos = []
        for i in range(self.altura):
            for j in range(self.largura):
                c = (i, j)
                if c in self.movimentos_feitos or c in self.mines:
                    continue
                prob = 0.0
                for restricao in self.restricoes:
                    if c in restricao.cells and len(restricao.cells) > 0:
                        p_local = restricao.count / len(restricao.cells)
                        if p_local > prob:
                            prob = p_local
                candidatos.append((prob, c))

        if not candidatos:
            return None

        candidatos.sort(key=lambda x: (x[0], x[1]))
        prob, escolhida = candidatos[0]
        if self.verbose:
            print(f"  >> [Heuristica] {escolhida} com prob. estimada "
                  f"{prob:.0%} de ser mina (menor entre desconhecidas).")
        return escolhida

    # -----------------------------------------------------------------
    # Apresentacao
    # -----------------------------------------------------------------

    def imprimir_bc(self):
        """Imprime as clausulas CNF da Base de Conhecimento."""
        self.bc.imprimir()

    def imprimir_resumo_logico(self):
        """Imprime um resumo das inferencias com operadores logicos."""
        ativas = self.bc.clausulas_ativas()
        print(f"\n  === Resumo Logico da BC ===")
        print(f"  Celulas reveladas:   {len(self.movimentos_feitos)}")
        print(f"  Clausulas CNF:       {len(self.bc.clausulas)} total, "
              f"{len(ativas)} ativas")
        print(f"  Restricoes ativas:   {len(self.restricoes)}")
        print(f"  Variaveis no modelo: {len(self.bc.modelo)}")

        if self.safes:
            safe_str = " AND ".join(
                f"NOT M({c[0]},{c[1]})" for c in sorted(self.safes))
            print(f"  Seguras (provado):   {safe_str}")

        if self.mines:
            mine_str = " AND ".join(
                f"M({c[0]},{c[1]})" for c in sorted(self.mines))
            print(f"  Minas (provado):     {mine_str}")

        total = self.altura * self.largura
        desconhecidas = total - len(self.safes) - len(self.mines)
        print(f"  Desconhecidas:       {desconhecidas} celulas")
        print()


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
          mostrar_bc=False):
    # Primeiro clique sera no canto (0,0); evitamos mina la
    primeira = (0, 0)
    jogo = Minesweeper(altura, largura, n_minas, semente=semente,
                       primeira_celula=primeira)
    ai = MinesweeperAI(altura, largura, verbose=verbose)

    print("=" * 60)
    print(" Campo Minado - Agente Logico Proposicional")
    print(" Inferencia: CNF + Propagacao Unitaria + Resolucao")
    print(" Operadores: AND, OR, NOT (usados na inferencia real)")
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
                print(f"Jogada SEGURA (modelo |= NOT M({si},{sj})): {jogada}")
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
            ai.imprimir_resumo_logico()
            if mostrar_bc:
                ai.imprimir_bc()
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
            if mostrar_bc:
                ai.imprimir_bc()
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
    mostrar_bc = "--bc" in sys.argv

    jogar(altura=altura, largura=largura, n_minas=n_minas,
          semente=semente, verbose=not silencioso,
          mostrar_bc=mostrar_bc)
