import pygame
import tcod as libtcod


from qQuest import constants, qqGlobal, graphics, map_util, menus, ai
from qQuest import actors, magic
from qQuest.actors import Actor, Creature, Item, Container, Equipment

from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME
from qQuest.graphics import ASSETS

from qQuest.lib.itemLib import ITEMS
from qQuest.lib.monsterLib import MONSTERS

def gameHandleKeys():

    # get player input
    eventsList = pygame.event.get()

    # process input
    for event in eventsList:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN:
            # arrow key up -> move player up
            if event.key == pygame.K_UP:
                PLAYER.move(0, -1)
                return "player-moved"

            # arrow key down -> move player down
            if event.key == pygame.K_DOWN:
                PLAYER.move(0, 1)
                return "player-moved"

            # arrow key left -> move player left
            if event.key == pygame.K_LEFT:
                PLAYER.move(-1, 0)
                return "player-moved"

            # arrow key right -> move player right
            if event.key == pygame.K_RIGHT:
                PLAYER.move(1, 0)
                return "player-moved"

            # pickup objects
            # TODO:  break this into a subroutine
            if event.key == pygame.K_g:
                objs = GAME.objectsAtCoords(PLAYER.x, PLAYER.y)
                for obj in objs:
                    if obj.item:
                        obj.pickup(PLAYER)

            # pause menu
            if event.key == pygame.K_p:
                menus.pause(GAME)

            # inventory menu
            if event.key == pygame.K_i:
                menus.inventory(SURFACE_MAIN, PLAYER)
            
            if event.key == pygame.K_q:
                return "QUIT"
    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():

    GAME.addMessage("whatup", constants.COLOR_WHITE)
    playerAction = "no-action"

    while playerAction != "QUIT":
       
        playerAction = gameHandleKeys()

        map_util.mapCalculateFov(PLAYER)#, fovMap=FOV_MAP)
        PLAYER.fovCalculate = False

        if playerAction == "player-moved":
            for gameObj in GAME.currentObjects:
                if gameObj.ai:
                    gameObj.ai.takeTurn()

        graphics.drawGame(PLAYER.fovMap)

        CLOCK.tick(constants.GAME_FPS)

    gameExit()


def gameAddEnemy(coordX, coordY, name, uniqueName=None):
    monsterDict = MONSTERS[name]
    name = monsterDict['name']
    if uniqueName:
        name = uniqueName + " the " + name

    inventory = Container(**monsterDict['kwargs'])
    enemy = Creature( (coordX, coordY), name, monsterDict['animation'],
                     ai=getattr(ai,monsterDict['ai'])(), 
                     container=inventory, deathFunction=monsterDict['deathFunction'])    #item = Item(name=name+"'s corpse")
    GAME.currentObjects.append(enemy)

def gameAddItem(coordX, coordY, name):
    itemDict = ITEMS[name]
    if 'equipment' in itemDict.keys():
        item = Equipment( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
                       **itemDict['kwargs'])
    else:
        item = Item( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
                       useFunction=itemDict['useFunction'], **itemDict['kwargs'])

    GAME.currentObjects.append(item)



def gameInitialize():
    global PLAYER #, GAME

    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    GAME.currentMap, playerFovMap = map_util.mapCreate()
    #GAME.currentFovMap = playerFovMap
    setattr(GAME, "currentFovMap", playerFovMap)

    # init hero
    playerInventory = Container()
    PLAYER = Creature( (1,1), "hero", ASSETS.a_player, 
                   fovMap=playerFovMap,
                   container=playerInventory)
    PLAYER.fovCalculate = True

    GAME.currentObjects.append(PLAYER)

    # init the enemy
    gameAddEnemy(5,7,"jelly", uniqueName="frank")
    gameAddEnemy(10,3,"jelly", uniqueName="george")
    gameAddEnemy(10,4,"demon", uniqueName="Mephisto, lord of terror")

    gameAddItem(4,4,"goggles")

    gameAddItem(8,4,"healingPotion")



if __name__ == "__main__":
    gameInitialize()
    gameMainLoop()

    


