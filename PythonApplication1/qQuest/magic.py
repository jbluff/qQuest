
from qQuest import graphics
from qQuest.game import GAME, SURFACE_MAIN


'''
Target is a Creature
'''
def castHeal(target, value):
    print("heal was cast")
    #TODO:  implement creature.heal function
    endHp = min(target.maxHp, target.hp+value)
    deltaHp = endHp - target.hp
    target.hp = endHp

    if deltaHp > 0:
        GAME.addMessage(target.name + " heals for " + str(deltaHp))
        graphics.drawGameMessages()
        return True
    else:
        GAME.addMessage(target.name + " is already at full HP")
        graphics.drawGameMessages()
        return False


