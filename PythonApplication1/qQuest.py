import pygame

from qQuest import constants, graphics,  menus 
from qQuest.levels import Level
from qQuest.game import SURFACE_MAIN, CLOCK, GAME


'''
Basic object structure:
    - Game type contains
        - Levels
        - Player 
        - Viewer (generally player)
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


'''
TODO:  

- Viewer() class -- and Player(Creature,Viewer) class?
- Portals and switching levels.
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
Needed external packages (on pip):  pygame, tcod, dill, numpy
'''

def handleMainLoopEvents():

    eventsList = pygame.event.get()

    for event in eventsList:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type != pygame.KEYDOWN:
            continue

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

        if event.key == pygame.K_g:
            GAME.player.pickupObjects()

        if event.key == pygame.K_p:
            menus.PauseMenu(SURFACE_MAIN)

        if event.key == pygame.K_i:
            menus.InventoryMenu(SURFACE_MAIN, GAME.player)
        
        if event.key == pygame.K_s:
            menus.SaveLoadMenu(SURFACE_MAIN)

        if event.key == pygame.K_q:
            return "QUIT"

    return "no-action"

def exitGame():
    pygame.quit()
    quit()

def mainGameLoop():
    playerAction = "no-action"

    GAME.viewer = GAME.player # can see other Creature FOV, mostly for degbugging purposes
    GAME.viewer.recalculateFov(force=True)

    while playerAction != "QUIT":
        playerAction = handleMainLoopEvents()
            
        if playerAction == "player-moved":
            GAME.viewer.recalculateFov()
            GAME.currentLevel.takeNPCturns()

        graphics.drawGame(GAME.viewer.fovMap)
        CLOCK.tick(constants.GAME_FPS)

    exitGame()


def initializeGame():
    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    #level1 = Level("newMap1")
    #level1 = Level("mapWithPlayer")
    #level1 = Level("mapwPG")
    #level1 = Level("testMap")
    level1 = Level("mapwPIE")

    GAME.levels.append(level1)
    GAME.currentLevel = 0

    #level1.addPortal(1,1,"stairs_down")


if __name__ == "__main__":
    initializeGame()
    mainGameLoop()

    


