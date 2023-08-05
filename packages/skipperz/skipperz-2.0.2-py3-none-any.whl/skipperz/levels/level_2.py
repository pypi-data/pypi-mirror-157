import pygame.display
from levels.level import Level
from FX.dwingling_stars import Dwingling_star
from FX import sound
from skip_libs import badGuys
import random

import zzChrono.zz_chrono as zz_chrono


class Universe_rect:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Level2 (Level):
    TOTAL_DURATION = 150
    TRANSITION_DURATION = 3

    def __init__(self, visible_universe: "rectangle(width, height)"):
        Level.__init__(self)

        if visible_universe is None:
            self.visible_universe = Universe_rect(1000, 800)
        else:
            self.visible_universe = visible_universe

    def start(self):
        Level.start(self)
        # sound.play_music("assets/alien.mod")
        # TODO: sound.play_music should check if the current music is the same. If so, don't restart
        badGuys.BadGuy.animationBadGuy.convert_alpha(pygame.display.get_surface())

    # each object in the self.object MUST have obj.x, obj.update and obj.hash
    def update(self) -> bool:
        Level.update(self)
        dead_objects = []

        for object in self.objects:  # object can be baddies or dwngling stars
            object.update()
            if object.x < -100:
                dead_objects.append(object)
        for object in dead_objects:
            self.objects.remove(object)
            self.score(15)

        return self.elapsed_time < self.TOTAL_DURATION

    @zz_chrono.chronometer("draw_star")
    def draw_stars(self, dest):
        star: Dwingling_star
        for star in {star for star in self.objects if type(star) is Dwingling_star}:
            star.display_trail_2(dest)

    @zz_chrono.chronometer("drawBaddies")
    def drawBaddies(self, dest: pygame.Surface):
        for sprite_BadGuy in {sprite for sprite in self.objects if isinstance(sprite, badGuys.BadGuy)}:
            sprite_BadGuy.display(dest)

    def draw(self, dest):
        dest.fill((0, 0, 0, 0))
        self.draw_stars(dest)
        self.drawBaddies(dest)

    def spawn(self):
        if not hasattr(self, "time_last_spawn") or self.time_last_spawn is None:
            self.time_last_spawn = self.time_function()

        if self.elapsed_time > self.TOTAL_DURATION - self.TRANSITION_DURATION:
            return None  # si on est dans la transition fermante, on ne spawn rien

        if random.randint(0, 10) == 1:
            return self.spawn_star()

        if self.elapsed_time < self.TRANSITION_DURATION:
            return None  # on ne spawn pas de mechant dans les premiere secondes

        if self.time_function() - self.time_last_spawn > 1.5:  # spawn bad guy each 1.5 second
            self.time_last_spawn = self.time_function()
            baddy = self.spawn_bad_guy()
            while not badGuys.paramValid(baddy):
                baddy = self.spawn_bad_guy()
            return baddy

        else:
            return None

    def spawn_bad_guy(self) -> badGuys.BadGuy:
        """"The bad guy fly horizontally across the screen (right to left)"""
        baddy = badGuys.BadGuy()
        baddy.animation = badGuys.BadGuy.animationBadGuy
        baddy.x = self.visible_universe.width + baddy.rect.width
        # baddy.y = random.randrange(0, self.visible_universe.height - baddy.rect.height)
        baddy.y = random.randrange(-200, self.visible_universe.height - baddy.rect.height + 200)
        baddy.vy = random.randrange(-50, 50)
        baddy.vx = random.randrange(-500, -100)
        self.danger.add(baddy)
        return baddy

    def spawn_star(self) -> Dwingling_star:
        star = Dwingling_star(self.visible_universe.width, random.randint(1, self.visible_universe.height))
        star.compute_RGB_sequence()
        return star


