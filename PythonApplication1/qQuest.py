import pygame

from qQuest import constants, graphics, menus 
from qQuest.levels import Level
from qQuest.game import CLOCK, GAME


'''
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


'''
TODO:  

- partial movement -- not just tile-by-tile.
- smart walls--gfx depend on neightbors, like fow.

- Clean up assets section.  Lots of unnecessary complexity there.  Be smarter about storage and separation of assets.

- creatures need stats and such
- add other types to menus
- npcs text popups and interaction, scripting schema
- add inventory and health graphics (expand gfx past map window.)

- procedural level generation integrated to be on the fly
- moar graphic assets

- Image processing on procGen rooms for rounding etc.

- Give Monsters a "properties" section.  Not quite sure how that should work, yet.

- Support for non-square roomes 
    - this is required for reasonable use of set pieces
- Fixed piece rooms
- Directional facing of character, monsters?
- Refine map loading (set pieces, named npcs, items.)
- New monster AIs
- Area effect spells

- multi character mechanics!
'''

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
        menus.PauseMenu()

    if event.key == pygame.K_i:
        menus.InventoryMenu(GAME.player)
    
    if event.key == pygame.K_s:
        menus.SaveLoadMenu()


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
            graphics.drawGame()
        elif debugMode == 'spriteList':
            graphics.spriteDebugger()
            
        CLOCK.tick(constants.GAME_FPS)

    exitGame()


def initializeGame():
    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    if 1:
        level0 = Level("town")
        GAME.levels.append(level0)
        GAME.currentLevel = level0
        level0.placePlayerAtPortal(level0.portals[0])

        level1 = Level("mapwPIES4")
        GAME.levels.append(level1)
        level0.portals[0].destinationPortal = level1.portals[0]
        level1.portals[0].destinationPortal = level0.portals[0]
    if 0:
        level0 = Level("mapwPIES4")
        GAME.levels.append(level0)
        GAME.currentLevel = level0
        level0.placePlayerAtPortal(level0.portals[0])

        level1 = Level("mapwPIES3")
        GAME.levels.append(level1)

        level2 = Level("mapwPIES2")
        GAME.levels.append(level1)

        level0.portals[0].destinationPortal = level1.portals[0]
        level1.portals[0].destinationPortal = level0.portals[0]

        level0.portals[1].destinationPortal = level2.portals[0]
        level2.portals[0].destinationPortal = level0.portals[1]

    GAME.viewer = GAME.player # can see other Creature FOV, mostly for degbugging purposes
    #GAME.viewer.recalculateFov(force=True)

    GAME.camera = graphics.Camera(viewer=GAME.player)

if __name__ == "__main__":
    initializeGame()

    # import cProfile
    # cProfile.run('mainGameLoop()')

    mainGameLoop()#debugMode = 'spriteList')



