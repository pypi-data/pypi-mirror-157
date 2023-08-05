import random

import pygame.display
from pgSprite import pgSprite
import  params

class BadGuy(pgSprite.Sprite):

    # variable statique. ils ont tous la meme anim
    animationBadGuy = pgSprite.Animation(params.bad_guy_1_animation)
    animationBadGuy.frequency=2

    #listBadGuys =[]

    #Factory that send bad guy with random trajectory
    #That is partly random initial Y, speed and acceleration
    @staticmethod
    def newBadGuyRandom() -> 'BadGuy':
        sprite = BadGuy()
        sprite.animation = BadGuy.animationBadGuy
        sprite.position.x = 1000
        sprite.position.y = random.randrange(50, 750, 1)
        sprite.speed.x = random.randrange(-200, -40)
        sprite.speed.y = random.randrange(-60, +60)
        sprite.acceleration.x = random.randrange(-80, +80)
        sprite.acceleration.y = random.randrange(-80, +80)
        
        if paramValid(sprite):
            BadGuy.listBadGuys.append(sprite)
            return sprite
        else:
            return BadGuy.newBadGuyRandom()

     #on surcharge update pour tuer le sprite s'il sort par le fond   
    def update(self, clock = None, update_clock = True):
        super().update(clock,update_clock)
        if self.x < -self.rect.width :
            self.kill()

def pos(mobile:pgSprite.Sprite ,t):
    """ position qu'un mobile aura au temp t
    renvois un euclyd.Vector2 """
    return mobile.position + t*mobile.speed + 0.5*t*t*mobile.acceleration
        

     #   Les param du sprite, au départ sont en partie aleatoire
     # plutot que de me prendere le chou, je teste la position anticipée
     # en 3 instant different et je rejette si ca sort d'un certain cadre
def paramValid(sprite: pgSprite.Sprite):
        # on teste a 3 moment diferent (2s,4s,6s) si le sprite ne sort pas verticalement
        for t in (2,4,6):
            forcastPos = pos(sprite, t)
            if forcastPos.y >pygame.display.get_surface().get_height() or forcastPos.y < -20 :
                return False
            if t==2 and forcastPos.x < 100: #too fast
                return False

        if pos(sprite, 10).x > 0: # si le sprite n'est pas sortie par le fond apres 10s
            return False
        #Si le sprite n'a pas ete rejete, on renvoi True
        return True
            


                
            
        
    
