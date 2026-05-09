# -*- coding: utf-8 -*-
"""
Rede Neural Feedforward para o Dino AI.

Acoes de saida (4):
  0 = nada
  1 = pulo normal
  2 = pulo curto (pula e agacha logo em seguida, sai mais rapido do pulo)
  3 = agachar
"""

import numpy as np


def tanh(x):
    return np.tanh(x)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


class NeuralNetwork:
    """
    Arquitetura: INPUT_SIZE -> HIDDEN1 -> HIDDEN2 -> OUTPUT_SIZE
    Duas camadas ocultas para maior capacidade de representacao.
    """

    INPUT_SIZE  = 7    # [dist, obsW, obsH, speed, dinoY, obsType, is_jumping]
    HIDDEN1     = 16
    HIDDEN2     = 10
    OUTPUT_SIZE = 4    # nada, pulo normal, pulo curto, agachar

    def __init__(self, weights: np.ndarray = None):
        if weights is not None:
            self._load_weights(weights)
        else:
            # Xavier initialization para convergencia mais rapida
            self.W1 = np.random.randn(self.INPUT_SIZE, self.HIDDEN1) * np.sqrt(2.0 / self.INPUT_SIZE)
            self.b1 = np.zeros(self.HIDDEN1)
            self.W2 = np.random.randn(self.HIDDEN1, self.HIDDEN2) * np.sqrt(2.0 / self.HIDDEN1)
            self.b2 = np.zeros(self.HIDDEN2)
            self.W3 = np.random.randn(self.HIDDEN2, self.OUTPUT_SIZE) * np.sqrt(2.0 / self.HIDDEN2)
            self.b3 = np.zeros(self.OUTPUT_SIZE)

    # ------------------------------------------------------------------
    def forward(self, inputs: np.ndarray) -> int:
        """Propaga o estado do jogo e retorna a acao (0, 1, 2 ou 3)."""
        x  = np.array(inputs, dtype=float)
        h1 = tanh(x  @ self.W1 + self.b1)
        h2 = tanh(h1 @ self.W2 + self.b2)
        out = sigmoid(h2 @ self.W3 + self.b3)
        return int(np.argmax(out))

    # ------------------------------------------------------------------
    def get_weights(self) -> np.ndarray:
        """Retorna todos os pesos como vetor 1-D."""
        return np.concatenate([
            self.W1.flatten(), self.b1,
            self.W2.flatten(), self.b2,
            self.W3.flatten(), self.b3,
        ])

    def _load_weights(self, w: np.ndarray):
        idx = 0

        def _take(shape):
            nonlocal idx
            n = int(np.prod(shape))
            chunk = w[idx:idx + n].reshape(shape)
            idx += n
            return chunk

        self.W1 = _take((self.INPUT_SIZE,  self.HIDDEN1))
        self.b1 = _take((self.HIDDEN1,))
        self.W2 = _take((self.HIDDEN1,    self.HIDDEN2))
        self.b2 = _take((self.HIDDEN2,))
        self.W3 = _take((self.HIDDEN2,    self.OUTPUT_SIZE))
        self.b3 = _take((self.OUTPUT_SIZE,))

    @classmethod
    def total_weights(cls) -> int:
        return (cls.INPUT_SIZE * cls.HIDDEN1 + cls.HIDDEN1
                + cls.HIDDEN1  * cls.HIDDEN2 + cls.HIDDEN2
                + cls.HIDDEN2  * cls.OUTPUT_SIZE + cls.OUTPUT_SIZE)

    @classmethod
    def random(cls) -> "NeuralNetwork":
        """Cria individuo completamente aleatorio."""
        return cls()
