import pygame
from pygame import Surface
import math
from typing import List

# TODO: maybe use pygame.freetype intead of pygame.font

try:
    pygame.font.init()
    defaultFont = pygame.font.Font(None, 50)
except TypeError:  # Pygame and PyInstaller have default font problem. Read https://github.com/pygame/pygame/issues/2603
    pygame.init()
    defaultFont = pygame.font.Font('assets/Raleway-VariableFont_wght.ttf', 50)


class CText:
    """CText for Control Text."""
    def __init__(self, x, y, text="", max_width=math.inf, max_height=math.inf, multiline=True, font=defaultFont, color = (255,255,255, 0)):
        self.valid = False
        self._x = x
        self._y = y
        self.max_width = max_width
        self.max_height = max_height
        self.multiline = multiline
        self.font = font
        self.color = color
        self._text = text
        self.interline = 2 # 2 pixel interline

    def _render(self) -> Surface:
        if not self.multiline:
            return self.font.render(self._text, False, self.color)

        surface_list : List[Surface] = list()
        for line in self._text.split("\n"):
            surface_list.append(self.font.render(line, False, self.color))

        result_width = max( [surf.get_width() for surf in surface_list ] )
        result_height = sum ( [surf.get_height() + self.interline for surf in surface_list])

        result = Surface((result_width, result_height), flags=pygame.SRCALPHA  )
        top = 0
        for surf in surface_list:
            result.blit( surf, (0,top) )
            top += surf.get_height()

        # TODO store result and validate
        return result

    def draw(self, dest:Surface):
        dest.blit(self._render(),(self.x, self.y))

    def invalidate(self):
        self.valid = False

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self.invalidate()
        self._text = new_text

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self.invalidate()
        self._x = new_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self.invalidate()
        self._y = new_y


if __name__ == "__main__":  # test
    screen_size = (1000, 600)
    pygame.init()

    # Surface Screen
    screen = pygame.display.set_mode(screen_size, pygame.DOUBLEBUF)
    text_zone = CText(20,20,"toto\ntata\ntiti")
    text_zone.draw(screen)

    pygame.display.flip()
    pygame.time.wait(2000)

    screen.fill((0, 0, 0))
    text_zone.text = "bonjour"
    text_zone.draw(screen)
    pygame.display.flip()
    pygame.time.wait(2000)
