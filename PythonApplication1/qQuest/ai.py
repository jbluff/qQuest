import random

### NPC behavior things ###
class aiTest:
    def takeTurn(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        self.owner.move(dx,dy)

