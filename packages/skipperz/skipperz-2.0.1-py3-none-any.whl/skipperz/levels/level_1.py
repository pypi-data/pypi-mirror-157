from levels.level import Level
from FX.tileArray import TileArray
from FX import sound
from skip_libs import badGuys
import random
import params
import pygame


class Universe_rect: #  TODO a remplacer par game.rectangle
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Level1 (Level):
    TILE_COUNT = 1

    def __init__(self,  visible_universe: "rectangle(width, height)"):
        Level.__init__(self)
        # le background est un damage horizontale de n fois la meme image

        picture = pygame.image.load(params.picture1)
        self.tileArray = TileArray(self.TILE_COUNT, 1, [picture])

        if visible_universe is None:
            self.visible_universe = Universe_rect(1000, 800)
        else:
            self.visible_universe = visible_universe

        for x in range(self.TILE_COUNT):
            self.tileArray.setTileImageIndex(0, x, 0)
            self.scrollingSpeed = 80  # 30 pix/second

    def start(self):
        Level.start(self)
        sound.play_music(params.music1)

    def get_offset(self) -> int:
        return int(self.elapsed_time * self.scrollingSpeed) - self.visible_universe.width

    def update(self) -> bool:
        """Update position of sprite, remove those outside of screen
        Return False if the end of level is reached"""
        Level.update(self)
        dead_sprites = []
        for sprite_BadGuy in self.objects:
            sprite_BadGuy.update()
            if not sprite_BadGuy.alive:
                dead_sprites.append(sprite_BadGuy)
        for sprite_BadGuy in dead_sprites:
            self.objects.remove(sprite_BadGuy)
            self.score(10)

        return self.tileArray.tileWidth * self.TILE_COUNT > self.get_offset()
        # return self.elapsed_time < self.TOTAL_DURATION

    def draw_background(self, dest):
        dest.fill((0, 0, 0, 0))
        self.tileArray.display(dest, self.get_offset(), 0)

    def drawBaddies(self, dest):
        for sprite_BadGuy in self.objects:
            sprite_BadGuy.display(dest)

    def draw(self, dest):
        self.draw_background(dest)
        self.drawBaddies(dest)

    def spawn(self):
        if not hasattr(self, "time_last_spawn"):
            self.time_last_spawn = self.time_function()

        if self.tileArray.tileWidth * self.TILE_COUNT  < self.get_offset() + 1000:
            return None

        if self.time_function() - self.time_last_spawn > 2:  # spawn bad guy each 2 second
            self.time_last_spawn = self.time_function()
            baddy = self.spawn_bad_guy()
            # self.objects.add(baddy)
            return baddy
        else:
            return None

    def spawn_bad_guy(self) -> badGuys.BadGuy:
        """"The bad guy fly horizontally across the screen (right to left)"""
        baddy = badGuys.BadGuy()
        baddy.animation = badGuys.BadGuy.animationBadGuy
        baddy.x = self.visible_universe.width + baddy.rect.width
        baddy.y = random.randrange(0, self.visible_universe.height - baddy.rect.height)
        baddy.vy = 0
        baddy.vx = random.randrange(-400, -100)
        self.danger.add(baddy)
        return baddy
