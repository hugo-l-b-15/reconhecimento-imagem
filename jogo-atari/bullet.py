# ============================================================
#  bullet.py — Projétil disparado pela nave
# ============================================================

# pyrefly: ignore [missing-import]
import pygame
from settings import (
    BULLET_SPEED, BULLET_W, BULLET_H,
    NEON_YELLOW, NEON_CYAN, WHITE
)


class Bullet(pygame.sprite.Sprite):
    """Projétil que se move para cima a partir da posição da nave."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = self._build_surface()
        self.rect  = self.image.get_rect(midbottom=(x, y))
        self.speed = BULLET_SPEED
        # contador para efeito de pulso
        self._tick = 0

    # ── construção da superfície ─────────────────────────────
    @staticmethod
    def _build_surface() -> pygame.Surface:
        surf = pygame.Surface((BULLET_W, BULLET_H), pygame.SRCALPHA)
        # núcleo branco
        pygame.draw.rect(surf, WHITE,      (1, 2, BULLET_W - 2, BULLET_H - 4))
        # borda neon
        pygame.draw.rect(surf, NEON_YELLOW, (0, 0, BULLET_W, BULLET_H), 1)
        return surf

    # ── atualização por frame ────────────────────────────────
    def update(self):
        self.rect.y -= self.speed
        self._tick  += 1

    # ── verificação de saída da tela ─────────────────────────
    def is_off_screen(self) -> bool:
        return self.rect.bottom < 0

    # ── desenho com brilho ───────────────────────────────────
    def draw(self, surface: pygame.Surface):
        # halo suave ao redor do projétil
        glow_rect = self.rect.inflate(6, 6)
        glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        alpha = 60 + int(40 * abs(__import__("math").sin(self._tick * 0.3)))
        pygame.draw.rect(
            glow_surf, (*NEON_CYAN, alpha),
            (0, 0, *glow_rect.size), border_radius=3
        )
        surface.blit(glow_surf, glow_rect.topleft)
        surface.blit(self.image, self.rect)
