from  ..skip_libs.raster import TextRaster
import pygame
import time

def display_credit_screen():
    credit_text = """A game by Simon Zozol
    
    
    Code by Simon Zozol under CC0 licence
    
    Graphics: CC0 stuffs found around the web
    
    music: module from ????
    """

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN & pygame.DOUBLEBUF)

    text_zone = TextRaster(1,1, credit_text)

    exit = False

    while not exit:
        screen.fill((0,0,0,0))
        screen.blit(text_zone._render(), (1,1))
        pygame.display.flip()
        time.sleep(0.02)

        # exit whenever user press a key or a mouse button
        exit = pygame.event.get(pygame.KEYDOWN) or pygame.event.get(pygame.MOUSEBUTTONDOWN)