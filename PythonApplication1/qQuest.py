import pygame
import tcod as libtcod


from qQuest import constants, qqGlobal, graphics, map_util, menus, ai
from qQuest import actors, magic
from qQuest.actors import Actor, Creature, Item, Container

from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME
from qQuest.graphics import ASSETS


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

#temporary and bad
def gameAddEnemy(coordX, coordY, name):
    inventory = Container()
    #item = Item(name=name+"'s corpse")
    #creature = Creature(name, deathFunction=lambda x: actors.deathMonster(GAME, x))
    enemy = Creature( (coordX, coordY), "evil jelly", ASSETS.a_jelly,
                     ai=ai.aiTest(), 
                     container=inventory, deathFunction=actors.deathMonster)#, item=item)
    GAME.currentObjects.append(enemy)

def gameAddItem(coordX, coordY, name):
    useFunction = lambda target: magic.castHeal(target, 5)
    #item = Item(name=name, useFunction=useFunction)
    goggles = Item( (coordX, coordY), "Goggles", ASSETS.a_goggles, 
                       useFunction=useFunction)
    GAME.currentObjects.append(goggles)


def gameInitialize():
    global PLAYER 

    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

  
    GAME.currentMap, playerFovMap = map_util.mapCreate()
    
    
    # init hero
    playerInventory = Container()
    PLAYER = Creature( (1,1), "hero", ASSETS.a_player, 
                   fovMap=playerFovMap,
                   container=playerInventory)
    PLAYER.fovCalculate = True

    GAME.currentObjects.append(PLAYER)

    # init the enemy
    gameAddEnemy(5,7,"frank")
    gameAddEnemy(10,3,"george")

    gameAddItem(4,4,"goggles")




if __name__ == "__main__":
    gameInitialize()
    gameMainLoop()

    


