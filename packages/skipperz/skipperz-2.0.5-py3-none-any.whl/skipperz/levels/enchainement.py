#from game import game_in_progress
from .level import Level
from .level_1 import Level1
from .level_2 import Level2
from .. import game
'''import levels.level as level
import levels.level_1 as level_1'''
import pygame

current_level = 0  # no level
generator = None


def init():
    global generator
    generator = level_generator()


def next_level() -> Level:
    global generator
    try:
        return next(generator)
    except StopIteration:
        return False


def level_generator() -> 'generator':
    global current_level #, game

    niveau = Level1(game.game_in_progress.screen_rectangle)
    current_level += 1
    print("Yield new level: ", niveau)
    yield niveau

    niveau = Level2(game.game_in_progress.screen_rectangle)
    current_level += 1
    yield niveau
