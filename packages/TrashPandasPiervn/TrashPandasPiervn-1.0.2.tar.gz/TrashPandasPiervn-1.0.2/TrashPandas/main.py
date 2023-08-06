"""Główny moduł całego projektu. Zawiera pętle w której sprawdzane są zdarzenia 
(wciśnięcia przycisków myszy i klawiatury) oraz rysowane są klatki gry."""

import pygame
import scoreboard as scoreboard
from window import *
from units import TrashPanda, Player, Bullet, Button
from levels import *

player = Player()
bg_color = (30, 30, 30)

# BULLETS AND PANDAS
panda_grid = [] #: Lista zawierająca przeciwników znajdujących się na ekranie.
bullets = [] #: Lista zawierająca pociski znajdujące się na ekranie.
bullet_counter = 0 #: Licznik częstotliwości pocisków.
shotting_break = 110
score = 0 #: Punktacja.

# LEVELS
level = 0 #: Zmienna przyjmująca numer poziomu wyświetlanego na ekranie
end_screen = 3 #: Numer ekranu końcowego.

# BUTTONS
hover_color = (150, 150, 150) #: Kolor na jaki podświetlają się przyciski.
play_button = Button('PLAY', 50, 0, 300) #: Przycisk PLAY.
scoreboard_button = Button('SCOREBOARD', 50, 0, 400) #: Przycisk SCOREBOARD.
back_button = Button('BACK', 50, 0, 700) #: Przycisk BACK.
cancel_button = Button('CANCEL', 30, -90, 450) #: Przycisk CANCEL.
submit_button = Button('SUBMIT', 30, 90, 450) #: Przycisk SUBMIT.


# SUBMIT SCORE
nick_to_submit = '' #: Zmienna przechowująca nick gracza, który chce zapisać swój wynik.
input_box = pygame.Rect(MID - 100, 380, 340, 50) #: Objekt służący do wpisania nicku gracza na koniec gry.
color_inactive = pygame.Color('lightskyblue3') #: Nieaktywny kolor ramki wpisywania.
color_active = pygame.Color('dodgerblue2') #: Aktywny kolor ramki wpisywania.
color = color_inactive
active = False #: Zmienna opisująca stan ramki wpisywania.

create_level(panda_grid)


def draw_window(mouse):
    """Rysowanie klatek na ekranie. Przy użyciu instrukcji ```match``` rozdzielam sposoby rysowania klatek
    ze względu na wartość zmiennej ```level```.
    
    Args:
        mouse (pygame.mouse.pos): Obiekt przechowujący dane o pozycji kursora myszy.
    
    Numeracja:
        * -1 -> Tablica wyników
        * 0 -> Menu / Ekran startowy
        * 1 -> Poziom 1
        * 2 -> Poziom 2
        * 3 -> Ekran końcowy / Zapisywanie wyniku.
    """
    global level, intro, shotting_break
    match level:
        case -1:
            WIN.fill(bg_color)
            pygame.draw.rect(WIN, (50, 50, 50), [MID - 400, MARGIN, 800, 600])
            draw_scoreboard(10)
            back_button.hover_button(mouse, bg_color, hover_color)
            back_button.spawn_button()
        case 0:
            WIN.fill(bg_color)
            WIN.blit(TRASHPANDAS, (MID - TRASHPANDAS.get_rect().width/2, 100))
            play_button.hover_button(mouse, bg_color, hover_color)
            scoreboard_button.hover_button(mouse, bg_color, hover_color)
            play_button.spawn_button()
            scoreboard_button.spawn_button()
        case 1:
            WIN.blit(BG_LVL1, (-10, -10))
            interface()
            for bullet in bullets:
                bullet.spawn()
            spawn_level(panda_grid, bullets)
            player.spawn()
            if level_finished():
                shotting_break = 240
                level += 1
                create_level(panda_grid)
        case 2:
            WIN.blit(BG_LVL2, (0, -120))
            interface()
            for bullet in bullets:
                bullet.spawn()
            spawn_level(panda_grid, bullets)
            player.spawn()
            if level_finished():
                shotting_break = 240
                level += 1
                create_level(panda_grid)
        case 3:
            draw_submit_score()
            cancel_button.hover_button(mouse, bg_color, hover_color)
            submit_button.hover_button(mouse, bg_color, hover_color)
            cancel_button.spawn_button()
            submit_button.spawn_button()
    pygame.display.update()


def draw_scoreboard(records: int):
    """Rysowanie tablicy wyników.

    Args:
        records (int): Liczba wyświetlanych rekordów.
    """
    number_of_scores = 0
    scores = scoreboard.session.query(
        scoreboard.Score).order_by(scoreboard.Score.score.desc()).all()
    for s in scores:
        record = scoreboard_font.render(
            str(number_of_scores+1)+'. '+str(s.nick), False, text_color)
        WIN.blit(record, (MID - 380, MARGIN +
                          20 + number_of_scores*60))
        record = scoreboard_font.render(
            str(s.score), False, text_color)
        WIN.blit(record, (MID + 380 - record.get_rect().width,
                          MARGIN + 20 + number_of_scores*60))
        number_of_scores += 1
        if number_of_scores >= records:
            return


def draw_submit_score():
    """Rysowanie ekranu końcowego / zapisywania wyniku."""
    WIN.fill(bg_color)
    WIN.blit(YOU_WIN, (MID - YOU_WIN.get_rect().width/2, 100))
    WIN.blit(NICK, (MID - NICK.get_rect().width/2, 300))
    # Render the current text.
    text_surface = scoreboard_font.render(
        nick_to_submit, False, color)
    # Resize the box if the text is too long.
    width = max(340, text_surface.get_width()+10)
    input_box.w = width
    # Blit the text.
    WIN.blit(text_surface, (MID - input_box.w/2 + 5, input_box.y+5))
    # Blit the input_box rect.
    pygame.draw.rect(
        WIN, color, [MID - input_box.w/2, 380, input_box.w, input_box.h], 2)


def shot_bullets():
    """Funkcja odpowiadająca za wypuszczanie pocisków."""
    global bullet_counter, bullets, shotting_break
    for i in range(0, len(bullets)):
        bullets[i].movement()
        if bullets[i].rect.y < -30:
            del bullets[i]
            break
    if shotting_break > 0:
        shotting_break -= 1
        return
    if bullet_counter % BULLET_FREQUENCY == 0:
        n = Bullet(player.rect.x + 20, player.rect.y - 25)
        bullets.append(n)
    bullet_counter += 1
    bullet_counter %= BULLET_FREQUENCY


def hit_panda():
    """Usuwanie przeciwników po trafieniu."""
    global bullets, score
    for p in range(len(panda_grid)):
        for b in range(len(bullets)):
            if panda_grid[p] and panda_grid[p].rect.colliderect(bullets[b]):
                score += 1
                panda_grid[p] = 0
                del bullets[b]
                break


def interface():
    """Rysowanie interfejsu - życie i liczba punktów."""
    global score
    for i in range(3):
        WIN.blit(HP, (10 + i*(HP.get_width() + 2), 10))
    interface_score = myfont.render(str(score), False, text_color)
    WIN.blit(interface_score, (180, 10))


def level_finished():
    """Warunek zakończenia gry - wszyscy przeciwnicy pokonani - nieutworzeni na nowo."""
    return not any(panda_grid)


# MAIN LOOP
def main_loop():
    """Główna pętla programu. Jej kolejne zadania to:
    
        * Sprawdzanie wszystkich zdarzeń - wciśnieć przycisków.
        * Wykonywanie ruchu gracza, usuwanie przeciwników oraz wypuszczanie pocisków podczas rozgrywania poziomów.
        * Wywołanie funkcji rysującej klatki.

    """
    global RUN, level, active, nick_to_submit, color
    while RUN: #: Główna pętla
        clock.tick(FPS)
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get(): #: Pętla sprawdzająca wszystkie zdarzenia - wciśnięcia przycisków.
            if event.type == pygame.QUIT: #: Zamknięcie okna.
                RUN = False
            elif event.type == pygame.MOUSEBUTTONDOWN: #: Kliknięcie przycisku myszy.
                if level == 0:
                    if play_button.mouse_over_button(mouse):
                        level = 1
                        player.starting_position()
                    if scoreboard_button.mouse_over_button(mouse):
                        level = -1
                elif level == -1 and back_button.mouse_over_button(mouse):
                    #scoreboard.add_score("pierun", 1234)
                    level = 0
                elif level == end_screen:
                    if input_box.collidepoint(event.pos):
                        active = True
                    else:
                        active = False
                    color = color_active if active else color_inactive
                    if cancel_button.mouse_over_button(mouse):
                        level = 0
                    if submit_button.mouse_over_button(mouse):
                        scoreboard.add_score(nick_to_submit, score)
                        # print(nick_to_submit)
                        level = 0
                        nick_to_submit = ''
            elif level == end_screen and event.type == pygame.KEYDOWN: #: Wprowadzanie nicku do pola umieszczonego na ekranie końcowym.
                if active:
                    if event.key == pygame.K_RETURN:
                        scoreboard.add_score(nick_to_submit, score)
                        # print(nick_to_submit)
                        nick_to_submit = ''
                        level = 0
                    elif event.key == pygame.K_BACKSPACE:
                        nick_to_submit = nick_to_submit[:-1]
                    else:
                        nick_to_submit += event.unicode
        if level in [1, 2]: #: Ruch gracza, usuwanie przeciwników oraz wypuszczanie pocisków podczas rozgrywania poziomów. 
            player.movement()
            hit_panda()
            shot_bullets()
        draw_window(mouse) #: Wywołanie funkcji rysującej klatki.

def main():
    main_loop() #: Wywołanie głównej pętli.
    scoreboard.session.close() #: Zamknięcie sesji zapisu i odczytu z bazy danych.
    pygame.quit() #: Zakończenie działania modułu ```pygame```.
