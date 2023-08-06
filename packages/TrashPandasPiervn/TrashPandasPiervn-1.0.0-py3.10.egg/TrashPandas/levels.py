"""Moduł zawierający funkcje odpowiedzialne za tworzenie poziomów."""

import pygame
from units import TrashPanda
from window import *

intro = True  #: Zmienna określająca czy wejście przeciwników ma nastąpić.


def create_level(panda_grid: list):
    """Tworzy siatkę przeciwników.

    Args:
        panda_grid (list): Lista reprezentująca siatkę przeciwników.
    """
    for i in range(4):
        for j in range(5):
            panda = TrashPanda(
                MID + 120*(j-2) - RACCOON.get_width()/2, MARGIN + 100*i - 600)
            if i*5+j < len(panda_grid):
                panda_grid[i*5+j] = panda
            else:
                panda_grid.append(panda)


def intro_movement_level(panda_grid: list, bullets: list):
    """Animuje rozpoczęcie nowego poziomu.

    Args:
        panda_grid (list): Lista reprezentująca siatkę przeciwników.
        bullets (list): Lista reprezentująca pociski znajdujące się na ekranie.
    """
    if any(bullets):
        return
    for panda in panda_grid:
        if panda != 0:
            panda.rect.y += PANDAS_ENTRY_SPEED


def spawn_level(panda_grid: list, bullets: list):
    """Rysuje na ekranie siatkę przeciwników

    Args:
        panda_grid (list): Lista reprezentująca siatkę przeciwników.
        bullets (list): Lista reprezentująca pociski znajdujące się na ekranie.
    """
    global intro
    if intro:
        intro_movement_level(panda_grid, bullets)
        if panda_grid[0].rect.y == MARGIN:
            intro = False
    for k in range(len(panda_grid)):
        if panda_grid[k]:
            panda_grid[k].spawn()
    if not any(panda_grid):
        intro = True
