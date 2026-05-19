# ============================================================
#  main.py — Ponto de entrada do jogo
# ============================================================

import sys
# pyrefly: ignore [missing-import]
import pygame
from settings import SCREEN_W, SCREEN_H, FPS, TITLE
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    # janela com suporte a alpha (para efeitos de brilho)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    # ícone simples gerado via pygame (sem arquivo externo)
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.polygon(icon, (0, 230, 255), [(16, 2), (2, 30), (16, 22), (30, 30)])
    pygame.display.set_icon(icon)

    game = Game(screen)
    game.run()

    sys.exit(0)


if __name__ == "__main__":
    main()
