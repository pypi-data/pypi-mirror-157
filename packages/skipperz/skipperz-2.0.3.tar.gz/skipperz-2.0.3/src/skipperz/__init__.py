import os
folder = os.path.dirname(__file__)
os.chdir(folder)
print("Skipperz 2 is running in this directory: ", folder)
from . import game
game.init()
