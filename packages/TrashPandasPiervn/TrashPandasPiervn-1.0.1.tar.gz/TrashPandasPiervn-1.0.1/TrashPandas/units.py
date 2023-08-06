"""Moduł zawierający podstawowe klasy."""
import pygame
from window import *


class Player():
    """Klasa opisująca działanie gracza."""

    def __init__(self):
        """Inicjacja gracza."""
        self.rect = pygame.Rect(MID - SHIP.get_width()/2,
                                BOTTOM, SHIP.get_width(), SHIP.get_height())

    def spawn(self):
        """Pojawianie się gracza na ekranie."""
        WIN.blit(SHIP, (self.rect.x, self.rect.y))

    def starting_position(self):
        """Ustawienie domyślnej pozycji gracza."""
        self.rect.x = MID - SHIP.get_width()/2
        self.rect.y = BOTTOM

    def movement(self):
        """Przypisanie działania strzałek do ruchu gracza."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x - PLAYER_SPEED > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.x + PLAYER_SPEED < WIN_WIDTH - 64:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.rect.y + PLAYER_SPEED < WIN_HEIGHT - 64:
            self.rect.y += PLAYER_SPEED
        if keys[pygame.K_UP] and self.rect.y - PLAYER_SPEED > 0:
            self.rect.y -= PLAYER_SPEED


class Bullet():
    """Klasa opisująca działanie pocisku"""
    def __init__(self, x: int, y: int):
        """Inicjacja pocisku.

        Args:
            x (int): Pozycja pocisku na osi X.
            y (int): Pozycja pocsiku na osi Y.
        """
        self.rect = pygame.Rect(x, y, BULLET.get_width(), BULLET.get_height())

    def spawn(self):
        """Pojawianie się pocisku na ekranie."""
        WIN.blit(BULLET, (self.rect.x, self.rect.y))

    def movement(self):
        """Ruch pocisku."""
        self.rect.y -= BULLET_SPEED


class TrashPanda():
    """Klasa opisująca działanie przeciwnika - szopa."""
    def __init__(self, x: int, y: int):
        """Inicjacja przeciwnika - szopa.

        Args:
            x (int): Pozycja przeciwnika na osi X.
            y (int): Pozycja przeciwnika na osi Y.
        """
        self.rect = pygame.Rect(
            x, y, RACCOON.get_width(), RACCOON.get_height())

    def spawn(self):
        """Pojawianie się przeciwnika na ekranie."""
        WIN.blit(RACCOON, (self.rect.x, self.rect.y))


class Button():
    """Klasa opisująca działanie przycisku."""
    def __init__(self, text: str, font_size: int, center_offset: int, y: int):
        """Inicjacja przycisku.

        Args:
            text (str): Tekst przycisku.
            font_size (int): Wielkość tekstu przycisku.
            center_offset (int): Pozycja przycisku względem środka szerokości ekranu. ``` -MID <= center_offset <= MID ```.
            y (int): Pozycja przycisku na osi Y.
        """
        font = pygame.font.SysFont('comfortaaregular', font_size)
        self.text = font.render(text, False, text_color)
        self.half_width = self.text.get_rect().width/2
        self.height = self.text.get_rect().height
        self.offset = center_offset
        self.ypos = y

    def mouse_over_button(self, mouse) -> bool:
        """Sprawdza czy kursor myszy znajduje się nad pryciskiem.

        Args:
            mouse (pygame.mouse.pos): Obiekt przechowujący dane o pozycji kursora myszy.

        Returns:
            bool: Prawda lub Fałsz
        """
        return MID - self.half_width + self.offset <= mouse[0] <= MID+self.half_width + self.offset and self.ypos <= mouse[1] <= self.ypos+self.height

    def hover_button(self, mouse, color: tuple, hover_color: tuple):
        """Zmiana koloru przycisku po najechaniu myszą.

        Args:
            mouse (pygame.mouse.pos): Obiekt przechowujący dane o pozycji kursora myszy.
            color (tuple): Kolor przycisku.
            hover_color (tuple): Kolor przycisku po najechaniu myszą.
        """
        if self.mouse_over_button(mouse):
            pygame.draw.rect(WIN, hover_color, [
                MID-self.half_width + self.offset, self.ypos, self.half_width*2, self.height])
        else:
            pygame.draw.rect(WIN, color, [
                MID-self.half_width + self.offset, self.ypos, self.half_width*2, self.height])

    def spawn_button(self):
        """Pojawianie się przycisku na ekranie."""
        WIN.blit(self.text, (MID - self.half_width + self.offset, self.ypos))
