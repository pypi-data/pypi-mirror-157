import pygame
import array

# Cette classe represente un tableau de bitmap a 2 dimensions.
# Donc, ca represente un gros bitmap compose d'un damier de petit bitmap(tile)
# self.imageList contient la liste des tile dispo (sans doublon, max 65000 elements)
# Le damier contien en fait les index des tiles dans image list
# It is assumed that all images are the same size (the size of `imageList[0]

# TODO self.array shoud use numpy as it will be used anyway by other part pf the game

class TileArray:

    # constructeur. Du genre TileArray(10,20,myImageList)
    def __init__(self, width, height, imageList=[]):
        self.array = []
        for column in range(width):
            self.array.append(array.array('H'))  # c'est un tableau de mot de 2 octects non signes
            for line in range(height):
                self.array[column].append(0)
        self.imageList = imageList
        try:
            self.tileWidth = imageList[0].get_width()
            self.tileHeight = imageList[0].get_height()
        except:
            self.tileWidth = 20
            self.tileHeight = 20

    def getTile(self, x, y) -> pygame.Surface:
        result = self.imageList[self.array[x][y]]
        if isinstance(result, pygame.Surface):
            return result
        else:
            return result.surface
        # return self.imageList[self.array[x][y]]

    def getTileImageIndex(self, x, y) -> int:
        return self.array[x][y]

    def setTileImageIndex(self, imageIndex, x, y):
        self.array[x][y] = imageIndex

    # affiche la partie du "monde" present a l'ecran
    # xScene, yScene sont les coordonee de la zone affichee a l'interieur du "Monde" que represente le tileArray
    # cet algo affiche sur tout le "screen"
    def display(self, screen, xScene, yScene):
        x = -(xScene % self.tileWidth)

        while x < screen.get_width():
            xCase = (x + xScene) // self.tileWidth  # reminder: // is floor division
            y = -(yScene % self.tileHeight)

            while y < screen.get_height():
                yCase = (y + yScene) // self.tileHeight
                try:
                    tile = self.getTile(xCase, yCase)
                    screen.blit(tile, (x, y))
                except(IndexError):
                    pass # if (x,y) out of bound, nevermind. We just don't display
                y += self.tileHeight

            x += self.tileWidth

    def width_in_pixel(self):
        return len(self.array) * self.tileWidth

    def height_in_pixel(self):
        try:
            return len(self.array[0]) * self.tileHeight
        except(IndexError):
            return 0