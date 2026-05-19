# ============================================================
#  hud.py — Interface visual: pontuação, menus e overlays
# ============================================================

import math
# pyrefly: ignore [missing-import]
import pygame
from settings import (
    SCREEN_W, SCREEN_H,
    WHITE, BLACK, NEON_CYAN, NEON_YELLOW, NEON_GREEN,
    NEON_RED, NEON_ORANGE, DARK_GREY, GREY
)


def _shadow_text(surface, font, text, color, x, y,
                 shadow_color=(0, 0, 0), offset=2):
    """Renderiza texto com sombra deslocada."""
    shadow = font.render(text, True, shadow_color)
    main   = font.render(text, True, color)
    surface.blit(shadow, (x + offset, y + offset))
    surface.blit(main,   (x, y))


class HUD:
    """Renderiza todos os elementos de interface do jogo."""

    def __init__(self):
        pygame.font.init()
        # fontes
        self.font_small  = pygame.font.SysFont("Courier New", 20, bold=True)
        self.font_medium = pygame.font.SysFont("Courier New", 32, bold=True)
        self.font_large  = pygame.font.SysFont("Courier New", 56, bold=True)
        self.font_title  = pygame.font.SysFont("Courier New", 72, bold=True)

        self._tick = 0  # animação

    def update(self):
        self._tick += 1

    # ── pontuação durante o jogo ─────────────────────────────
    def draw_score(self, surface: pygame.Surface, score: int, high_score: int):
        # painel semi-transparente
        panel = pygame.Surface((220, 54), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        surface.blit(panel, (8, 8))

        _shadow_text(surface, self.font_small,
                     f"SCORE  {score:>7}", NEON_CYAN, 14, 14)
        _shadow_text(surface, self.font_small,
                     f"BEST   {high_score:>7}", NEON_YELLOW, 14, 36)

    # ── nível e velocidade ───────────────────────────────────
    def draw_level(self, surface: pygame.Surface, level: int):
        text = f"LVL {level}"
        surf = self.font_small.render(text, True, NEON_GREEN)
        surface.blit(surf, (SCREEN_W - surf.get_width() - 14, 14))

    # ── tela de menu inicial ─────────────────────────────────
    def draw_menu(self, surface: pygame.Surface):
        # overlay escuro
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        # título pulsante
        pulse = abs(math.sin(self._tick * 0.04))
        title_color = (
            int(NEON_CYAN[0] * pulse + WHITE[0] * (1 - pulse)),
            int(NEON_CYAN[1] * pulse + WHITE[1] * (1 - pulse)),
            int(NEON_CYAN[2] * pulse + WHITE[2] * (1 - pulse)),
        )
        title_surf = self.font_title.render("ASTEROID", True, title_color)
        subtitle   = self.font_large.render("BLASTER", True, NEON_ORANGE)

        cx = SCREEN_W // 2
        surface.blit(title_surf,  title_surf.get_rect(center=(cx, 160)))
        surface.blit(subtitle,    subtitle.get_rect(center=(cx, 235)))

        # linha decorativa
        pygame.draw.line(surface, NEON_CYAN,
                         (cx - 200, 270), (cx + 200, 270), 2)

        # instruções
        instructions = [
            ("← → / A D", "Mover nave"),
            ("ESPAÇO / ↑",  "Atirar"),
            ("ESC",          "Sair"),
        ]
        y_start = 300
        for key, action in instructions:
            key_surf = self.font_small.render(f"{key:<14}", True, NEON_YELLOW)
            act_surf = self.font_small.render(action,       True, WHITE)
            surface.blit(key_surf, key_surf.get_rect(right=cx - 10, y=y_start))
            surface.blit(act_surf, act_surf.get_rect(left=cx + 10,  y=y_start))
            y_start += 34

        # botão pisca
        if (self._tick // 30) % 2 == 0:
            start_surf = self.font_medium.render(
                "[ PRESSIONE ENTER PARA JOGAR ]", True, NEON_GREEN
            )
            surface.blit(start_surf, start_surf.get_rect(center=(cx, 470)))

        # versão
        ver = self.font_small.render("v1.0 — Atari Edition", True, DARK_GREY)
        surface.blit(ver, ver.get_rect(center=(cx, SCREEN_H - 22)))

    # ── tela de game over ────────────────────────────────────
    def draw_game_over(self, surface: pygame.Surface,
                       score: int, high_score: int, is_new_record: bool):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_W // 2

        # título Game Over com efeito vermelho pulsante
        pulse = abs(math.sin(self._tick * 0.05))
        r = int(NEON_RED[0])
        g = int(50 * pulse)
        go_surf = self.font_large.render("GAME  OVER", True, (r, g, 50))
        surface.blit(go_surf, go_surf.get_rect(center=(cx, 155)))

        # linha decorativa superior
        pygame.draw.line(surface, NEON_RED, (cx - 220, 195), (cx + 220, 195), 2)

        # pontuação final em destaque
        sc_label = self.font_small.render("PONTUAÇÃO FINAL", True, GREY)
        surface.blit(sc_label, sc_label.get_rect(center=(cx, 220)))

        sc_surf = self.font_large.render(str(score), True, WHITE)
        surface.blit(sc_surf, sc_surf.get_rect(center=(cx, 265)))

        # recorde
        hi_color = NEON_GREEN if is_new_record else NEON_YELLOW
        hi_label = "★  NOVO RECORDE!  ★" if is_new_record else f"RECORDE:  {high_score}"
        hi_surf  = self.font_medium.render(hi_label, True, hi_color)
        surface.blit(hi_surf, hi_surf.get_rect(center=(cx, 320)))

        # linha divisória
        pygame.draw.line(surface, GREY, (cx - 220, 360), (cx + 220, 360), 1)

        # pergunta ao jogador
        q_surf = self.font_small.render("Deseja jogar novamente?", True, WHITE)
        surface.blit(q_surf, q_surf.get_rect(center=(cx, 385)))

        # botão R — pisca
        if (self._tick // 25) % 2 == 0:
            r_surf = self.font_medium.render("[ R ]  SIM, JOGAR NOVAMENTE", True, NEON_GREEN)
            surface.blit(r_surf, r_surf.get_rect(center=(cx, 425)))
        else:
            r_surf = self.font_medium.render("[ R ]  SIM, JOGAR NOVAMENTE", True, (0, 120, 60))
            surface.blit(r_surf, r_surf.get_rect(center=(cx, 425)))

        # botão ESC
        esc_surf = self.font_small.render("[ ESC ]  NÃO, VOLTAR AO MENU", True, GREY)
        surface.blit(esc_surf, esc_surf.get_rect(center=(cx, 472)))

    # ── efeito de explosão (flash de tela) ───────────────────
    def draw_flash(self, surface: pygame.Surface, intensity: int):
        if intensity <= 0:
            return
        flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        alpha = min(180, intensity * 18)
        flash.fill((255, 200, 50, alpha))
        surface.blit(flash, (0, 0))
