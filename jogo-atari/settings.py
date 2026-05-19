# ============================================================
#  settings.py — Constantes globais do jogo
# ============================================================

# ── Tela ────────────────────────────────────────────────────
SCREEN_W = 800
SCREEN_H = 600
FPS      = 60
TITLE    = "Asteroid Blaster — Atari Edition"

# ── Estados do jogo ─────────────────────────────────────────
STATE_MENU      = "menu"
STATE_PLAYING   = "playing"
STATE_GAME_OVER = "game_over"

# ── Paleta de cores (estilo Atari) ───────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
NEON_YELLOW  = (255, 255,  50)
NEON_GREEN   = ( 57, 255, 100)
NEON_ORANGE  = (255, 140,   0)
NEON_CYAN    = (  0, 230, 255)
NEON_RED     = (255,  50,  50)
GREY         = (160, 160, 160)
DARK_GREY    = ( 40,  40,  40)
STAR_COLOR   = (200, 200, 220)

# ── Nave (Player) ────────────────────────────────────────────
PLAYER_SPEED        = 6       # px / frame
PLAYER_SHOOT_COOLDOWN = 18    # frames entre disparos
PLAYER_WIDTH        = 40
PLAYER_HEIGHT       = 36

# ── Projétil (Bullet) ────────────────────────────────────────
BULLET_SPEED  = 12   # px / frame (sobe)
BULLET_W      = 4
BULLET_H      = 14

# ── Asteroides ───────────────────────────────────────────────
ASTEROID_BASE_SPEED      = 2.5   # px / frame
ASTEROID_SPAWN_INTERVAL  = 55    # frames entre spawns (inicial)
ASTEROID_MIN_INTERVAL    = 18    # intervalo mínimo (mais difícil)
ASTEROID_SPAWN_DECREASE  = 1     # reduz intervalo a cada N pontos

# Tamanhos: (raio_base, pontos_ao_destruir)
ASTEROID_SIZES = {
    "large":  (32, 10),
    "medium": (20,  5),
    "small":  (11,  2),
}

# ── Estrelas do fundo ────────────────────────────────────────
STAR_COUNT = 120

# ── Pontuação e dificuldade ──────────────────────────────────
SCORE_SPEED_THRESHOLD = 50   # a cada N pontos, velocidade aumenta
SPEED_INCREASE_FACTOR = 0.12  # quanto aumenta por threshold
