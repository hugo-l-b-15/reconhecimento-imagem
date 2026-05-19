# ============================================================
#  game.py — Loop principal e gerenciamento de estados
# ============================================================

import math
import random
# pyrefly: ignore [missing-import]
import pygame
from settings import (
    SCREEN_W, SCREEN_H, FPS,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER,
    BLACK, WHITE, STAR_COLOR, STAR_COUNT,
    ASTEROID_SPAWN_INTERVAL, ASTEROID_MIN_INTERVAL,
    SCORE_SPEED_THRESHOLD, SPEED_INCREASE_FACTOR,
    NEON_YELLOW, NEON_CYAN, NEON_ORANGE, NEON_GREEN, NEON_RED
)
from player   import Player
from asteroid import Asteroid
from bullet   import Bullet
from hud      import HUD


# ── Partícula de explosão ────────────────────────────────────
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size")

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(1.5, 6.0)
        self.vx       = math.cos(angle) * speed
        self.vy       = math.sin(angle) * speed
        self.max_life = random.randint(18, 40)
        self.life     = self.max_life
        self.color    = color
        self.size     = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.12           # gravidade leve
        self.vx *= 0.97
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha  = int(255 * self.life / self.max_life)
        size   = max(1, int(self.size * self.life / self.max_life))
        r, g, b = self.color
        # círculo com alpha (via surface)
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, alpha), (size, size), size)
        surface.blit(s, (int(self.x) - size, int(self.y) - size))

    @property
    def is_dead(self):
        return self.life <= 0


# ── Estrelas do fundo ────────────────────────────────────────
def _generate_stars():
    return [
        (
            random.randint(0, SCREEN_W),
            random.randint(0, SCREEN_H),
            random.randint(1, 3),           # tamanho
            random.uniform(0.3, 1.0),       # brilho
        )
        for _ in range(STAR_COUNT)
    ]


class Game:
    """Gerencia estados, entidades e o loop principal do jogo."""

    def __init__(self, screen: pygame.Surface):
        self.screen   = screen
        self.clock    = pygame.time.Clock()
        self.hud      = HUD()
        self.stars    = _generate_stars()
        self.high_score = 0
        self._state   = STATE_MENU
        self._reset()

    # ── reset completo para nova partida ─────────────────────
    def _reset(self):
        self.player    = Player()
        self.asteroids: list[Asteroid] = []
        self.bullets:   list[Bullet]   = []
        self.particles: list[Particle] = []
        self.score     = 0
        self.level     = 1
        self._spawn_timer    = 0
        self._spawn_interval = ASTEROID_SPAWN_INTERVAL
        self._speed_mult     = 1.0
        self._flash_timer    = 0
        self._new_record     = False

    # ── loop principal ───────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self._handle_events()
            self._update()
            self._draw()
        pygame.quit()

    # ── eventos ──────────────────────────────────────────────
    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self._state == STATE_PLAYING:
                        self._state = STATE_MENU
                        self._reset()
                    else:
                        return False

                if self._state == STATE_MENU:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self._state = STATE_PLAYING
                        self._reset()

                elif self._state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self._state = STATE_PLAYING
                        self._reset()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self._state = STATE_MENU
                        self._reset()

        return True

    # ── atualização geral ────────────────────────────────────
    def _update(self):
        self.hud.update()

        if self._state != STATE_PLAYING:
            return

        # input da nave
        new_bullets = self.player.handle_input()
        self.bullets.extend(new_bullets)
        self.player.update()

        # projéteis
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if not b.is_off_screen()]

        # asteroides
        self._spawn_timer += 1
        if self._spawn_timer >= self._spawn_interval:
            self._spawn_timer = 0
            self.asteroids.append(Asteroid(speed_multiplier=self._speed_mult))

        for a in self.asteroids:
            a.update()

        # asteroides que saíram por baixo → game over
        for a in self.asteroids:
            if a.is_off_screen():
                self._trigger_game_over()
                return

        # colisão: bullet × asteroide
        to_remove_bullets    = set()
        to_remove_asteroids  = set()

        for bi, bullet in enumerate(self.bullets):
            for ai, asteroid in enumerate(self.asteroids):
                if asteroid.collides_with_rect(bullet.rect):
                    to_remove_bullets.add(bi)
                    to_remove_asteroids.add(ai)
                    self._explode(asteroid, bullet_hit=True)
                    self.score += asteroid.points_value
                    break

        self.bullets   = [b for i, b in enumerate(self.bullets)
                          if i not in to_remove_bullets]
        self.asteroids = [a for i, a in enumerate(self.asteroids)
                          if i not in to_remove_asteroids]

        # colisão: nave × asteroide
        if not self.player.is_invincible:
            for asteroid in self.asteroids:
                if asteroid.collides_with_rect(self.player.rect):
                    self._trigger_game_over()
                    return

        # partículas
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead]

        # flash
        if self._flash_timer > 0:
            self._flash_timer -= 1

        # dificuldade progressiva
        self._update_difficulty()

    def _update_difficulty(self):
        """Aumenta velocidade e frequência de spawn com o score."""
        level = max(1, self.score // SCORE_SPEED_THRESHOLD + 1)
        if level != self.level:
            self.level       = level
            self._speed_mult = 1.0 + (level - 1) * SPEED_INCREASE_FACTOR
            # reduz intervalo de spawn
            new_interval = max(
                ASTEROID_MIN_INTERVAL,
                ASTEROID_SPAWN_INTERVAL - (level - 1) * 3
            )
            self._spawn_interval = new_interval

    def _explode(self, asteroid: Asteroid, bullet_hit: bool = True):
        """Gera partículas de explosão e flash de tela."""
        cx, cy = asteroid.rect.center
        colors = [NEON_ORANGE, NEON_YELLOW, (255, 255, 200), (200, 100, 0)]
        num    = {"large": 22, "medium": 14, "small": 8}[asteroid.size_name]
        for _ in range(num):
            color = random.choice(colors)
            self.particles.append(Particle(cx, cy, color))
        self._flash_timer = 5 if bullet_hit else 10

    def _trigger_game_over(self):
        """Finaliza a partida."""
        if self.score > self.high_score:
            self.high_score = self.score
            self._new_record = True
        # gera explosão na posição da nave
        self._explode(
            type("_FakeAst", (), {
                "rect": self.player.rect,
                "size_name": "large"
            })(),
            bullet_hit=False
        )
        self._flash_timer = 15
        self._state = STATE_GAME_OVER

    # ── renderização ─────────────────────────────────────────
    def _draw(self):
        # fundo
        self.screen.fill(BLACK)
        self._draw_stars()

        if self._state == STATE_MENU:
            self.hud.draw_menu(self.screen)

        elif self._state == STATE_PLAYING:
            # entidades
            for a in self.asteroids:
                a.draw(self.screen)
            for b in self.bullets:
                b.draw(self.screen)
            for p in self.particles:
                p.draw(self.screen)
            self.player.draw(self.screen)
            # HUD
            self.hud.draw_score(self.screen, self.score, self.high_score)
            self.hud.draw_level(self.screen, self.level)
            self.hud.draw_flash(self.screen, self._flash_timer)

        elif self._state == STATE_GAME_OVER:
            for p in self.particles:
                p.draw(self.screen)
            self.hud.draw_game_over(
                self.screen, self.score, self.high_score, self._new_record
            )

        pygame.display.flip()

    def _draw_stars(self):
        """Desenha o fundo estrelado com brilho leve."""
        t = pygame.time.get_ticks() / 1000.0
        for x, y, size, brightness in self.stars:
            # twinkle suave
            flicker = 0.7 + 0.3 * math.sin(t * brightness * 2.5 + x)
            r = int(STAR_COLOR[0] * brightness * flicker)
            g = int(STAR_COLOR[1] * brightness * flicker)
            b = int(STAR_COLOR[2] * brightness * flicker)
            pygame.draw.circle(self.screen, (r, g, b), (x, y), size)
