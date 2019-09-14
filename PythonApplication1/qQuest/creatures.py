from qQuest.qqGlobal import GAME

def deathMonster(game, monster):
    '''
    What happens when a non-player character dies?
    Monster is actor class instance.
    '''
    game.addMessage(monster.creature.name + " has been slain!")
    monster.creature = None
    monster.ai = None

class Creature:
    def __init__(self, name, hp=10, deathFunction=None):

        self.name = name
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction

    def takeDamage(self, damage):
        self.hp -= damage
        GAME.addMessage(self.name + "'s health is " + str(self.hp) + "/" + str(self.maxHp))

        if self.hp <= 0:
            if self.deathFunction:
                self.deathFunction(self.owner)

    def move(self, dx, dy):
        tileIsWall = (GAME.currentMap[self.owner.x + dx]
                        [self.owner.y + dy].blockPath == True)

        target = GAME.checkForCreature(self.owner.x + dx, self.owner.y + dy, exclude_object=self.owner)

        if target:
            GAME.addMessage(self.name + " attacks " + target.name)
            target.takeDamage(3)

        if not tileIsWall and target is None:
            self.owner.x += dx
            self.owner.y += dy