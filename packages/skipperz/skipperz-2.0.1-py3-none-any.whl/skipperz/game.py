
class Game:
    MENU = 0   # I make no enum as code completion is easier this way
    FOR_EACH_LEVEL = 1
    WHILE_LEVEL_UPDATE = 2

    def __init__(self, screen_rectangle=None):
        self.score = 0
        self.loop_level = 0
        self.screen_rectangle = screen_rectangle


game_in_progress: Game


def init(screen_rectangle=None):
    global game_in_progress
    game_in_progress = Game(screen_rectangle)
