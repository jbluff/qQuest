import pygame
import tcod as libtcod
import json, os, datetime, pickle

from qQuest import constants, graphics, map_util, menus
from qQuest.levels import Level
from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME
#from qQuest import constants, qqGlobal, graphics, map_util, menus, ai
#from qQuest import actors, magic
#from qQuest.actors import Actor, Creature, Item, Container, Equipment
#from qQuest.graphics import ASSETS
#from qQuest.lib.itemLib import ITEMS
#from qQuest.lib.monsterLib import MONSTERS


'''
TODO:  

- menus w/ text input
- Save & load games
- Support for non-square roomes 
    - this is required for reasonable use of set pieces
- Fixed piece rooms
- Camera stuff
- Image processing on procGen rooms for rounding etc.
- New monster AIs
- Area effect spells
- Directional facing of character, monsters?
- Refine map loading (set pieces, named npcs, items.)
'''
'''
Needed external packages (on pip):  pygame, tcod
'''

def gameHandleKeys():

    # get player input
    eventsList = pygame.event.get()

    # process input
    for event in eventsList:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                GAME.player.move(0, -1)
                return "player-moved"

            if event.key == pygame.K_DOWN:
                GAME.player.move(0, 1)
                return "player-moved"

            if event.key == pygame.K_LEFT:
                GAME.player.move(-1, 0)
                return "player-moved"

            if event.key == pygame.K_RIGHT:
                GAME.player.move(1, 0)
                return "player-moved"

            # pickup objects
            # TODO:  break this into a subroutine
            if event.key == pygame.K_g:
                objs = GAME.currentLevel.objectsAtCoords(GAME.player.x, GAME.player.y)
                for obj in objs:
                    if obj.item:
                        obj.pickup(GAME.player)

            # pause menu
            if event.key == pygame.K_p:
                menus.PauseMenu(SURFACE_MAIN)

            # inventory menu
            if event.key == pygame.K_i:
                menus.InventoryMenu(SURFACE_MAIN, GAME.player)
            
            if event.key == pygame.K_s:
                menus.SaveLoadMenu(SURFACE_MAIN)

            if event.key == pygame.K_q:
                return "QUIT"

    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():

    playerAction = "no-action"

    viewer = GAME.player # can see other Creature FOV, mostly for degbugging purposes
    map_util.mapCalculateFov(viewer)

    while playerAction != "QUIT":
       
        playerAction = gameHandleKeys()
            
        if playerAction == "player-moved":
            map_util.mapCalculateFov(viewer)
            for gameObj in GAME.currentLevel.objects:
                if gameObj.ai:
                    gameObj.ai.takeTurn()

        graphics.drawGame(viewer.fovMap)
        CLOCK.tick(constants.GAME_FPS)

    gameExit()


def gameInitialize():
    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    #level1 = Level("newMap1")
    #level1 = Level("mapWithPlayer")
    #level1 = Level("mapwPG")
    #level1 = Level("testMap")
    level1 = Level("mapwPIE")

    GAME.levels.append(level1)
    GAME.currentLevel = level1

# def gameSave(saveName='default'):
#     dt = datetime.datetime.now()
#     dtString = dt.strftime('%Y%H%M%M')

#     fileName = dtString + '_' + saveName + '.sav'
#     filePath = os.path.join(os.path.dirname(__file__),"..","saves",fileName)
#     with open(filePath, 'wb') as f:
#         pickle.dump(GAME, f)
#     pass


if __name__ == "__main__":
    #gameSave()
    gameInitialize()
    gameMainLoop()

    


