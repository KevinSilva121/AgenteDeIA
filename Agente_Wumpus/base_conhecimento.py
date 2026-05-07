"""
Base de Conhecimento (BC) do Agente Wumpus.

Armazena fatos observados e realiza inferencia logica proposicional
para classificar celulas como Segura, Possivel Poco, Possivel Wumpus
ou Perigo Confirmado.

Atomos logicos por celula (x,y):
  V(x,y)   - "esta celula foi visitada"
  S(x,y)   - "ha fedor nesta celula"   (observado)
  B(x,y)   - "ha brisa nesta celula"   (observado)
  W(x,y)   - "ha Wumpus nesta celula"  (a inferir)
  P(x,y)   - "ha Poco nesta celula"    (a inferir)
  OK(x,y)  - "esta celula e segura"    (a inferir)

Regras (slides classicos do AIMA):
  R1: ~S(x,y)  => ~W(a,b)  para todo (a,b) adjacente
  R2: ~B(x,y)  => ~P(a,b)  para todo (a,b) adjacente
  R3: S(x,y)   => W(adj1) v W(adj2) v ...   (Wumpus em algum adjacente)
  R4: B(x,y)   => P(adj1) v P(adj2) v ...   (Poco em algum adjacente)
  R5: ~W(x,y) ^ ~P(x,y)  => OK(x,y)
"""


class BaseConhecimento:
    def __init__(self, tamanho=4):
        self.tamanho = tamanho

        # Fatos observados (do que o agente sentiu)
        self.visitadas = set()
        self.com_fedor = set()
        self.sem_fedor = set()
        self.com_brisa = set()
        self.sem_brisa = set()

        # Conclusoes inferidas
        self.sem_wumpus = set()      # ~W(x,y) provado
        self.sem_poco = set()        # ~P(x,y) provado
        self.wumpus_confirmado = None  # (x,y) ou None
        self.poco_confirmado = set()
        self.wumpus_morto = False

        # [1,1] e sempre seguro pelas regras do mundo
        self.sem_wumpus.add((1, 1))
        self.sem_poco.add((1, 1))

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
        """Insere os fatos percebidos na BC."""
        self.visitadas.add(celula)
        # Se o agente esta na celula e sobreviveu, ela nao tem Wumpus nem Poco
        self.sem_wumpus.add(celula)
        self.sem_poco.add(celula)

        if percepcoes["fedor"]:
            self.com_fedor.add(celula)
        else:
            self.sem_fedor.add(celula)
        if percepcoes["brisa"]:
            self.com_brisa.add(celula)
        else:
            self.sem_brisa.add(celula)

    def registrar_wumpus_morto(self):
        self.wumpus_morto = True
        # Wumpus morto -> nao ha mais Wumpus em lugar nenhum
        for c in self.todas_celulas():
            self.sem_wumpus.add(c)

    # -------------------- Inferencia --------------------

    def inferir(self, log=None):
        """
        Aplica as regras logicas ate atingir um ponto fixo.
        Se 'log' e uma lista, registra os passos de raciocinio.
        """
        mudou = True
        while mudou:
            mudou = False

            # R1: nao ha fedor => nenhum vizinho tem Wumpus
            for c in self.sem_fedor:
                for v in self.adjacentes(c):
                    if v not in self.sem_wumpus:
                        self.sem_wumpus.add(v)
                        mudou = True
                        if log is not None:
                            log.append(
                                f"R1: nao senti fedor em {c}, logo nao ha Wumpus em {v}."
                            )

            # R2: nao ha brisa => nenhum vizinho tem Poco
            for c in self.sem_brisa:
                for v in self.adjacentes(c):
                    if v not in self.sem_poco:
                        self.sem_poco.add(v)
                        mudou = True
                        if log is not None:
                            log.append(
                                f"R2: nao senti brisa em {c}, logo nao ha Poco em {v}."
                            )

            # R3a: ha fedor em c => W em algum adjacente.
            #      Se ja eliminamos todos os adj exceto um, esse e o Wumpus.
            if not self.wumpus_morto and self.wumpus_confirmado is None:
                for c in self.com_fedor:
                    candidatos = [v for v in self.adjacentes(c)
                                  if v not in self.sem_wumpus]
                    if len(candidatos) == 1:
                        self.wumpus_confirmado = candidatos[0]
                        if log is not None:
                            log.append(
                                f"R3a: fedor em {c} e todos os outros vizinhos foram "
                                f"descartados -> Wumpus deve estar em {candidatos[0]}."
                            )
                        mudou = True
                        break

            # R3b: o Wumpus e unico. Se ha fedor em duas (ou mais) celulas
            #      diferentes, o Wumpus deve estar na interseccao dos candidatos.
            if (not self.wumpus_morto and self.wumpus_confirmado is None
                    and len(self.com_fedor) >= 2):
                interseccao = None
                for c in self.com_fedor:
                    cand = {v for v in self.adjacentes(c) if v not in self.sem_wumpus}
                    interseccao = cand if interseccao is None else interseccao & cand
                if interseccao is not None and len(interseccao) == 1:
                    (alvo,) = interseccao
                    self.wumpus_confirmado = alvo
                    if log is not None:
                        log.append(
                            f"R3b: fedor sentido em {sorted(self.com_fedor)} -> "
                            f"o Wumpus (unico) so pode estar na interseccao "
                            f"dos vizinhos = {alvo}."
                        )
                    mudou = True

            # Se sabemos onde e o Wumpus, todos os outros nao tem Wumpus
            if self.wumpus_confirmado is not None and not self.wumpus_morto:
                for cel in self.todas_celulas():
                    if cel != self.wumpus_confirmado and cel not in self.sem_wumpus:
                        self.sem_wumpus.add(cel)
                        mudou = True

            # R4: ha brisa em c => P em algum adjacente.
            #     Se sobrou apenas um candidato, e Poco confirmado.
            for c in self.com_brisa:
                candidatos = [v for v in self.adjacentes(c)
                              if v not in self.sem_poco]
                if len(candidatos) == 1:
                    poco = candidatos[0]
                    if poco not in self.poco_confirmado:
                        self.poco_confirmado.add(poco)
                        mudou = True
                        if log is not None:
                            log.append(
                                f"R4: brisa em {c} e todos os outros vizinhos descartados "
                                f"-> Poco confirmado em {poco}."
                            )

    # -------------------- Classificacao --------------------

    def deduzir_seguranca(self, celula):
        """
        Retorna o status logico da celula:
          'Segura'              - OK(celula) provado
          'Perigo Confirmado'   - W ou P provado
          'Possivel Wumpus'     - existe modelo em que ha Wumpus aqui
          'Possivel Poco'       - existe modelo em que ha Poco aqui
          'Possivel Wumpus/Poco'
        """
        if celula == self.wumpus_confirmado and not self.wumpus_morto:
            return "Perigo Confirmado (Wumpus)"
        if celula in self.poco_confirmado:
            return "Perigo Confirmado (Poco)"

        seguro_w = celula in self.sem_wumpus
        seguro_p = celula in self.sem_poco
        if seguro_w and seguro_p:
            return "Segura"

        if not seguro_w and not seguro_p:
            return "Possivel Wumpus/Poco"
        if not seguro_w:
            return "Possivel Wumpus"
        return "Possivel Poco"

    def eh_segura(self, celula):
        return self.deduzir_seguranca(celula) == "Segura"

    # -------------------- Apresentacao --------------------

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
