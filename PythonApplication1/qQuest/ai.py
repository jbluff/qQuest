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


class aiRandom(aiTemplate):
    def think(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        self.owner.scheduleMove(dx,dy)


class aiDumbAggro(aiTemplate):
    def __init__(self):
        self.thinkingDuration = 2 
        self.seenEnemy = False

    def think(self):
        dx = GAME.player.graphicX - self.owner.graphicX
        dy = GAME.player.graphicY - self.owner.graphicY

        dist = math.sqrt(dx**2 + dy**2)
        
        ATTACK_RADIUS = 5
        if (dist < ATTACK_RADIUS):
            emote = 'monsterEmote' if self.seenEnemy==0 else None

            dx = round(dx/dist)
            dy = round(dy/dist)
            self.seenEnemy = 1
            self.owner.scheduleMove(dx,dy,emoteName=emote)
        else:
            emote = 'questionEmote' if self.seenEnemy==1 else None
            self.seenEnemy = 0
            self.owner.scheduleWait(emoteName=emote)


class aiDumbCoward(aiTemplate):
    def __init__(self):
        self.thinkingDuration = 2 

    def think(self):
        dx = GAME.player.graphicX - self.owner.graphicX
        dy = GAME.player.graphicY - self.owner.graphicY

        dist = math.sqrt(dx**2 + dy**2)
        
        ATTACK_RADIUS = 5
        if (dist < ATTACK_RADIUS):
            dx = -1*round(dx/dist)
            dy = -1*round(dy/dist)
        else:
            dx, dy = 0, 0
        self.owner.scheduleMove(dx,dy)

