from .game import game_in_progress, Game

import time
import pygame

from . import params
from .skip_libs import pgZoneText
from  .FX import sound
from .pgSprite.pgSprite import Animation, Sprite
from .skip_libs.pgThrotle import Throtle

from .levels import enchainement


def initialisation():
    global screen, clock, baddies, still_running, sound_bank, textZone,\
        animationHeros, animationBoum, spriteHeros, herosThrotle

    pygame.init()
    screen = pygame.display.set_mode((1200, 850), pygame.FULLSCREEN)
    game_in_progress.screen_rectangle = pygame.display.get_surface().get_rect()
    enchainement.init()
    clock = pygame.time.Clock()
    baddies = set()

    still_running = True  # False if user close window or press "Esc" key

    sound_bank = dict()
    sound.load_sounds(sound_bank)

    textZone = pgZoneText.CText(screen.get_width()-150, 1, "0")  #    pgZoneText.TextZone((screen.get_width()-150, 1), (screen.get_width()-10, 50))
    animationBoum = Animation(params.explosion_1_animation)
    animationHeros = Animation(params.hero_1_animation)
    spriteHeros = Sprite(animation=animationHeros)
    spriteHeros.x = 20
    spriteHeros.y = 300
    herosThrotle = Throtle(spriteHeros, acceleration=(80, 80))  # each tick with key pressed, speed increase


def manage_voluntary_exit():
    """" exits when user press `esc` or external order is given"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_in_progress.loop_level = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_in_progress.loop_level = 0


def displayHero():
    spriteHeros.display(screen)


def exitScreen(sprite: Sprite, screen: pygame.Surface) -> bool:
    return not(screen.get_rect().contains(sprite.rect))


def killOnExit(sprite: Sprite):
    global screen
    # The sprite bounce on the screen border
    if not (0 < sprite.x < screen.get_width() - sprite.rect.width):
        sprite.vx = - sprite.vx
    if not (0 < sprite.y < screen.get_height() - sprite.rect.height):
        sprite.vy = - sprite.vy
    sprite.kill()  # then dies


def death_animation(level):
    """when the heroe dies"""
    sound_bank['death_of_hero'].play()

    spriteHeros.animation = animationBoum
    spriteHeros.animation.frequency = 5
    spriteHeros.acceleration.x = 0
    spriteHeros.acceleration.y = 0

    for i in range(100):
        level.update()  # update position of scroll, bad guy and thing linked to this level
        refresh_screen(level)
        # for sprite_BadGuy in BadGuy.listBadGuys:
        #   sprite_BadGuy.update()  # modifie la position logique du mechant
        spriteHeros.update()

        manage_voluntary_exit()
        if game_in_progress.loop_level == Game.MENU:  # if Esc pressed or window manually closed
            return


def refresh_screen(level=None):
    pygame.display.flip()
    clock.tick(30)

    if level is not None:
        level.draw(screen)
    displayHero()

    textZone.text = str(game_in_progress.score)
    textZone.draw(screen)


def launch_game():
    global still_running, screen, spriteHeros

    initialisation()
    game_in_progress.loop_level = Game.WHILE_LEVEL_UPDATE
    game_in_progress.score = 0
    while (level := enchainement.next_level()) and game_in_progress.loop_level >= Game.FOR_EACH_LEVEL:
        level.start()
        while spriteHeros.alive and level.update() \
                and game_in_progress.loop_level >= Game.WHILE_LEVEL_UPDATE:
            refresh_screen(level)  # mostly drawing stuffs

            herosThrotle.readKeyboard()  # modifie vitesse ou acceleration heros
            spriteHeros.update()
            if spriteHeros.collideAny(level.danger):  # comment those 2 lines for god-mode
                spriteHeros.kill()  # comment those 2 lines for god-mode

            if exitScreen(spriteHeros, screen):
                killOnExit(spriteHeros)

            manage_voluntary_exit()
            pygame.event.pump()

        if not spriteHeros.alive:  # we exited the loop 'cause he's dead
            print("You died. Your score is: ", game_in_progress.score)
            death_animation(level)
            game_in_progress.loop_level = Game.MENU


if __name__ == "__main__":
    launch_game()
