import time
from .vector2d import Vector2, enforce_vector2
        
                        
class Mobile:

    @enforce_vector2(1)
    def __init__(self, position: Vector2):
        self.position: Vector2
        self.speed: Vector2
        self.acceleration: Vector2

        self.position = position
        self.speed = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        self.t0 = time.time()  #  top a partir duquel on mesure les temps.
            # Comportement par defaut: c'est le temp du dernier update

    # met a jour position et speed en fonction tu temps ecoule
    # Par defaut, clock = now
    def update(self, clock = None, update_clock = True):
        if clock is None: clock = time.time()
        lapse = clock - self.t0

        if self.speed is not None:
            self.position += lapse * self.speed
        if self.acceleration is not None:
            self.speed += lapse * self.acceleration

        if update_clock: # `update_clock = False` allow some kind of simulation from t0
            self.t0 = clock # t0 = date de dernier update

    def __str__(self):
        return mobileToStr(self)


    #des racourcis
    @property
    def x(self):
        return self.position.x
    @x.setter
    def x(self, new_x): self.position.x = new_x

    @property
    def y(self): return self.position.y
    @y.setter
    def y(self, new_y): self.position.y = new_y

    @property
    def vx(self): return self.speed.x
    @vx.setter
    def vx(self, new_vx): self.speed.x = new_vx

    @property
    def vy(self): return self.speed.y
    @vy.setter
    def vy(self, new_vy): self.speed.y = new_vy
    
    @property
    def ax(self): return self.acceleration.x
    @ax.setter
    def ax(self, new_ax): self.acceleration.x = new_ax
    
    @property
    def ay(self): return self.acceleration.y
    @ay.setter
    def ay(self, new_ay): self.acceleration.y = new_ay


#class MobileSurRail(Mobile):
    #TODO l'update est diferent
