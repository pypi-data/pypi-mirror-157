import pygame
from .. import params

def play_music(file_name):
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play(-1)

def load_sounds(dico_sound:dict):
    # dico_sound['sound_loop'] = pygame.mixer.music.load(params.sound_loop)
    dico_sound['death_of_hero'] = pygame.mixer.Sound(params.death_of_hero)
