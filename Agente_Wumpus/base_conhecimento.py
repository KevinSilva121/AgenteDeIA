"""
Base de Conhecimento (BC) do Agente Wumpus - Logica Proposicional.

Implementa sentencas logicas com operadores AND, OR, NOT, IMPLIES
e BICONDICIONAL para raciocinio formal no Mundo de Wumpus.

Atomos logicos por celula (x,y):
  V(x,y)   - "esta celula foi visitada"
  S(x,y)   - "ha fedor nesta celula"   (observado)
  B(x,y)   - "ha brisa nesta celula"   (observado)
  W(x,y)   - "ha Wumpus nesta celula"  (a inferir)
  P(x,y)   - "ha Poco nesta celula"    (a inferir)
  OK(x,y)  - "esta celula e segura"    (a inferir)

Regras formalizadas como sentencas logicas:
  R1: NOT S(x,y) IMPLIES (NOT W(a,b) AND NOT W(c,d) AND ...)
      "Se nao ha fedor, entao nenhum vizinho tem Wumpus"

  R2: NOT B(x,y) IMPLIES (NOT P(a,b) AND NOT P(c,d) AND ...)
      "Se nao ha brisa, entao nenhum vizinho tem Poco"

  R3: S(x,y) IMPLIES (W(a,b) OR W(c,d) OR ...)
      "Se ha fedor, entao o Wumpus esta em algum vizinho"

  R4: B(x,y) IMPLIES (P(a,b) OR P(c,d) OR ...)
      "Se ha brisa, entao ha Poco em algum vizinho"

  R5: (NOT W(x,y) AND NOT P(x,y)) IMPLIES OK(x,y)
      "Se nao ha Wumpus nem Poco, a celula e segura"
"""


# ======================== SENTENCAS LOGICAS ========================

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
    """Simbolo atomico proposicional (ex: W(1,2), S(3,4))."""

    def __init__(self, nome):
        self.nome = nome

    def avaliar(self, modelo):
        if self.nome in modelo:
            return modelo[self.nome]
        # Simbolo sem valor atribuido -> nao pode avaliar
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
        # A -> B equivale a NOT A OR B
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


# ======================== BASE DE CONHECIMENTO ========================

class BaseConhecimento:
    """
    Base de conhecimento proposicional para o Mundo de Wumpus.

    Armazena sentencas logicas e realiza inferencia por enumeracao
    de modelos (model checking) para determinar se uma sentenca
    e consequencia logica (entailment) da base.
    """

    def __init__(self, tamanho=4):
        self.tamanho = tamanho

        # Base de sentencas logicas (lista de sentencas que sao verdadeiras)
        self.sentencas = []

        # Cache de simbolos proposicionais para acesso rapido
        self._simbolos_cache = {}

        # Fatos observados (para consulta rapida pelo agente)
        self.visitadas = set()
        self.com_fedor = set()
        self.sem_fedor = set()
        self.com_brisa = set()
        self.sem_brisa = set()

        # Conclusoes inferidas (cache de resultados para eficiencia)
        self.sem_wumpus = set()
        self.sem_poco = set()
        self.wumpus_confirmado = None
        self.poco_confirmado = set()
        self.wumpus_morto = False

        # [1,1] e sempre seguro pelas regras do mundo
        self.sem_wumpus.add((1, 1))
        self.sem_poco.add((1, 1))

        # Adicionar fato inicial: NOT W(1,1) AND NOT P(1,1)
        self._adicionar_sentenca(Not(self._simbolo("W", 1, 1)))
        self._adicionar_sentenca(Not(self._simbolo("P", 1, 1)))
        self._adicionar_sentenca(self._simbolo("OK", 1, 1))

    # -------------------- Fabrica de simbolos --------------------

    def _simbolo(self, tipo, x, y):
        """Cria/recupera um Simbolo proposicional. Ex: _simbolo('W', 3, 2) -> W(3,2)."""
        nome = f"{tipo}({x},{y})"
        if nome not in self._simbolos_cache:
            self._simbolos_cache[nome] = Simbolo(nome)
        return self._simbolos_cache[nome]

    def _adicionar_sentenca(self, sentenca, log=None, descricao=None):
        """Adiciona uma sentenca a base de conhecimento."""
        self.sentencas.append(sentenca)
        if log is not None and descricao is not None:
            log.append(f"  Sentenca adicionada: {sentenca}  |  {descricao}")

    # -------------------- Utilitarios --------------------

    def adjacentes(self, celula):
        x, y = celula
        viz = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= self.tamanho and 1 <= ny <= self.tamanho:
                viz.append((nx, ny))
        return viz

    def todas_celulas(self):
        return [(x, y) for x in range(1, self.tamanho + 1)
                for y in range(1, self.tamanho + 1)]

    # -------------------- Atualizacao --------------------

    def registrar_percepcao(self, celula, percepcoes):
        """
        Insere fatos percebidos como sentencas logicas na BC.

        Constroi sentencas com AND, OR, NOT, IMPLIES baseadas
        nas percepcoes do agente na celula atual.
        """
        x, y = celula
        self.visitadas.add(celula)

        # Se o agente esta vivo na celula, ela nao tem Wumpus nem Poco
        # Sentenca: NOT W(x,y) AND NOT P(x,y)
        self.sem_wumpus.add(celula)
        self.sem_poco.add(celula)
        self._adicionar_sentenca(Not(self._simbolo("W", x, y)))
        self._adicionar_sentenca(Not(self._simbolo("P", x, y)))
        self._adicionar_sentenca(self._simbolo("V", x, y))

        vizinhos = self.adjacentes(celula)

        if percepcoes["fedor"]:
            self.com_fedor.add(celula)
            # Sentenca: S(x,y) = True
            self._adicionar_sentenca(self._simbolo("S", x, y))

            # R3: S(x,y) IMPLIES (W(v1) OR W(v2) OR ...)
            # "Ha fedor, logo o Wumpus esta em algum dos vizinhos"
            simbolos_w = [self._simbolo("W", vx, vy) for vx, vy in vizinhos]
            if simbolos_w:
                disjuncao = Or(*simbolos_w) if len(simbolos_w) > 1 else simbolos_w[0]
                regra = Implies(self._simbolo("S", x, y), disjuncao)
                self._adicionar_sentenca(regra)

        else:
            self.sem_fedor.add(celula)
            # Sentenca: NOT S(x,y) = True
            self._adicionar_sentenca(Not(self._simbolo("S", x, y)))

            # R1: NOT S(x,y) IMPLIES (NOT W(v1) AND NOT W(v2) AND ...)
            # "Sem fedor, logo nenhum vizinho tem Wumpus"
            negs = [Not(self._simbolo("W", vx, vy)) for vx, vy in vizinhos]
            if negs:
                conjuncao = And(*negs) if len(negs) > 1 else negs[0]
                regra = Implies(Not(self._simbolo("S", x, y)), conjuncao)
                self._adicionar_sentenca(regra)

        if percepcoes["brisa"]:
            self.com_brisa.add(celula)
            # Sentenca: B(x,y) = True
            self._adicionar_sentenca(self._simbolo("B", x, y))

            # R4: B(x,y) IMPLIES (P(v1) OR P(v2) OR ...)
            # "Ha brisa, logo ha Poco em algum dos vizinhos"
            simbolos_p = [self._simbolo("P", vx, vy) for vx, vy in vizinhos]
            if simbolos_p:
                disjuncao = Or(*simbolos_p) if len(simbolos_p) > 1 else simbolos_p[0]
                regra = Implies(self._simbolo("B", x, y), disjuncao)
                self._adicionar_sentenca(regra)

        else:
            self.sem_brisa.add(celula)
            # Sentenca: NOT B(x,y) = True
            self._adicionar_sentenca(Not(self._simbolo("B", x, y)))

            # R2: NOT B(x,y) IMPLIES (NOT P(v1) AND NOT P(v2) AND ...)
            # "Sem brisa, logo nenhum vizinho tem Poco"
            negs = [Not(self._simbolo("P", vx, vy)) for vx, vy in vizinhos]
            if negs:
                conjuncao = And(*negs) if len(negs) > 1 else negs[0]
                regra = Implies(Not(self._simbolo("B", x, y)), conjuncao)
                self._adicionar_sentenca(regra)

        # R5: (NOT W(x,y) AND NOT P(x,y)) IMPLIES OK(x,y)
        # "Se nao ha Wumpus nem Poco, a celula e segura"
        regra_ok = Implies(
            And(Not(self._simbolo("W", x, y)), Not(self._simbolo("P", x, y))),
            self._simbolo("OK", x, y)
        )
        self._adicionar_sentenca(regra_ok)

    def registrar_wumpus_morto(self):
        """Registra que o Wumpus foi morto com sentencas NOT W(x,y) para todas celulas."""
        self.wumpus_morto = True
        for c in self.todas_celulas():
            x, y = c
            self.sem_wumpus.add(c)
            self._adicionar_sentenca(Not(self._simbolo("W", x, y)))

    # -------------------- Inferencia Logica --------------------

    def _consultar(self, consulta_simbolo):
        """
        Verifica se a base de conhecimento implica logicamente (entails)
        a sentenca de consulta usando enumeracao de modelos (model checking).

        KB |= alpha  <=>  em todo modelo que satisfaz KB, alpha tambem e verdade.

        Para eficiencia, limita os simbolos relevantes aqueles presentes
        nas sentencas que envolvem os simbolos da consulta.
        """
        # Coletar simbolos relevantes (apenas os que aparecem nas sentencas
        # que compartilham simbolos com a consulta)
        simbolos_consulta = consulta_simbolo.simbolos()
        simbolos_relevantes = set(simbolos_consulta)
        for s in self.sentencas:
            simbs = s.simbolos()
            if simbs & simbolos_consulta:
                simbolos_relevantes |= simbs

        simbolos_lista = sorted(simbolos_relevantes)
        return self._verificar_entailment(simbolos_lista, {}, consulta_simbolo)

    def _verificar_entailment(self, simbolos, modelo, consulta):
        """
        Enumeracao recursiva de modelos (algoritmo TT-Entails do AIMA).

        Para cada combinacao de valores True/False dos simbolos:
          - Se o modelo satisfaz TODAS as sentencas da BC (KB e True),
            entao verifica se a consulta tambem e True.
          - Se existir algum modelo onde KB e True mas consulta e False,
            entao KB NAO implica a consulta.
        """
        if not simbolos:
            # Todos os simbolos atribuidos - verificar o modelo
            # Verificar se a KB e satisfeita neste modelo
            kb_verdadeira = all(
                s.avaliar(modelo) is True for s in self.sentencas
                if s.simbolos().issubset(set(modelo.keys()))
            )
            if kb_verdadeira:
                resultado = consulta.avaliar(modelo)
                return resultado is True
            # Se a KB nao e satisfeita, este modelo nao importa (True vacuamente)
            return True

        primeiro = simbolos[0]
        resto = simbolos[1:]

        # Tenta True e False para este simbolo
        modelo_true = {**modelo, primeiro: True}
        modelo_false = {**modelo, primeiro: False}

        return (self._verificar_entailment(resto, modelo_true, consulta) and
                self._verificar_entailment(resto, modelo_false, consulta))

    def inferir(self, log=None):
        """
        Aplica inferencia logica proposicional usando as sentencas da BC.

        Utiliza as sentencas com operadores AND, OR, NOT, IMPLIES para
        deduzir novos fatos sobre o mundo.

        Se 'log' e uma lista, registra os passos de raciocinio mostrando
        as sentencas logicas envolvidas.
        """
        mudou = True
        while mudou:
            mudou = False

            # R1: Inferir NOT W(v) a partir de sentencas NOT S(x,y) IMPLIES NOT W(vizinhos)
            for c in list(self.sem_fedor):
                for v in self.adjacentes(c):
                    if v not in self.sem_wumpus:
                        # Consulta: KB |= NOT W(v)?
                        # A regra NOT S(c) IMPLIES NOT W(v) combinada com NOT S(c) = True
                        # resulta em NOT W(v) por Modus Ponens
                        vx, vy = v
                        cx, cy = c
                        self.sem_wumpus.add(v)
                        self._adicionar_sentenca(Not(self._simbolo("W", vx, vy)))
                        mudou = True
                        if log is not None:
                            log.append(
                                f"R1: NOT S({cx},{cy}) AND "
                                f"(NOT S({cx},{cy}) IMPLIES NOT W({vx},{vy})) "
                                f"=> NOT W({vx},{vy})  [Modus Ponens]"
                            )

            # R2: Inferir NOT P(v) a partir de sentencas NOT B(x,y) IMPLIES NOT P(vizinhos)
            for c in list(self.sem_brisa):
                for v in self.adjacentes(c):
                    if v not in self.sem_poco:
                        vx, vy = v
                        cx, cy = c
                        self.sem_poco.add(v)
                        self._adicionar_sentenca(Not(self._simbolo("P", vx, vy)))
                        mudou = True
                        if log is not None:
                            log.append(
                                f"R2: NOT B({cx},{cy}) AND "
                                f"(NOT B({cx},{cy}) IMPLIES NOT P({vx},{vy})) "
                                f"=> NOT P({vx},{vy})  [Modus Ponens]"
                            )

            # R3a: Wumpus por eliminacao
            # S(c) IMPLIES (W(v1) OR W(v2) OR ...)
            # Se NOT W(v2), NOT W(v3), ..., entao W(v1)  [Resolucao unitaria]
            if not self.wumpus_morto and self.wumpus_confirmado is None:
                for c in self.com_fedor:
                    candidatos = [v for v in self.adjacentes(c)
                                  if v not in self.sem_wumpus]
                    if len(candidatos) == 1:
                        alvo = candidatos[0]
                        ax, ay = alvo
                        cx, cy = c
                        self.wumpus_confirmado = alvo
                        self._adicionar_sentenca(self._simbolo("W", ax, ay))

                        # Mostrar a cadeia de raciocinio logico
                        vizinhos = self.adjacentes(c)
                        eliminados = [v for v in vizinhos if v in self.sem_wumpus]
                        if log is not None:
                            elim_str = " AND ".join(
                                f"NOT W({ex},{ey})" for ex, ey in eliminados
                            )
                            viz_str = " OR ".join(
                                f"W({vx},{vy})" for vx, vy in vizinhos
                            )
                            log.append(
                                f"R3a: S({cx},{cy}) IMPLIES ({viz_str})\n"
                                f"      {elim_str}\n"
                                f"      => W({ax},{ay})  "
                                f"[Resolucao: eliminados todos exceto um]"
                            )
                        mudou = True
                        break

            # R3b: Wumpus por interseccao de clausulas disjuntivas
            # Se S(c1) IMPLIES (W(a) OR W(b)) AND S(c2) IMPLIES (W(b) OR W(c))
            # e a interseccao dos candidatos tem tamanho 1, Wumpus esta la
            if (not self.wumpus_morto and self.wumpus_confirmado is None
                    and len(self.com_fedor) >= 2):
                interseccao = None
                clausulas_str = []
                for c in self.com_fedor:
                    cx, cy = c
                    cand = {v for v in self.adjacentes(c) if v not in self.sem_wumpus}
                    cand_str = " OR ".join(f"W({vx},{vy})" for vx, vy in sorted(cand))
                    clausulas_str.append(f"S({cx},{cy}) IMPLIES ({cand_str})")
                    interseccao = cand if interseccao is None else interseccao & cand
                if interseccao is not None and len(interseccao) == 1:
                    (alvo,) = interseccao
                    ax, ay = alvo
                    self.wumpus_confirmado = alvo
                    self._adicionar_sentenca(self._simbolo("W", ax, ay))
                    if log is not None:
                        sentencas_log = "\n      AND ".join(clausulas_str)
                        log.append(
                            f"R3b: {sentencas_log}\n"
                            f"      => Interseccao dos candidatos = {{W({ax},{ay})}}\n"
                            f"      => W({ax},{ay})  "
                            f"[Resolucao por interseccao de clausulas]"
                        )
                    mudou = True

            # Se sabemos onde e o Wumpus (unicidade): W(alvo) IMPLIES NOT W(outros)
            if self.wumpus_confirmado is not None and not self.wumpus_morto:
                wx, wy = self.wumpus_confirmado
                for cel in self.todas_celulas():
                    if cel != self.wumpus_confirmado and cel not in self.sem_wumpus:
                        cx, cy = cel
                        self.sem_wumpus.add(cel)
                        self._adicionar_sentenca(Not(self._simbolo("W", cx, cy)))
                        mudou = True
                        if log is not None:
                            log.append(
                                f"R3c: W({wx},{wy}) AND (unicidade do Wumpus) "
                                f"IMPLIES NOT W({cx},{cy})"
                            )

            # R4: Poco por eliminacao
            # B(c) IMPLIES (P(v1) OR P(v2) OR ...)
            # Se NOT P(v2), NOT P(v3)..., entao P(v1)  [Resolucao unitaria]
            for c in self.com_brisa:
                candidatos = [v for v in self.adjacentes(c)
                              if v not in self.sem_poco]
                if len(candidatos) == 1:
                    poco = candidatos[0]
                    if poco not in self.poco_confirmado:
                        px, py = poco
                        cx, cy = c
                        self.poco_confirmado.add(poco)
                        self._adicionar_sentenca(self._simbolo("P", px, py))

                        vizinhos = self.adjacentes(c)
                        eliminados = [v for v in vizinhos if v in self.sem_poco]
                        if log is not None:
                            elim_str = " AND ".join(
                                f"NOT P({ex},{ey})" for ex, ey in eliminados
                            )
                            viz_str = " OR ".join(
                                f"P({vx},{vy})" for vx, vy in vizinhos
                            )
                            log.append(
                                f"R4: B({cx},{cy}) IMPLIES ({viz_str})\n"
                                f"     {elim_str}\n"
                                f"     => P({px},{py})  "
                                f"[Resolucao: eliminados todos exceto um]"
                            )
                        mudou = True

    # -------------------- Classificacao --------------------

    def deduzir_seguranca(self, celula):
        """
        Retorna o status logico da celula usando inferencia proposicional.

        Verifica as sentencas:
          - W(x,y) confirmado => 'Perigo Confirmado (Wumpus)'
          - P(x,y) confirmado => 'Perigo Confirmado (Poco)'
          - NOT W(x,y) AND NOT P(x,y) => 'Segura' (via R5)
          - Caso contrario, classifica como Possivel ameaca
        """
        x, y = celula

        if celula == self.wumpus_confirmado and not self.wumpus_morto:
            return "Perigo Confirmado (Wumpus)"
        if celula in self.poco_confirmado:
            return "Perigo Confirmado (Poco)"

        # R5: (NOT W(x,y) AND NOT P(x,y)) IMPLIES OK(x,y)
        seguro_w = celula in self.sem_wumpus  # NOT W(x,y) provado
        seguro_p = celula in self.sem_poco    # NOT P(x,y) provado

        if seguro_w and seguro_p:
            return "Segura"

        if not seguro_w and not seguro_p:
            return "Possivel Wumpus/Poco"
        if not seguro_w:
            return "Possivel Wumpus"
        return "Possivel Poco"

    def eh_segura(self, celula):
        """Verifica se NOT W(celula) AND NOT P(celula) esta na BC."""
        return self.deduzir_seguranca(celula) == "Segura"

    # -------------------- Apresentacao --------------------

    def imprimir_sentencas(self):
        """Imprime todas as sentencas logicas da base de conhecimento."""
        print("\n  === Base de Conhecimento - Sentencas Logicas ===")
        print(f"  Total de sentencas: {len(self.sentencas)}\n")
        for i, s in enumerate(self.sentencas, 1):
            print(f"  [{i:3d}] {s}")
        print()

    def imprimir_mapa_inferido(self, posicao_agente=None):
        """Mostra o mapa de acordo com o que o agente sabe."""
        print("  Mapa inferido pelo agente:")
        print("    OK = Segura | ?? = Desconhecida | W! = Wumpus confirmado")
        print("    P! = Poco confirmado | .V = Visitada")
        for y in range(self.tamanho, 0, -1):
            linha = f"  {y} |"
            for x in range(1, self.tamanho + 1):
                c = (x, y)
                if posicao_agente == c:
                    marca = "A"
                elif c == self.wumpus_confirmado and not self.wumpus_morto:
                    marca = "W!"
                elif c in self.poco_confirmado:
                    marca = "P!"
                elif c in self.visitadas:
                    marca = ".V"
                elif c in self.sem_wumpus and c in self.sem_poco:
                    marca = "OK"
                else:
                    marca = "??"
                linha += f" {marca:^4}|"
            print(linha)
        print("     " + "  ".join(f" {x}  " for x in range(1, self.tamanho + 1)))

    def imprimir_resumo_logico(self):
        """Imprime um resumo das inferencias feitas com operadores logicos."""
        print("\n  === Resumo Logico ===")
        print(f"  Celulas visitadas: {sorted(self.visitadas)}")

        if self.sem_wumpus:
            nw = " AND ".join(f"NOT W{c}" for c in sorted(self.sem_wumpus))
            print(f"  Sem Wumpus (provado): {nw}")

        if self.sem_poco:
            np_ = " AND ".join(f"NOT P{c}" for c in sorted(self.sem_poco))
            print(f"  Sem Poco (provado):   {np_}")

        if self.wumpus_confirmado:
            print(f"  Wumpus confirmado:    W{self.wumpus_confirmado} = True")
        if self.poco_confirmado:
            pc = " AND ".join(f"P{c}" for c in sorted(self.poco_confirmado))
            print(f"  Poco confirmado:      {pc}")

        seguras = [c for c in self.todas_celulas() if self.eh_segura(c)]
        if seguras:
            ok = " AND ".join(f"OK{c}" for c in seguras)
            print(f"  Celulas seguras:      {ok}")
        print()
