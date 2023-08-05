"""Start menu
at this point, `__init__.py` has already run"""
import pygame
import pygame_menu
from . import main_loop
from . import params
from .FX.sound import play_music
from .skip_libs.credit_screen import display_credit_screen
from . import params


def start_the_game():
    print("start the game")
    main_loop.launch_game()  # TODO: Peut etre externaliser cet appel. Pour limiter le code en memoire
    play_music(params.music_menu) # restart the menu music


def credit_screen():
    global screen
    display_credit_screen()


def onMenuLoop(menu):
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_ESCAPE]:
        menu.quit_button.apply()  # simulate clic on Quit button


def create_menu_screen(surface):
    menu = pygame_menu.Menu('Welcome to Skipperz', 400, 300,
                            theme=pygame_menu.themes.THEME_BLUE)

    menu.play_button = menu.add.button('Play', start_the_game)
    menu.credit_button = menu.add.button('Credit screen', credit_screen)
    menu.quit_button = menu.add.button('Quit', pygame_menu.events.EXIT)

    menu.mainloop(surface, onMenuLoop)


if __name__ == "__main__":
    pygame.init()
    play_music(params.music_menu)
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

    create_menu_screen(screen)