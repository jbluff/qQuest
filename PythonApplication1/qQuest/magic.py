
from qQuest.game import GAME

def castHeal(target, value) -> float:
    ''' Target is a Creature type. '''
    print("heal was cast")
    #TODO:  implement creature.heal function
    endHp = min(target.maxHp, target.hp+value)
    deltaHp = endHp - target.hp
    target.hp = endHp

    if deltaHp > 0:
        GAME.addMessage(target.name + " heals for " + str(deltaHp))
        return True
    else:
        GAME.addMessage(target.name + " is already at full HP")
        return False


