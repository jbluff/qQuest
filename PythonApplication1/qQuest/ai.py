import random

### NPC behavior things ###
class aiTest:
    def __init__(self):
        self.thinkingDuration = 5
        
    def think(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        self.owner.scheduleMove(dx,dy)

