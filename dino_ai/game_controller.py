# -*- coding: utf-8 -*-
"""
GameController: Interface Selenium com https://trex-runner.com/

Acoes disponiveis (4):
  0 = nada
  1 = pulo normal
  2 = pulo curto (pula + agacha imediatamente = sai do pulo mais rapido!)
  3 = agachar
"""

import time
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys


# ---------------------------------------------------------------------------
# JavaScript injetado para expor o estado interno do jogo
# ---------------------------------------------------------------------------
JS_INJECT = """
(function() {
    if (window.__dinoPatched) return;
    window.__dinoPatched = true;

    const origGameOver = Runner.prototype.gameOver;
    Runner.prototype.gameOver = function() {
        window.__dinoDead = true;
        origGameOver.call(this);
    };

    window.getDinoState = function() {
        const r = Runner.instance_;
        if (!r) return null;

        const dino  = r.tRex;
        const obs   = (r.horizon && r.horizon.obstacles) ? r.horizon.obstacles : [];
        const speed = r.currentSpeed || 0;
        const score = r.distanceMeter
            ? r.distanceMeter.getActualDistance(r.distanceRan) : 0;

        // Obstaculo mais proximo a frente
        let dist = 9999, obsW = 0, obsH = 0, obsType = 0;
        for (let i = 0; i < obs.length; i++) {
            const o = obs[i];
            const right = o.xPos + o.typeConfig.width;
            if (right > dino.xPos) {
                dist    = o.xPos - dino.xPos - dino.config.WIDTH;
                obsW    = o.typeConfig.width;
                obsH    = o.typeConfig.height;
                obsType = o.typeConfig.type === 'PTERODACTYL' ? 1 : 0;
                break;
            }
        }

        // Estado do pulo
        const isJumping = dino.jumping ? 1 : 0;

        return {
            dist:      dist,
            obsW:      obsW,
            obsH:      obsH,
            obsType:   obsType,
            speed:     speed,
            dinoY:     dino.yPos,
            isJumping: isJumping,
            score:     score,
            dead:      window.__dinoDead || false
        };
    };

    window.dinoRestart = function() {
        window.__dinoDead = false;
        Runner.instance_.restart();
    };

    // Dispara keydown simulado
    window.dinoKeyDown = function(code) {
        document.dispatchEvent(new KeyboardEvent('keydown', {keyCode: code, which: code, bubbles: true}));
    };
    window.dinoKeyUp = function(code) {
        document.dispatchEvent(new KeyboardEvent('keyup', {keyCode: code, which: code, bubbles: true}));
    };
})();
"""

JS_GET_STATE = "return window.getDinoState();"
JS_RESTART   = "window.dinoRestart();"
JS_JUMP      = "window.dinoKeyDown(32);"       # SPACE = 32
JS_DOWN_ON   = "window.dinoKeyDown(40);"       # ARROW_DOWN = 40
JS_DOWN_OFF  = "window.dinoKeyUp(40);"


# ---------------------------------------------------------------------------
# Layout automatico de janelas para N instancias
# ---------------------------------------------------------------------------
def compute_window_geometry(index: int, total: int,
                             screen_w: int = 1920,
                             screen_h: int = 1020) -> dict:
    cols = min(total, 3)
    rows = (total + cols - 1) // cols
    w    = screen_w // cols
    h    = screen_h // rows
    col  = index % cols
    row  = index // cols
    return {"x": col * w, "y": row * h, "width": w, "height": h}


class GameController:
    GAME_URL = "https://trex-runner.com/"

    # Delay em segundos entre pressionar JUMP e pressionar DOWN no pulo curto
    SHORT_JUMP_DELAY = 0.06   # ~60ms — suficiente para subir, depois truncar

    def __init__(self, headless: bool = False,
                 window_index: int = 0, total_windows: int = 1):
        self.window_index  = window_index
        self.total_windows = total_windows
        self.is_ducking    = False  # estado interno de agachar

        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--disable-infobars")
        opts.add_argument("--mute-audio")
        opts.add_argument("--log-level=3")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_experimental_option("excludeSwitches", ["enable-logging"])

        geo = compute_window_geometry(window_index, total_windows)
        opts.add_argument(f"--window-size={geo['width']},{geo['height']}")
        opts.add_argument(f"--window-position={geo['x']},{geo['y']}")

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=opts)
        except Exception:
            self.driver = webdriver.Chrome(options=opts)

        self.driver.get(self.GAME_URL)
        time.sleep(3)

        self.driver.execute_script(JS_INJECT)
        time.sleep(0.3)

        # Inicia o jogo com primeira tecla
        self._js(JS_JUMP)
        time.sleep(0.6)

    # ------------------------------------------------------------------
    # Helpers de JS
    # ------------------------------------------------------------------
    def _js(self, script: str):
        try:
            self.driver.execute_script(script)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Acoes (4 tipos)
    # ------------------------------------------------------------------
    def jump(self):
        """Pulo normal — arco completo."""
        if self.is_ducking:
            self._js(JS_DOWN_OFF)
            self.is_ducking = False
        self._js(JS_JUMP)

    def short_jump(self):
        """
        Pulo curto: pressiona SPACE e logo em seguida DOWN.
        O dinossauro sai do pulo bem mais rapido, util para obstaculos baixos
        ou quando precisa pousar rapido antes do proximo obstaculo.
        """
        if self.is_ducking:
            self._js(JS_DOWN_OFF)
            self.is_ducking = False
        self._js(JS_JUMP)
        time.sleep(self.SHORT_JUMP_DELAY)
        self._js(JS_DOWN_ON)
        self.is_ducking = True   # sera solto no proximo passo se necessario

    def duck(self):
        """Agachar — entra em modo duck."""
        if not self.is_ducking:
            self._js(JS_DOWN_ON)
            self.is_ducking = True

    def release_duck(self):
        """Solta o agachar."""
        if self.is_ducking:
            self._js(JS_DOWN_OFF)
            self.is_ducking = False

    def do_nothing(self):
        """Nenhuma acao. Garante que duck foi solto."""
        if self.is_ducking:
            self.release_duck()

    # ------------------------------------------------------------------
    # Estado do jogo
    # ------------------------------------------------------------------
    def get_state(self) -> dict | None:
        try:
            return self.driver.execute_script(JS_GET_STATE)
        except Exception:
            return None

    def is_dead(self) -> bool:
        state = self.get_state()
        return True if state is None else bool(state.get("dead", False))

    def get_score(self) -> float:
        state = self.get_state()
        return 0.0 if state is None else float(state.get("score", 0))

    # ------------------------------------------------------------------
    # Converte estado em vetor normalizado para a rede neural (7 features)
    # ------------------------------------------------------------------
    def state_to_inputs(self, state: dict) -> np.ndarray:
        """
        Features normalizadas:
          [dist_norm, obsW_norm, obsH_norm, speed_norm, dinoY_norm, obsType, is_jumping]
        """
        if state is None:
            return np.zeros(7)

        dist      = np.clip(state.get("dist",      1000), 0, 1000) / 1000.0
        obs_w     = np.clip(state.get("obsW",       200), 0,  200) / 200.0
        obs_h     = np.clip(state.get("obsH",       200), 0,  200) / 200.0
        speed     = np.clip(state.get("speed",         0), 0,   25) /  25.0
        dino_y    = np.clip(state.get("dinoY",        93), 0,  200) / 200.0
        obs_type  = float(state.get("obsType",  0))
        is_jumping = float(state.get("isJumping", 0))

        return np.array([dist, obs_w, obs_h, speed, dino_y, obs_type, is_jumping])

    # ------------------------------------------------------------------
    # Reinicia a partida
    # ------------------------------------------------------------------
    def restart(self):
        self.is_ducking = False
        try:
            self.driver.execute_script(JS_RESTART)
        except Exception:
            self._js(JS_JUMP)
        time.sleep(0.2)

    # ------------------------------------------------------------------
    # Fecha o browser
    # ------------------------------------------------------------------
    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass
