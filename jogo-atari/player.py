# ============================================================
#  player.py — Nave controlada pelo jogador
# ============================================================

import math
# pyrefly: ignore [missing-import]
import pygame
from settings import (
    SCREEN_W, SCREEN_H,
    PLAYER_SPEED, PLAYER_SHOOT_COOLDOWN,
    PLAYER_WIDTH, PLAYER_HEIGHT,
    WHITE, NEON_CYAN, NEON_YELLOW
)
from bullet import Bullet


class Player(pygame.sprite.Sprite):
    """Nave triangular do jogador; move-se horizontal e atira projéteis."""

    # polígono base (relativo ao centro, apontando para cima)
    _BASE_POLY = [
        (0,      -PLAYER_HEIGHT // 2),          # ponta do nariz
        (-PLAYER_WIDTH // 2,  PLAYER_HEIGHT // 2),  # asa esq.
        (0,       PLAYER_HEIGHT // 4),           # reentrância central
        ( PLAYER_WIDTH // 2,  PLAYER_HEIGHT // 2),  # asa dir.
    ]

    def __init__(self):
        super().__init__()
        self.image = self._build_surface()
        self.rect  = self.image.get_rect(
            midbottom=(SCREEN_W // 2, SCREEN_H - 20)
        )
        self.speed          = PLAYER_SPEED
        self._shoot_timer   = 0
        self._thruster_tick = 0
        self._invincible    = 0   # frames de invencibilidade (pós-hit)

    # ── construção da superfície ─────────────────────────────
    @staticmethod
    def _build_surface() -> pygame.Surface:
        w, h = PLAYER_WIDTH + 10, PLAYER_HEIGHT + 10
        surf  = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        # transladar o polígono para o centro da superfície
        poly = [(cx + px, cy + py) for px, py in Player._BASE_POLY]

        # sombra/brilho externo
        outer = [(cx + int(px * 1.15), cy + int(py * 1.15)) for px, py in Player._BASE_POLY]
        pygame.draw.polygon(surf, (*NEON_CYAN, 60), outer)

        # corpo principal
        pygame.draw.polygon(surf, WHITE, poly)
        # borda neon
        pygame.draw.polygon(surf, NEON_CYAN, poly, 2)
        return surf

    # ── ponto do canhão (topo da nave) ───────────────────────
    @property
    def gun_pos(self) -> tuple[int, int]:
        return (self.rect.centerx, self.rect.top + 4)

    # ── input e movimento ────────────────────────────────────
    def handle_input(self) -> list[Bullet]:
        """Processa teclas e retorna lista de novos projéteis (0 ou 1)."""
        keys   = pygame.key.get_pressed()
        new_bullets: list[Bullet] = []

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # clamp nas bordas horizontais
        self.rect.left  = max(0, self.rect.left)
        self.rect.right = min(SCREEN_W, self.rect.right)

        # tiro com cooldown
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self._shoot_timer == 0:
            new_bullets.append(Bullet(*self.gun_pos))
            self._shoot_timer = PLAYER_SHOOT_COOLDOWN

        return new_bullets

    # ── atualização por frame ────────────────────────────────
    def update(self):
        if self._shoot_timer > 0:
            self._shoot_timer -= 1
        if self._invincible > 0:
            self._invincible -= 1
        self._thruster_tick += 1

    # ── estado de invencibilidade (pós-colisão) ──────────────
    def hit(self):
        """Marca a nave como invencível por um curto período."""
        self._invincible = 40

    @property
    def is_invincible(self) -> bool:
        return self._invincible > 0

    # ── desenho ──────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        # pisca quando invencível
        if self._invincible > 0 and (self._invincible // 5) % 2 == 0:
            return

        surface.blit(self.image, self.rect)

        # chama do propulsor (triângulo laranja animado)
        self._draw_thruster(surface)

    def _draw_thruster(self, surface: pygame.Surface):
        tick   = self._thruster_tick
        flicker = math.sin(tick * 0.4)
        h_size  = int(6 + 6 * abs(flicker))
        cx      = self.rect.centerx
        base_y  = self.rect.bottom - 2

        thruster_poly = [
            (cx - 7, base_y),
            (cx + 7, base_y),
            (cx,     base_y + h_size),
        ]
        color = (255, int(100 + 100 * abs(flicker)), 0, 200)
        thruster_surf = pygame.Surface(
            (SCREEN_W, SCREEN_H), pygame.SRCALPHA
        )
        pygame.draw.polygon(thruster_surf, color, thruster_poly)
        surface.blit(thruster_surf, (0, 0))
