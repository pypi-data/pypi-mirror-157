import time
from game import game_in_progress


# to identify situation where Level.spawn return several objects
class SpawnTuple (tuple):
    pass


class Level:
    def __init__(self):
        self.starting_time = None
        self.current_time = None
        self.time_function = time.time  # we need a function. Not a call to said function
        self.objects = set()  # objects can be badies, bonus etc... feature obj.update, obj.x, obj,y, obj.display
        self.danger = set()  # subset of object. things that kill on collision, feature obj.rect and obj.collide
        self.collectable = set()  # subset of object. Things that can colide but don't kill

    @property
    def elapsed_time(self):
        if self.starting_time is None or self.current_time is None:
            return None
        return self.current_time - self.starting_time

    def start(self):
        self.starting_time = self.time_function()
        self.current_time = self.time_function()

    def update(self) -> bool:
        """"update the situation
        Return false if the level is over. Hence the loop true a level can be `while level.update():` """
        self.current_time = self.time_function()
        if spawned := self.spawn():
            self.objects.add(spawned)
        return True

    def draw(self, dest):
        pass

    def spawn(self) -> object:
        """" this is where we add things to self.objects"""
        return None

    @staticmethod
    def score(amount):
        game_in_progress.score += amount
