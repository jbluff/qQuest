
from qQuest.qqGlobal import GAME, SURFACE_MAIN
from qQuest import graphics

'''
Target is a creature
'''
def castHeal(target, value):
    
    
    endHp = min(target.maxHp, target.hp+value)
    deltaHp = endHp - target.hp
    target.hp = endHp
    GAME.addMessage(target.name + " heals for " + str(deltaHp))

    graphics.drawGameMessages()
    

    #TODO actually heal

