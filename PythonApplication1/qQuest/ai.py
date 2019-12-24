import random
import math

from qQuest.game import GAME

### NPC behavior things ###
class aiTemplate():
    def __init__(self):
        self.thinkingDuration = 5
        # WILL ATTACK CLASSES

    def think(self):
        raise NotImplementedError('Filled in by child class.')


class aiTest(aiTemplate):
    def think(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        self.owner.scheduleMove(dx,dy)


class aiDumbAggro(aiTemplate):
    def __init__(self):
        self.thinkingDuration = 2 

    def think(self):
        dx = GAME.player.graphicX - self.owner.graphicX
        dy = GAME.player.graphicY - self.owner.graphicY

        dist = math.sqrt(dx**2 + dy**2)
        
        ATTACK_RADIUS = 5
        if (dist < ATTACK_RADIUS):
            dx = round(dx/dist)
            dy = round(dy/dist)
        else:
            dx, dy = 0, 0
        self.owner.scheduleMove(dx,dy)

