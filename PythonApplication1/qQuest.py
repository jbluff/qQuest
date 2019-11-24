import pygame
import tcod as libtcod
import json
import os

from qQuest import constants, qqGlobal, graphics, map_util, menus, ai
from qQuest import actors, magic
from qQuest.actors import Actor, Creature, Item, Container, Equipment
from qQuest.levels import Level

from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME
from qQuest.graphics import ASSETS

from qQuest.lib.itemLib import ITEMS
from qQuest.lib.monsterLib import MONSTERS


'''
TODO:  
- Finish map loading, including player & monster location
    - expand to generally load things from the libraries
- Camera stuff
- Fixed piece sooms
- Save & load games
- Support for non-square roomes 
    - this is required for reasonable use of set pieces
- Image processing on procGen rooms for rounding etc.
- New monster AIs
- Area effect spells
- Directional facing of character, monsters?
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
            # arrow key up -> move player up
            if event.key == pygame.K_UP:
                GAME.player.move(0, -1)
                return "player-moved"

            # arrow key down -> move player down
            if event.key == pygame.K_DOWN:
                GAME.player.move(0, 1)
                return "player-moved"

            # arrow key left -> move player left
            if event.key == pygame.K_LEFT:
                GAME.player.move(-1, 0)
                return "player-moved"

            # arrow key right -> move player right
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
            
            if event.key == pygame.K_q:
                return "QUIT"
    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():

    playerAction = "no-action"

    viewer = GAME.player # can see other Creature FOV, mostly for degbugging purposes

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
    level1 = Level("mapWithPlayer")
    GAME.levels.append(level1)
    GAME.currentLevel = level1

    # init hero
    #level1.addPlayer(15,2)

    # init the enemy
    level1.addEnemy(15,4,"jelly", uniqueName="frank")

    level1.addItem(16,2,"goggles")
    level1.addItem(17,2,"healingPotion")

    level1.addEnemy(15,10,"demon", uniqueName="Mephisto, lord of terror")


if __name__ == "__main__":
    gameInitialize()
    gameMainLoop()

    


