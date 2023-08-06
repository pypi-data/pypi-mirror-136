"""Moduł zawierający bazowe wartości dotyczące rozgrywki.

    Grafika:
        * www.flaticon.com
        * www.pexels.com
"""

import pygame

WIN_WIDTH = 1200  #: Szerokość okna
WIN_HEIGHT = 780  #: Wysokość okna


# GAME VARIABLES
RUN = True  #: Warunek działania głównej pętli pygame.

FPS = 60  #: Liczba klatek na sekundę.
MID = WIN_WIDTH/2  #: Połowa szerokości ekranu.
BOTTOM = WIN_HEIGHT-100  # : Dolna część ekranu.
MARGIN = 60  #: Margines dla obiektów.
PLAYER_SPEED = 5  #: Szybkość gracza.
BULLET_SPEED = 6  #: Szybkość pocisków.
PANDAS_ENTRY_SPEED = 6  #: Szybkość animacji poziomów.
BULLET_FREQUENCY = 6  #: Częstotliwość pocisków.

# WINDOW SETTINGS
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  #: Okno gry
clock = pygame.time.Clock()
pygame.display.set_caption("Trash Pandas")  #: Tytuł okna
pygame.font.init()

# STRINGS
text_color = (255, 255, 255)
title = pygame.font.SysFont('comfortaaregular', 80)
myfont = pygame.font.SysFont('comfortaaregular', 50)
scoreboard_font = pygame.font.SysFont('comfortaaregular', 30)

TRASHPANDAS = title.render('TRASH PANDAS', False, text_color)
YOU_WIN = title.render('YOU WIN', False, text_color)
NICK = myfont.render('NICK', False, text_color)

# IMAGES
BG_LVL1 = pygame.image.load('assets/background_lvl1_blur.jpg') #: Tło 1 poziomu.
BG_LVL2 = pygame.image.load('assets/background_lvl2_blur.jpg') #: Tło 2 poziomu.

SHIP = pygame.image.load('assets/spaceshipv2.png') #: Grafika statku.
RACCOON = pygame.image.load('assets/racoon64.png') #: Grafika szopa.
HP = pygame.image.load('assets/heart_32.png') #: Grafika serca.
BULLET = pygame.image.load('assets/bullet_fire.png') #: Grafika pocisku.
