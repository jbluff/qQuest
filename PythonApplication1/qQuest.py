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


'''
TODO:  
- floating movement -- this requires a real change in how actors and time work
- "smart" wall and fov sprite selections-- choice of sprite depends on neighbors
- Clean up assets section.  Lots of unnecssary complexity there.  Be smarter about storate and separation of assets.
- Refactoring menu list items
    - adding text-entry menu list items

- Image processing on procGen rooms for rounding etc.

- Give Monsters a "properties" section.  Not quite sure how that should work, yet.

- Support for non-square roomes 
    - this is required for reasonable use of set pieces
- Fixed piece rooms
- Directional facing of character, monsters?
- Refine map loading (set pieces, named npcs, items.)
- New monster AIs
- Area effect spells
'''

def handleInputEvents():
    eventsList = pygame.event.get()

    for event in eventsList:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type != pygame.KEYDOWN:
            continue

        if event.key == pygame.K_UP:
            GAME.player.scheduleMove(0, -1)

        if event.key == pygame.K_DOWN:
            GAME.player.scheduleMove(0, 1)

        if event.key == pygame.K_LEFT:
            GAME.player.scheduleMove(-1, 0)

        if event.key == pygame.K_RIGHT:
            GAME.player.scheduleMove(1, 0)

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

        if event.key == pygame.K_y:
            entryPortal = GAME.player.isOnPortal()
            if entryPortal is None:
                return
            GAME.transitPortal(entryPortal)

    return "no-action"

def exitGame():
    pygame.quit()
    quit()

def mainGameLoop():
    playerAction = ""

    while playerAction != "QUIT":
        playerAction = handleInputEvents()
            
        GAME.currentLevel.takeCreatureTurns()
        GAME.camera.updatePositionFromViewer()

        graphics.drawGame()
        CLOCK.tick(constants.GAME_FPS)

    exitGame()


def initializeGame():
    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    #level1 = Level("newMap1")
    #level1 = Level("mapWithPlayer")
    #level1 = Level("mapwPG")
    #level1 = Level("testMap")
    #level1 = Level("mapwPIE")

    # level1 = Level("mapwPIES", initPlayer=True)
    # GAME.levels.append(level1)
    # GAME.currentLevel = 0

    # level2 = Level("mapwPIES3", initPlayer=False)
    # GAME.levels.append(level2)

    level1 = Level("mapwPIES3")#, initPlayer=False)
    GAME.levels.append(level1)
    GAME.currentLevel = level1
    level1.placePlayerAtPortal(level1.portals[0])

    level2 = Level("mapwPIES2")#, initPlayer=False)
    GAME.levels.append(level1)

    level1.portals[0].destinationPortal = level2.portals[0]
    level2.portals[0].destinationPortal = level1.portals[0]

    GAME.viewer = GAME.player # can see other Creature FOV, mostly for degbugging purposes
    #GAME.viewer.recalculateFov(force=True)

    GAME.camera = graphics.Camera(viewer=GAME.player)

if __name__ == "__main__":
    initializeGame()

    # import cProfile
    # cProfile.run('mainGameLoop()')

    mainGameLoop()



