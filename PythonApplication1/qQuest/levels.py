import json
import os
import itertools
import random
from typing import List, Tuple

import numpy as np
import tcod as libtcod

from qQuest import ai, constants

from qQuest.constants import SpriteDict 
from qQuest.characters import Creature, Combatant, Conversationalist, PlayerClass, Viewer
from qQuest.items import Item, Equipment, Container
from qQuest.game import GAME
from qQuest.graphics import ASSETS, Actor #, compileBackgroundTiles

from qQuest.lib.itemLib import ITEMS
from qQuest.lib.characterLib import CHARACTERS, NAMES
from qQuest.lib.portalLib import PORTALS 
from qQuest.lib.tileLib import TILES 


class Portal(Actor):
    ''' This class represents a location at which a creature can move rapidly
    from one location and another.  These instances point at another instance
    of the same type, generally (but not necessarily) in a different level.

    Should this actually subclass Tile?  They might be see-thru or not.
    '''
    numPortals = 0

    def __init__(self, *args, destinationPortal=None, **kwargs): #: Portal=
        
        self.uniqueID = f'portal{Portal.numPortals}'
        Portal.numPortals += 1

        super().__init__(*args, **kwargs)
        self.destinationPortal = destinationPortal
         
    def pickup(self, actor: Actor) -> None:
        return


class Tile(Actor):
    ''' Tiles are Actor instances designed, principally, for walls and floors.
    They are used to determine where a Creature and move and the influence of the
    level on what a Viewer can see.  They are drawn beneath the other Actors,
    and we expect one to be defined for every cell.'''

    def __init__(self, pos: Tuple[int], blocking=False, seeThru=True, **kwargs):
        self.blocking = blocking
        self.seeThru = seeThru
        super().__init__(pos, **kwargs)


class Level:
    numLevels = 0

    def __init__(self, levelFileName: str, loadFromFile: bool=True):
        self.levelName = levelFileName

        self.objects = [] #should this be a set?   would it simplify deletion?
        self.portals = []

        if loadFromFile:
            self.loadLevelFile()
            self.parseLevelDict()

        self.uniqueID = f'level{Level.numLevels}'
        Level.numLevels += 1

    def loadLevelFile(self) -> None:
        ''' Loads self.levelDict dictionary from a saved .lvl file '''
        filePath = os.path.join(os.path.dirname(__file__),"..","levels",self.levelName+".lvl")
        with open(filePath, "r") as levelFile:
            self.levelDict = json.load(levelFile)
        levelFile.close()

    def parseLevelDict(self) -> None:
        ''' This parses the loaded level dictionary and populates the Level
        instances tiles.  Floors, walls, items, monsters, portals.  All as
        specified in the loaded dictionary.'''

        levelArray = self.levelDict["level"]
        decoder = self.levelDict["decoderRing"]

        self.mapHeight = len(levelArray)
        self.mapWidth = len(levelArray[0])

        floorTile = ""#Tile("s_floor", blocking=False, seeThru=True)
        self.map = [[[] for x in range(self.mapWidth )] for y in range(self.mapHeight)]

        for (i, j) in itertools.product(range(self.mapHeight), range(self.mapWidth)):
            allTiles = levelArray[i][j]
            for tileChar in allTiles:
                tileTypeKey = decoder[tileChar]
                if tileTypeKey in TILES.keys():
                    tileDict = TILES[tileTypeKey]
                    self.map[i][j].append(Tile((j,i),**tileDict))
                    continue

                elif tileTypeKey == "player":
                    # don't use this.  always add player at portal.
                    continue

                elif tileTypeKey in ITEMS.keys():
                    self.addItem(j, i, tileTypeKey)
                    continue

                elif tileTypeKey in CHARACTERS.keys():
                    self.addCharacter(j, i, tileTypeKey)
                    continue

                elif tileTypeKey in PORTALS.keys():
                    self.addPortal(j, i, tileTypeKey) 
                    continue

                raise Exception(f"Failed at adding item during level parsing. {tileTypeKey}")

        self.initializeVisibilityMap()

    @property
    def tilesFlattened(self) -> List[Tile]:
        ''' Returns all of the 'background' tiles, in self.map, in a flattened
        list for drawing.'''
        bgTiles = []
        for row in self.map:
            for position in row:
                bgTiles.extend(position)
        return bgTiles

    def tileIsBlocking(self, x:int, y:int) -> bool:
        ''' Can we (not) walk through cell (x,y)?'''
        return any([tile.blocking for tile in self.map[y][x]])

    def initializeVisibilityMap(self) -> None:
        ''' The visibilityMap is a libtcod object for calculating the field of 
        view from any position.  This is a property of the Level.  computeFov() 
        uses this map to generate a Viewer-specific fov from its location.
        '''
        mapHeight = len(self.map)
        mapWidth = len(self.map[0])

        self.visibilityMap = libtcod.map.Map(width=mapWidth, height=mapHeight)
        for (y, x) in itertools.product(range(mapHeight), range(mapWidth)):
            seeThru = all([tile.seeThru for tile in self.map[y][x]])
            self.visibilityMap.transparent[y][x] = seeThru
        self.recalculateViewerFovs()

    def recalculateViewerFovs(self) -> None:
        for obj in self.objects:
            if isinstance(obj, Viewer):  
                obj.recalculateFov()
  
    def computeFov(self, x: int, y: int) -> np.ndarray:
        ''' Using the boolean visibility map of the level, return the boolean 
        field of view may from a specific (x,y) position. x,y specificed in 
        cells.  The returned array is of booleans.
        '''
        self.visibilityMap.compute_fov(x, y,
            radius = constants.FOV_RADIUS,
            light_walls = constants.FOV_LIGHT_WALLS,
            algorithm = constants.FOV_ALGO)
        return self.visibilityMap.fov
                
    def checkForCreature(self, x: int, y: int, excludeObject: Actor=None)->Actor:
        ''' Returns target creature instance if target location contains creature.
        x,y in cells.  excludeObject can be any type which is in level.objects.
        For the time being, that means Actors and (mostly) subclasses.
        The return type has the same constraints.
        '''
        for obj in self.objectsAtCoords(x, y):
            if (obj is not excludeObject) and isinstance(obj, Creature): #Combatant
                return obj
        return None

    def objectsAtCoords(self,x: int,y: int) -> List[Actor]:
        '''Returns all objects at cell (x,y)?'''
        return [obj for obj in self.objects if obj.x == x and obj.y == y]

    def addCharacter(self, coordX: int, coordY: int, 
                       name: str, uniqueName: str =None) -> None:
        ''' Place an enemy of type name (looked up in monsterLib) at coordinate
        cell (x,y).  Unique name is instance name of that particular monster.
        '''
        monsterDict = CHARACTERS[name]

        if uniqueName is None:
            uniqueName = random.choice(NAMES) + " the " + name
        inventory = Container(**monsterDict)
        aiInst = getattr(ai,monsterDict['aiName'])() 

        if monsterDict.get('combatant', True):
            newClass = Combatant
        elif monsterDict.get('conversationalist', False):
            newClass = Conversationalist
        else:
            newClass = Creature
        enemy = newClass((coordX, coordY), level=self, container=inventory, 
                         ai=aiInst, uniqueName=uniqueName,
                          **monsterDict)  
 
        self.objects.append(enemy)

    def addPlayer(self, x: int, y: int) -> None:
        ''' place player at (x,y).  This can mean creating a Player instance or
        moving the current one to the new location. 
        '''
        if GAME.player is None:
            playerInventory = Container()
            playerSpriteDict = SpriteDict('dawnlike/Characters/humanoid0.png',
                                           colIdx=0, rowIdx=3, numSprites=3)
            GAME.player = PlayerClass((x,y), name="hero", level=self,
                                      spriteDict=(playerSpriteDict,),
                                      container=playerInventory, 
                                      speed=0.12)
        else:
            GAME.player.x = x
            GAME.player.y = y
            GAME.player.level = self
            GAME.player.resyncGraphicPosition()
       
        if GAME.player not in self.objects:
            self.objects.append(GAME.player)

        GAME.player.initLevelExplorationHistory()
        self.recalculateViewerFovs()

    def addItem(self, coordX: int, coordY: int, name: str) -> None:
        ''' Place an item of type name (looked up in itemLib) at coordinate
        cell (x,y).  
        '''
        itemDict = ITEMS[name]
        isEquipment = itemDict.get('equipment', False)
        newClass = Equipment if isEquipment else Item
        item = newClass((coordX, coordY), level=self, **itemDict)
        self.objects.append(item)

    def addPortal(self, coordX: int, coordY: int, name: str) -> None:
        itemDict = PORTALS[name]
        item = Portal( (coordX, coordY), level=self, 
                        destinationPortal=None, **itemDict)
        self.objects.append(item)
        self.portals.append(item)

    def placePlayerAtPortal(self, portal: Portal) -> None:
        self.addPlayer(portal.x, portal.y)

    def takeCreatureTurns(self) -> None:
        for gameObj in self.objects:
            if isinstance(gameObj, Creature):
                gameObj.resolveQueueTick()


