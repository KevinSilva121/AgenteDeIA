"""
Ambiente do Mundo de Wumpus.

Grade 4x4 indexada de [1,1] (canto inferior esquerdo) a [4,4].
Contem: 1 Wumpus, varios Pocos e 1 Ouro.
A casa [1,1] e sempre segura (e a posicao inicial do agente).
"""

import random


class MundoWumpus:
    TAMANHO = 4

    def __init__(self, semente=None, prob_poco=0.2,
                 wumpus=None, ouro=None, pocos=None):
        """
        Cria o mundo. Se 'wumpus', 'ouro' ou 'pocos' forem informados,
        usa essas posicoes em vez do sorteio aleatorio.

        wumpus: tupla (x,y) ou None para sortear.
        ouro:   tupla (x,y) ou None para sortear.
        pocos:  iteravel de tuplas (x,y) ou None para sortear via prob_poco.
        """
        if semente is not None:
            random.seed(semente)

        self.tamanho = self.TAMANHO
        self.wumpus_vivo = True

        # Wumpus
        if wumpus is not None:
            self._validar_posicao(wumpus, "wumpus")
            if wumpus == (1, 1):
                raise ValueError("Wumpus nao pode estar em [1,1] (casa inicial).")
            self.wumpus = tuple(wumpus)
        else:
            self.wumpus = self._sortear_celula_excluindo([(1, 1)])

        # Ouro
        if ouro is not None:
            self._validar_posicao(ouro, "ouro")
            self.ouro = tuple(ouro)
        else:
            self.ouro = self._sortear_celula_excluindo([(1, 1)])

        # Pocos
        if pocos is not None:
            self.pocos = set()
            for p in pocos:
                self._validar_posicao(p, "poco")
                if p == (1, 1):
                    raise ValueError("Nao pode haver poco em [1,1] (casa inicial).")
                if p == self.wumpus:
                    raise ValueError(f"Poco {p} colide com posicao do Wumpus.")
                if p == self.ouro:
                    raise ValueError(f"Poco {p} colide com posicao do Ouro.")
                self.pocos.add(tuple(p))
        else:
            self.pocos = set()
            for x in range(1, self.tamanho + 1):
                for y in range(1, self.tamanho + 1):
                    if (x, y) == (1, 1):
                        continue
                    if (x, y) == self.wumpus or (x, y) == self.ouro:
                        continue
                    if random.random() < prob_poco:
                        self.pocos.add((x, y))

    def _validar_posicao(self, p, nome):
        if (not isinstance(p, (tuple, list)) or len(p) != 2
                or not all(isinstance(c, int) for c in p)):
            raise ValueError(f"Posicao invalida para {nome}: {p!r}")
        x, y = p
        if not (1 <= x <= self.tamanho and 1 <= y <= self.tamanho):
            raise ValueError(
                f"Posicao do {nome} {p} fora do mundo "
                f"(use coordenadas de 1 a {self.tamanho})."
            )

    def _sortear_celula_excluindo(self, excluir):
        while True:
            c = (random.randint(1, self.tamanho), random.randint(1, self.tamanho))
            if c not in excluir:
                return c

    def adjacentes(self, celula):
        x, y = celula
        vizinhos = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx <= self.tamanho and 1 <= ny <= self.tamanho:
                vizinhos.append((nx, ny))
        return vizinhos

    def perceber(self, celula):
        """Retorna os sensores ativos na celula: Fedor, Brisa, Brilho."""
        percepcoes = {
            "fedor": False,
            "brisa": False,
            "brilho": False,
        }
        if self.wumpus_vivo:
            for v in self.adjacentes(celula):
                if v == self.wumpus:
                    percepcoes["fedor"] = True
        for v in self.adjacentes(celula):
            if v in self.pocos:
                percepcoes["brisa"] = True
        if celula == self.ouro:
            percepcoes["brilho"] = True
        return percepcoes

    def eh_mortal(self, celula):
        """Pisar nesta celula mata o agente?"""
        if celula in self.pocos:
            return True
        if self.wumpus_vivo and celula == self.wumpus:
            return True
        return False

    def atirar_flecha(self, origem, direcao):
        """
        Dispara uma flecha desde 'origem' em uma direcao.
        direcao: (dx, dy) com um dos vetores unitarios.
        Retorna True se acertou o Wumpus (gerando um grito).
        """
        if not self.wumpus_vivo:
            return False
        x, y = origem
        dx, dy = direcao
        while True:
            x += dx
            y += dy
            if not (1 <= x <= self.tamanho and 1 <= y <= self.tamanho):
                return False
            if (x, y) == self.wumpus:
                self.wumpus_vivo = False
                return True

    def imprimir_mapa(self, agente_pos=None, revelar=True):
        """Imprime o mapa real (para debug). Origem [1,1] no canto inferior esquerdo."""
        print()
        print("  Mapa real do mundo (W=Wumpus, P=Poco, G=Ouro, A=Agente):")
        for y in range(self.tamanho, 0, -1):
            linha = f"  {y} |"
            for x in range(1, self.tamanho + 1):
                conteudo = []
                if agente_pos == (x, y):
                    conteudo.append("A")
                if revelar:
                    if (x, y) == self.wumpus and self.wumpus_vivo:
                        conteudo.append("W")
                    if (x, y) in self.pocos:
                        conteudo.append("P")
                    if (x, y) == self.ouro:
                        conteudo.append("G")
                celula = ",".join(conteudo) if conteudo else "."
                linha += f" {celula:^4}|"
            print(linha)
        print("     " + "  ".join(f" {x}  " for x in range(1, self.tamanho + 1)))
        print()
