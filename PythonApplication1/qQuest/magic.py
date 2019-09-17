
from qQuest.qqGlobal import GAME, SURFACE_MAIN
from qQuest import graphics

'''
Target is a Creature
'''
def castHeal(target, value):
    
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


