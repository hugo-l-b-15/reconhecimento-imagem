# ============================================================
#  asteroid.py — Asteroide que cai do topo da tela
# ============================================================

import math
import random
# pyrefly: ignore [missing-import]
import pygame
from settings import (
    SCREEN_W, SCREEN_H,
    ASTEROID_BASE_SPEED, ASTEROID_SIZES,
    NEON_ORANGE, GREY, WHITE
)


def _random_polygon(cx: int, cy: int, radius: int, num_points: int = 9) -> list[tuple[int, int]]:
    """Gera um polígono irregular a partir de um círculo distorcido."""
    points = []
    for i in range(num_points):
        angle = (2 * math.pi / num_points) * i
        r     = radius * random.uniform(0.65, 1.0)
        x     = cx + int(r * math.cos(angle))
        y     = cy + int(r * math.sin(angle))
        points.append((x, y))
    return points


class Asteroid(pygame.sprite.Sprite):
    """Asteroide que surge no topo e desce em velocidade constante."""

    SIZE_NAMES = ["large", "medium", "small"]

    def __init__(self, speed_multiplier: float = 1.0, size_name: str | None = None):
        super().__init__()

        # tamanho
        if size_name is None:
            size_name = random.choices(
                self.SIZE_NAMES,
                weights=[0.45, 0.35, 0.20]
            )[0]
        self.size_name = size_name
        self.radius, self.points_value = ASTEROID_SIZES[size_name]

        # posição inicial
        margin = self.radius + 5
        start_x = random.randint(margin, SCREEN_W - margin)
        start_y = -self.radius

        # velocidade (levemente aleatória para variar)
        base_speed = ASTEROID_BASE_SPEED * speed_multiplier
        self.speed = base_speed * random.uniform(0.85, 1.3)

        # rotação
        self.angle      = random.uniform(0, 360)
        self.rot_speed  = random.uniform(-1.8, 1.8)

        # gera o polígono base (relativo à origem)
        num_pts = {"large": 10, "medium": 8, "small": 7}[size_name]
        self._base_poly = _random_polygon(0, 0, self.radius, num_pts)

        # cor com leve variação
        r = min(255, NEON_ORANGE[0] + random.randint(-30, 30))
        g = min(200, NEON_ORANGE[1] + random.randint(-20, 30))
        b = random.randint(0, 20)
        self.color       = (r, g, b)
        self.edge_color  = (255, min(255, g + 60), 40)

        # rect de colisão (círculo aproximado por rect)
        d = self.radius * 2
        self.image = pygame.Surface((d, d), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(start_x, start_y))

        # posição float para precisão
        self._x = float(start_x)
        self._y = float(start_y)

    # ── atualização por frame ────────────────────────────────
    def update(self):
        self._y     += self.speed
        self.angle  += self.rot_speed
        self.rect.center = (int(self._x), int(self._y))

    # ── verificação de saída de tela ─────────────────────────
    def is_off_screen(self) -> bool:
        return self._y - self.radius > SCREEN_H

    # ── colisão por distância (mais precisa que rect) ────────
    def collides_with_rect(self, other_rect: pygame.Rect) -> bool:
        cx, cy = self.rect.center
        # ponto mais próximo do rect ao centro do asteroide
        nx = max(other_rect.left, min(cx, other_rect.right))
        ny = max(other_rect.top,  min(cy, other_rect.bottom))
        dist_sq = (cx - nx) ** 2 + (cy - ny) ** 2
        return dist_sq < (self.radius * 0.80) ** 2

    # ── desenho ──────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        cx, cy    = int(self._x), int(self._y)
        angle_rad = math.radians(self.angle)

        # rotacionar polígono
        rotated = []
        for px, py in self._base_poly:
            rx = px * math.cos(angle_rad) - py * math.sin(angle_rad)
            ry = px * math.sin(angle_rad) + py * math.cos(angle_rad)
            rotated.append((cx + rx, cy + ry))

        # sombra interna escura
        inner = [(cx + (px - cx) * 0.6, cy + (py - cy) * 0.6)
                 for px, py in rotated]
        pygame.draw.polygon(surface, (30, 20, 10), inner)

        # corpo
        pygame.draw.polygon(surface, self.color, rotated)
        # borda brilhante
        pygame.draw.polygon(surface, self.edge_color, rotated, 2)

        # detalhe: pequenas crateras
        if self.size_name in ("large", "medium"):
            for i, (px, py) in enumerate(rotated[::3]):
                r_crat = max(2, self.radius // 6)
                pygame.draw.circle(surface, (30, 20, 10),
                                   (int(px * 0.7 + cx * 0.3),
                                    int(py * 0.7 + cy * 0.3)),
                                   r_crat)
