import random
import numpy as np
import itertools
import pygame

"""  It may seems a lot of code for a simple graphical object.
The thing is I precalculate so the display operation is only 2 lines
usage:
    my_star = Dwingling_star(x,y)
    my_star.compute_RGB_sequence()
    for  x in range (0,100)
        my_star.x = x
        my_star.display_trail(pygame_screen)
"""

class Dwingling_star:
    def __init__(self, x, y, v=None, t=0, dwingling_sequence=None, apparent_magnitude=0, fading_speed=2):
        """ non-graphic object for a dwingling star crossing the screen horizontally
        if apparent_magnitude <> 0,  dwingling_sequence is ignored (a random sequence based on magnitude will be computed"""

        self.x = x
        self.y = y  
        self.t = t

        if v is None:
            self.v = self.default_star_speed()  # self.v between 5 and 10 (included)
        else:
            self.v = v

        if not apparent_magnitude:
            if dwingling_sequence:
                self.apparent_magnitude = np.average(dwingling_sequence)
            else:
                self.apparent_magnitude = random.randint(50, 250)
        else:
            self.apparent_magnitude = apparent_magnitude

        if dwingling_sequence is None:
            dwingling_sequence = np.random.rand(5)
            dwingling_sequence *= 200
            dwingling_sequence += 55
            dwingling_sequence *= self.apparent_magnitude

            self.dwingling_sequence =  np.zeros((5), np.uint8)
            self.dwingling_sequence[:] = dwingling_sequence[:] # un tableau d'entier de 155 à 255
        else:
            self.dwingling_sequence = dwingling_sequence

        self.fading_speed = fading_speed

        self.sequence = self.compute_sequence()  # a array of trail where each trail is an array of light intensity (uint8)
        self.RGB_sequence = None  # a array of trail where each trail is an array of RGB ( array(uint8,uint8,uint8) )

    def default_star_speed(self):
        # this function can (and should) be replaced (inheritance or Monkey Patching), depending on wanted behavoir
        return random.randint(5, 10)  # v between 5 and 10 (included)

    def compute_sequence(self, dwingling_sequence=None, fading_speed=None):
        # We precompute here how the star and its trail will dwingle
        if dwingling_sequence is None:
            dwingling_sequence = self.dwingling_sequence
        if fading_speed is None:
            fading_speed = self.fading_speed

        maximum_sequence_length = len(dwingling_sequence) + np.max(dwingling_sequence) // fading_speed - 1
        maximum_sequence_length = int(maximum_sequence_length)
        sequence = np.zeros((maximum_sequence_length, maximum_sequence_length),
                            np.int16)  # in fine, on veux des valeur entre 0 et 255, mais on va se retrouver avec des nombre négtif qu'on ecrétera plus tard en zéro

        dwingling_generator = itertools.cycle(dwingling_sequence)

        sequence[0, 0] = next(dwingling_generator)
        for n_seq in range(1, maximum_sequence_length):
            # le premier élément de la trainé (trail) est l'element suivant de la dwingling_sequence
            sequence[n_seq, 0] = next(dwingling_generator)

            # le reste de la trainé, c'est la trainé précédente moins la fading speed
            sequence[n_seq, 1:] = sequence[n_seq - 1, :-1] - fading_speed
            sequence[n_seq] = np.maximum(sequence[n_seq], 0)  # si valeur négative => 0

        # la fin de cette sequence est cyclique. C'est donc cet extrait de sequnce qu'on garde
        sequence = sequence[-len(dwingling_sequence):]

        if self: self.sequence = sequence
        return sequence

    def compute_RGB_sequence(self):
        # self.sequence is an array of light intensity. We want an array of RGB value (maybe I'll need alpha one day)
        self.RGB_sequence = self.sequence[..., np.newaxis].repeat(3, -1).astype("uint8")

    def update(self, elapsed_time = 1, absolute_time = None):
        self.x -= self.v * elapsed_time

        self.t += elapsed_time

    def get_trail(self):
        return self.sequence[self.t % self.sequence_length]

    def get_RGB_trail(self):
        return self.RGB_sequence[self.t % self.sequence_length]

    @property
    def trail_length(self):
        return self.sequence.shape[1]

    @property
    def sequence_length(self):
        return self.sequence.shape[0]

    def display_trail(self, surface:pygame.Surface): # TODO: manage if partially or totaly out of bounds
        screen3D = pygame.surfarray.pixels3d(surface)
        screen3D[self.x:self.x + self.trail_length, self.y] = self.get_RGB_trail()

    def display_trail_2(self, screen:pygame.Surface):
        if not (0<self.y<screen.get_height()) : return # if y do not match screen, there's noting to display

        # if x do not match screen, it is still possible that there's a part of the trail to display.
        # so, we start by dealing with the "normal" case
        if 0 < self.x < screen.get_width()-self.trail_length:
            screen3D = pygame.surfarray.pixels3d(screen)
            screen3D[self.x:self.x + self.trail_length, self.y] = self.get_RGB_trail()
        else:
            if self.x+self.trail_length<=0: return
            if self.x>screen.get_width() : return
            left_trim = max(-self.x, 0)
            right_trim = max(0, (self.x+self.trail_length - screen.get_width()) )
            screen3D = pygame.surfarray.pixels3d(screen)            
            screen3D[self.x + left_trim: self.x + self.trail_length-right_trim, self.y] = \
                    self.get_RGB_trail()[left_trim: self.trail_length-right_trim]

            
class Set_of_stars(set):
    def update(self, elapsed_time = 1):
        for star in self:
            star.update(elapsed_time)  # TODO optimisable si besoin

    def display(self, screen: pygame.Surface):
        for star in self:
            star.display_trail_2(screen)


if __name__ == "__main__":

    from pygame.locals import *

    def dwingling_test_2():
        liste = []
        for y in range(10, 600, 10):
            toto = Dwingling_star(800, y, fading_speed=2)
            toto.compute_RGB_sequence()
            liste += [toto]

        stars = Set_of_stars(liste)

        pygame.init()

        global_screen = pygame.display.set_mode((1024, 668), DOUBLEBUF)
        clock = pygame.time.Clock()

        for t in range(800):
            stars.display(global_screen)
            stars.update()
            clock.tick(30)
            pygame.display.flip()


    def dwingling_test():
        seq = [222, 200, 180, 250]
        # seq = dwingling_star.compute_sequence(None,seq, 2 )
        """ [[250 160 160 162 170  80  80  82  90   0   0   2   0   0   0]
             [222 230 140 140 142 150  60  60  62  70   0   0   0   0   0]
             [200 202 210 120 120 122 130  40  40  42  50   0   0   0   0]
             [180 180 182 190 100 100 102 110  20  20  22  30   0   0   0]]"""

        star = Dwingling_star(800, 200, dwingling_sequence=seq, fading_speed=2)
        star.compute_RGB_sequence()

        pygame.init()

        global_screen = pygame.display.set_mode((1024, 668), DOUBLEBUF)
        clock = pygame.time.Clock()

        for t in range(1000):
            star.display_trail_2(global_screen)
            star.update()
            clock.tick(30)
            pygame.display.flip()

    dwingling_test_2()

