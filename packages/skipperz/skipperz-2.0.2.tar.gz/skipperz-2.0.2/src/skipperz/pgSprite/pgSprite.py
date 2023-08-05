import pygame
from . import mobile as lib_mobile
import time

class Animation():
    def __init__ (self,imageList=None):
        if imageList is None: imageList = []

        # on s'assure que toute les images sont de type pyGame.Surface
        properList=[] 
        for image in imageList:
            if  (type(image) is pygame.Surface):
                # image = image.convert_alpha()
                properList.append(image)
            else:
                #ca marche pour un nom de fichier. Peut etre dans d'autre cas
                try:
                    image = pygame.image.load(image)
                except(FileNotFoundError):
                    raise FileNotFoundError("can't find file "+str(image))
                try:
                    image = image.convert_alpha()
                except Exception:
                    print("WARNING: pygame.surface.convert_alpha failed in pgSprite.Animation")
                properList.append(image)

        # puis, on fait les choses un peu generiques
        # super().__init__(properList)
        self.imageList = properList

        self.t0 = time.time()
        self.frequency = 10  # par default, 10 image/sec.

    def addImage(self,image):
        if  isinstance(image, pygame.Surface):
            self.imageList.append(image)
        else:
            #ca marche pour un nom de fichier. Peut etre dans d'autre cas
            image = pygame.image.load(image)
            self.imageList.append(image)

    def convert_alpha(self, surface=None):
        for image_index, image  in enumerate(self.imageList) :
            if surface is None:
                self.imageList[image_index] = image.convert_alpha()
            else:
                self.imageList[image_index] = image.convert_alpha(surface)

    def nbImage(self, clock=None):
        if clock is None: clock = time.time()
        lapse = clock - self.t0

        return int((lapse * self.frequency) % len(self.imageList))

    def getImage(self, clock=None):
        return self.imageList[self.nbImage(clock)]

    # par default, on cycle lineairement, mais on peu surcharger pour plus complexe.
    # surtout je fait un sprite generique qui appele animation.update()
    def update(self):
        pass


# TODO rendre compatible avec pyGame.Sprite
class Sprite(lib_mobile.Mobile):

    def __init__(self, mobile=None, animation=None):
        if mobile is None: mobile = lib_mobile.Mobile((0, 0))
        if animation is None: animation = Animation()

        lib_mobile.Mobile.__init__(self, mobile.position)
        self.animation = animation
        self.alive = True

    def update(self, clock = None, update_clock = True):
        lib_mobile.Mobile.update(self, clock, update_clock)
        self.animation.update()

    @property
    def image(self):
        return self.animation.getImage()

    def kill(self):
        self.alive = False

    def __str__(self):
        result = lib_mobile.Mobile.__str__(self) + ", image#="+str(self.animation.nbImage())
        return result

    def display(self, screen):
        screen.blit(self.image, (self.x, self.y))

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
    
    def collide(self, otherSprite):
        return pygame.sprite.collide_mask(self, otherSprite)

    # MEthode pour tester colision entre 1 sprite (a priori le heros)
    # et tout les sprites d'une liste (les obstacles/méchant)
    # Return false si pas de colision. return le badGuy si colision
    def collideAny(self, list_of_sprites):
        for sprite in list_of_sprites :
            if self.collide(sprite):
                return sprite
        return False
