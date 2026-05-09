# 🦕 Dino AI — Redes Neurais + Algoritmos Genéticos

Sistema de inteligência artificial que aprende a jogar o jogo do dinossauro do Chrome
em **https://trex-runner.com/** usando **Redes Neurais Feedforward** evoluídas por um
**Algoritmo Genético**.

---

## 📁 Estrutura do Projeto

```
dino_ai/
├── main.py              # Ponto de entrada (treino / assistir)
├── neural_network.py    # Rede Neural Feedforward
├── genetic_algorithm.py # Algoritmo Genético (seleção, crossover, mutação)
├── game_controller.py   # Interface Selenium com o jogo
├── requirements.txt     # Dependências Python
└── best_dino.npy        # Melhor indivíduo salvo (gerado durante treino)
```

---

## 🧠 Arquitetura da IA

### Rede Neural
- **Entradas (6):** distância ao obstáculo, largura, altura, velocidade do jogo, posição Y do dino, tipo do obstáculo (cacto/pterodáctilo)
- **Camada Oculta:** 12 neurônios com ativação `tanh`
- **Saídas (3):** `nenhum`, `pular`, `agachar`

### Algoritmo Genético
| Parâmetro | Valor padrão |
|---|---|
| Tamanho da população | 30 |
| Taxa de mutação | 15% |
| Escala de mutação | 0.3 |
| Taxa de crossover | 80% |
| Elitismo | 10% |
| Seleção | Torneio (k=4) |

---

## 🚀 Como Usar

### 1. Instalar dependências
```bash
python -m pip install -r requirements.txt
```

### 2. Iniciar o treinamento
```bash
python main.py
```
O Chrome abrirá automaticamente com o jogo. A IA começa a jogar e evoluir a partir da geração 1.

### 3. Assistir o melhor indivíduo (após treinar)
```bash
python main.py --load
```

### 4. Treinar no modo headless (sem janela, mais rápido)
```bash
python main.py --headless
```

---

## 📊 Acompanhando o progresso

- O log de cada geração é salvo em `training_log.csv`
- O melhor indivíduo é salvo automaticamente em `best_dino.npy` após cada geração
- A IA considera "aprendida" quando atingir score ≥ 5000

---

## ⚙️ Requisitos

- Python 3.11+
- Google Chrome instalado
- Conexão com a internet (para acessar o jogo online)

O `webdriver-manager` baixa e instala o ChromeDriver automaticamente.

---

## 🔧 Customizações em `main.py`

| Constante | Descrição |
|---|---|
| `POPULATION_SIZE` | Qtd. de indivíduos por geração |
| `MAX_GENERATIONS` | Máx. de gerações (0 = infinito) |
| `STEP_DELAY` | Intervalo entre decisões (segundos) |
| `MAX_SCORE_TARGET` | Score alvo para encerrar o treino |

---

## 🎯 Como a IA aprende

1. **Geração 1:** 30 redes neurais com pesos aleatórios tentam jogar
2. **Seleção:** As melhores (maior score) têm mais chance de "reproduzir"  
3. **Crossover:** Genes (pesos) dos pais se misturam para criar filhos
4. **Mutação:** Pequenas variações aleatórias nos pesos evitam estagnação
5. **Elitismo:** Os top 10% sobrevivem intactos para a próxima geração
6. **Repetir** a partir do passo 2, gerando versões cada vez melhores
