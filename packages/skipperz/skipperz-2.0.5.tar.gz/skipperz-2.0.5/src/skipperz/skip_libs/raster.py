import pygame
from pygame import Surface
import numpy as np
from ..skip_libs import pgZoneText as text_zone
import math
import time

class TextRaster (text_zone.CText):
    """A text having a raster color effect"""

    PALETTE_SIZE = 500
    # palette is a column where each number is a diferent color
    palette = np.ndarray((1, PALETTE_SIZE), np.uint32)
    step = 11 + 17*256 + 7*256*256
    start = 0 + 128*256 + 255*256*256
    for line in range(PALETTE_SIZE):
        palette[0, line] = (start + line * step) % 16777216

    def __init__(self, x, y, text="", max_width=math.inf, max_height=math.inf, multiline=True
                 , font=text_zone.defaultFont):
        text_zone.CText.__init__(self, x, y, text, max_width, max_height, multiline, font)
        self.start_time = time.time()

    def _render(self) -> Surface:
        elapsed_time = time.time() - self.start_time
        # each black pixel will be translated as False in mask
        mask: np.ndarray
        mask = pygame.surfarray.pixels2d(text_zone.CText._render(self)) != 0

        result = pygame.Surface(mask.shape)
        result_array = pygame.surfarray.pixels2d(result)

        for ln in range(result.get_height() - 1):
            color_number = int((ln + elapsed_time*20) % self.PALETTE_SIZE)
            result_array[:, ln] = mask[:, ln] * self.palette[0, color_number]

        return result

