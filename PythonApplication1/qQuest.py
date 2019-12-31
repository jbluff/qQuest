
''' This module is the place where the game starts.  It makes a bunch of large
singletons (GAME and the graphics surfaces, namely).  It parses player input. 
It starts the main game loop.


Basic Class & structure:
    - Game type contains
        - Levels
        - Player 
        - Viewer (generally player)
        - Camera
        and is the principal thing that supports saving, loading, and changing levels

    - Level type contains
        - Actor objects, which are graphical things
        - Include Creatures, which can move, and Items, which cannot
            - the Player is a particular Creature, which is both an object in the Level and specially known by Game
          
    - Actors contain a reference back to the Level they exist in.

    - Creatures can have, as attributes
        - Containers, which are collections of Items
        - AI objects, which can tell Creatures how to move
       
    - Items (and subclass Equipment), can contain Magic
'''

import pygame
from pygame.locals import DOUBLEBUF, FULLSCREEN

from qQuest import graphics, menus, constants
from qQuest.levels import Level
from qQuest.game import GAME



SURFACE_MAIN = pygame.display.set_mode((constants.TOTAL_WIDTH_P,                                                            constants.TOTAL_HEIGHT_P ),
                                        FULLSCREEN | DOUBLEBUF)

SURFACE_MAP = pygame.Surface((constants.CAMERA_WIDTH_P, constants.CAMERA_HEIGHT_P))
SURFACE_CHYRON = pygame.Surface((constants.TOTAL_WIDTH_P, constants.CHYRON_HEIGHT_P))

menus.DEFAULT_SURFACE = SURFACE_MAIN


def handleMovementInputs():
    pressedKeys = pygame.key.get_pressed()
    move = [0,0]
    if pressedKeys[pygame.K_UP]:
        move[1] -= 1

    if pressedKeys[pygame.K_DOWN]:
        move[1] += 1

    if pressedKeys[pygame.K_LEFT]:
        move[0] -= 1

    if pressedKeys[pygame.K_RIGHT]:
        move[0] += 1

    if move != [0,0]:
        GAME.player.scheduleMove(*move)

def handleOtherGameInputs(event):
    if event.key == pygame.K_g:
        GAME.player.pickupObjects()

    if event.key == pygame.K_y:
        entryPortal = GAME.player.isOnPortal()
        if entryPortal is None:
            return
        GAME.transitPortal(entryPortal)

def handleMenuInputs(event):
    if event.key == pygame.K_p:
        menus.PauseMenu(SURFACE_MAIN)

    if event.key == pygame.K_i:
        menus.InventoryMenu(SURFACE_MAIN, GAME.player)
    
    if event.key == pygame.K_s:
        menus.SaveLoadMenu(SURFACE_MAIN, GAME)

    if event.key == pygame.K_h:
        menus.HelpMenu(SURFACE_MAIN)

def handleInputEvents():
    eventsList = pygame.event.get()

    for event in eventsList:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type != pygame.KEYDOWN:
            continue

        if event.key == pygame.K_q:
            return "QUIT"

        handleMovementInputs()
        handleOtherGameInputs(event)
        handleMenuInputs(event)
    return "no-action"

def exitGame():
    pygame.quit()
    quit()

def mainGameLoop(debugMode=None):
    playerAction = ""

    while playerAction != "QUIT":
        playerAction = handleInputEvents()
            
        GAME.currentLevel.takeCreatureTurns()
        GAME.camera.updatePositionFromViewer()

        if debugMode is None:
            graphics.drawGame(SURFACE_MAIN, SURFACE_MAP, SURFACE_CHYRON, GAME)
        elif debugMode == 'spriteList':
            graphics.spriteDebugger(SURFACE_MAIN)
            
        constants.CLOCK.tick(constants.GAME_FPS)

    exitGame()


def initializeGame():
    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    if 1:
        level0 = Level("town3")
        GAME.levels.append(level0)
        GAME.currentLevel = level0
        level0.placePlayerAtPortal(level0.portals[1])

        level1 = Level("mapwPIES4")
        GAME.levels.append(level1)
        GAME.couplePortals(level0.portals[0], level1.portals[0])

        level2 = Level("mapwPIES3")
        GAME.levels.append(level2)
        GAME.couplePortals(level1.portals[1], level2.portals[0])

    GAME.viewer = GAME.player 
    GAME.camera = graphics.Camera(viewer=GAME.player)


if __name__ == "__main__":
    initializeGame()

    # import cProfile
    # cProfile.run('mainGameLoop()')

    mainGameLoop()#debugMode = 'spriteList')



