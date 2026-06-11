"""
Agente Baseado em Conhecimento para o Mundo de Wumpus.

Ciclo do agente:
  1) Percebe a celula atual (Fedor / Brisa / Brilho).
  2) Atualiza a Base de Conhecimento.
  3) Aplica inferencia logica.
  4) Decide a acao:
       - Pegar ouro se houver Brilho.
       - Voltar para [1,1] e sair se ja tem o ouro.
       - Atirar a flecha se souber onde esta o Wumpus e ele estiver no caminho.
       - Mover-se para uma celula provada Segura ainda nao visitada.
       - Se nao houver opcao segura, o agente para (preserva a vida).
"""

from collections import deque

from base_conhecimento import BaseConhecimento


class AgenteWumpus:
    def __init__(self, mundo, verbose=True):
        self.mundo = mundo
        self.bc = BaseConhecimento(tamanho=mundo.tamanho)
        self.posicao = (1, 1)
        self.tem_ouro = False
        self.tem_flecha = True
        self.vivo = True
        self.venceu = False
        self.passos = 0
        self.verbose = verbose
        # Direcao atual (vetor unitario): inicia olhando para a direita
        self.direcao = (1, 0)

    # -------------------- Loop principal --------------------

    def jogar(self, max_passos=60):
        self._log(f"=== Inicio: agente em {self.posicao} ===")
        while self.vivo and not self.venceu and self.passos < max_passos:
            self.passos += 1
            self._log(f"\n--- Passo {self.passos} | Posicao {self.posicao} ---")

            percepcoes = self.mundo.perceber(self.posicao)
            self._log(f"Percepcoes: {self._fmt_percepcoes(percepcoes)}")
            self.bc.registrar_percepcao(self.posicao, percepcoes)

            log_inferencia = []
            self.bc.inferir(log=log_inferencia)
            for linha in log_inferencia:
                self._log(f"  > {linha}")

            # 1) Pegar ouro
            if percepcoes["brilho"] and not self.tem_ouro:
                self._log("Vejo o brilho! Pegando o ouro.")
                self.tem_ouro = True

            # 2) Sair com o ouro
            if self.tem_ouro and self.posicao == (1, 1):
                self._log("Estou de volta a [1,1] com o ouro. SAIR. VITORIA!")
                self.venceu = True
                break

            # 3) Decidir acao
            acao = self._escolher_acao()
            if acao is None:
                self._log("Nao consigo provar nenhuma acao segura. Parando.")
                break
            self._executar(acao)

        if self.verbose:
            print()
            self.bc.imprimir_mapa_inferido(self.posicao)
            self.bc.imprimir_resumo_logico()
        return self.venceu

    # -------------------- Decisao --------------------

    def _escolher_acao(self):
        """
        Retorna uma tupla descrevendo a acao:
          ("mover", destino)
          ("atirar", direcao)
        ou None se nao houver acao segura.
        """
        # Se ja peguei o ouro, planejar caminho seguro de volta a [1,1]
        if self.tem_ouro:
            caminho = self._caminho_seguro_ate(self.posicao, (1, 1))
            if caminho and len(caminho) >= 2:
                return ("mover", caminho[1])
            # sem caminho seguro: nao arriscar
            return None

        # Procurar uma celula adjacente segura ainda nao visitada
        for v in self.bc.adjacentes(self.posicao):
            if v not in self.bc.visitadas and self.bc.eh_segura(v):
                return ("mover", v)

        # Procurar QUALQUER celula segura nao visitada e ir ate la por celulas seguras
        alvos_seguros = [c for c in self.bc.todas_celulas()
                         if c not in self.bc.visitadas and self.bc.eh_segura(c)]
        for alvo in alvos_seguros:
            caminho = self._caminho_seguro_ate(self.posicao, alvo)
            if caminho and len(caminho) >= 2:
                return ("mover", caminho[1])

        # Tentar usar a flecha se sabemos onde esta o Wumpus
        if (self.tem_flecha and self.bc.wumpus_confirmado is not None
                and not self.bc.wumpus_morto):
            direcao = self._direcao_para_atirar(self.bc.wumpus_confirmado)
            if direcao is not None:
                return ("atirar", direcao)

        return None

    def _direcao_para_atirar(self, alvo):
        """
        Retorna o vetor (dx,dy) para atirar a flecha contra 'alvo'
        a partir da posicao atual, se estao alinhados horizontal/verticalmente.
        """
        ax, ay = self.posicao
        wx, wy = alvo
        if ax == wx:
            return (0, 1) if wy > ay else (0, -1)
        if ay == wy:
            return (1, 0) if wx > ax else (-1, 0)
        return None

    def _caminho_seguro_ate(self, origem, destino):
        """BFS por celulas provadas seguras (visitadas tambem sao seguras)."""
        if origem == destino:
            return [origem]
        fila = deque([origem])
        veio_de = {origem: None}
        while fila:
            atual = fila.popleft()
            if atual == destino:
                # reconstroi
                caminho = []
                while atual is not None:
                    caminho.append(atual)
                    atual = veio_de[atual]
                return list(reversed(caminho))
            for v in self.bc.adjacentes(atual):
                if v in veio_de:
                    continue
                if v == destino or self.bc.eh_segura(v) or v in self.bc.visitadas:
                    veio_de[v] = atual
                    fila.append(v)
        return None

    # -------------------- Execucao --------------------

    def _executar(self, acao):
        tipo, dado = acao
        if tipo == "mover":
            destino = dado
            self._log(f"Acao: mover de {self.posicao} para {destino} "
                      f"(deduzido como {self.bc.deduzir_seguranca(destino)}).")
            dx = destino[0] - self.posicao[0]
            dy = destino[1] - self.posicao[1]
            self.direcao = (dx, dy)
            self.posicao = destino
            if self.mundo.eh_mortal(destino):
                self.vivo = False
                self._log(f"O agente morreu em {destino}!")
        elif tipo == "atirar":
            direcao = dado
            self._log(f"Acao: atirar a flecha em {self.posicao} na direcao {direcao}.")
            self.tem_flecha = False
            acertou = self.mundo.atirar_flecha(self.posicao, direcao)
            if acertou:
                self._log("OUVI UM GRITO! O Wumpus foi morto.")
                self.bc.registrar_wumpus_morto()
            else:
                self._log("A flecha se perdeu. Wumpus nao estava nessa direcao.")

    # -------------------- Apresentacao --------------------

    def _fmt_percepcoes(self, p):
        ativos = [k for k, v in p.items() if v]
        return ", ".join(ativos) if ativos else "nenhuma"

    def _log(self, msg):
        if self.verbose:
            print(msg)
