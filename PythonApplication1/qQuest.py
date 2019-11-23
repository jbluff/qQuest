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
- Separate out Level() and Game() classes.  One game can have several levels
    - CurrentEntities in a game, Entities in a level
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
                #PLAYER.move(0, -1)
                GAME.player.move(0, -1)
                return "player-moved"

            # arrow key down -> move player down
            if event.key == pygame.K_DOWN:
                #PLAYER.move(0, 1)
                GAME.player.move(0, 1)
                return "player-moved"

            # arrow key left -> move player left
            if event.key == pygame.K_LEFT:
                #PLAYER.move(-1, 0)
                GAME.player.move(-1, 0)
                return "player-moved"

            # arrow key right -> move player right
            if event.key == pygame.K_RIGHT:
                #PLAYER.move(1, 0)
                GAME.player.move(1, 0)
                return "player-moved"

            # pickup objects
            # TODO:  break this into a subroutine
            if event.key == pygame.K_g:
                
                #objs = GAME.currentLevel.objectsAtCoords(PLAYER.x, PLAYER.y)
                objs = GAME.currentLevel.objectsAtCoords(GAME.player.x, GAME.player.y)
                for obj in objs:
                    if obj.item:
                        
                        #obj.pickup(PLAYER)
                        obj.pickup(GAME.player)

            # pause menu
            if event.key == pygame.K_p:
                menus.PauseMenu(SURFACE_MAIN)

            # inventory menu
            if event.key == pygame.K_i:
                
                #menus.InventoryMenu(SURFACE_MAIN, PLAYER)
                menus.InventoryMenu(SURFACE_MAIN, GAME.player)
            
            if event.key == pygame.K_q:
                return "QUIT"
    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():
    #global PLAYER
    playerAction = "no-action"
    #viewer = PLAYER # can see other Creature FOV for degbugging purposes
    viewer = GAME.player

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


# '''
#     Creates NPC characters by type, looking qp info in a library file.
# '''
# def gameAddEnemy(coordX, coordY, name, uniqueName=None):
#     monsterDict = MONSTERS[name]
#     name = monsterDict['name']
#     if uniqueName:
#         name = uniqueName + " the " + name

#     inventory = Container(**monsterDict['kwargs'])
#     enemy = Creature( (coordX, coordY), name, monsterDict['animation'],
#                      ai=getattr(ai,monsterDict['ai'])(), 
#                      container=inventory, deathFunction=monsterDict['deathFunction'],
#                      fovMap=map_util.createFovMap(GAME.currentLevel.map))    
#     GAME.currentLevel.objects.append(enemy)

# '''
#     Creates Items by type, looking up info in a library file.
# '''
# def gameAddItem(coordX, coordY, name):
#     itemDict = ITEMS[name]
#     if 'equipment' in itemDict.keys():
#         item = Equipment( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
#                        **itemDict['kwargs'])
#     else:
#         item = Item( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
#                        useFunction=itemDict['useFunction'], **itemDict['kwargs'])

#     GAME.currentLevel.objects.append(item)

# '''
#     Only call this once!  Creates a global/singleton.
# '''
# def gameAddPlayer(x,y):
#     global PLAYER

#     playerInventory = Container()
#     playerFovMap = map_util.createFovMap(GAME.currentLevel.map)
#     PLAYER = Creature( (x,y), "hero", ASSETS.a_player, 
#                    fovMap=playerFovMap,
#                    container=playerInventory)
#     setattr(GAME.currentLevel, "currentFovMap", playerFovMap)
#     map_util.mapCalculateFov(PLAYER)


#     GAME.currentLevel.objects.append(PLAYER)


def gameInitialize():
    # filePath = os.path.join(os.path.dirname(__file__),"levels","testLevelE.lvl")

    # with open(filePath, "r") as levelFile:
    #     levelDict = json.load(levelFile)

    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    #levelDict = map_util.loadLevelFile("testLevel")
    levelDict = map_util.loadLevelFile("newMap1")
    level1 = Level(GAME, levelDict)#, activeFovMap)
    #level1.map = map_util.loadLevel(levelDict)
    #currentLevel.
    GAME.currentLevel = level1
    #GAME.map = map_util.loadLevel(levelDict)

    # init hero
    level1.addPlayer(15,2)

    # init the enemy
    level1.addEnemy(15,4,"jelly", uniqueName="frank")
    #gameAddEnemy(10,3,"jelly", uniqueName="george")
    #gameAddEnemy(10,4,"demon", uniqueName="Mephisto, lord of terror")

    level1.addItem(16,2,"goggles")
    level1.addItem(17,2,"healingPotion")


if __name__ == "__main__":
    gameInitialize()
    gameMainLoop()

    


