import json
import os
import itertools
import random
from typing import List

import numpy as np
import tcod as libtcod

from qQuest import ai, constants

from qQuest.constants import SpriteDict 
from qQuest.actors import Creature, Portal, PlayerClass, Viewer
from qQuest.items import Item, Equipment, Container
from qQuest.game import GAME
from qQuest.graphics import ASSETS, Actor, compileBackgroundTiles

from qQuest.lib.itemLib import ITEMS
from qQuest.lib.monsterLib import MONSTERS, NAMES
from qQuest.lib.portalLib import PORTALS 
from qQuest.lib.tileLib import TILES 


class Tile:
    def __init__(self, blocking=False, seeThru=True, spriteDict={}, **kwargs):
        self.blocking = blocking
        self.seeThru = seeThru
        self.spriteDict = spriteDict

class Level:
    numLevels = 0

    def __init__(self, levelName):
        self.levelName = levelName

        self.objects = [] #should this be a set?   would it simplify deletion?
        self.portals = []

        self.loadLevelFile()
        self.parseLevelDict()

        self.uniqueID = f'level{Level.numLevels}'
        Level.numLevels += 1

        self.compileMapGraphic()

    def compileMapGraphic(self, force=False) -> None:
        if (self.uniqueID not in ASSETS.compiledLevelMaps) and (not force):
            levelSurface = compileBackgroundTiles(level=self)
            ASSETS.compiledLevelMaps[self.uniqueID] = levelSurface

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

        '''
        Refactor & entensions plan:
        x 1)  entries in the levelArray should allow more than one type per entry
            - that allows, for instance, multiple objects at the same place.
            - looking ahead, that means we can specify both the floor tile and
                the object on top of it.

        x 2) tileLib gets renamed portalLib

        x 3) we create floorLib, which points at various different types of 
            floor tile sprites, so we can mix that up.

        x 4) similarly we create wallLib.
            - note that this DOESN'T allow for dynamic, neighbor-aware sprite
                selection.  We'll have to work that out later.  Maybe handle in
                generation?

        5) I'd also like to make some decoratives that get rendered on top of 
            the floors and walls, but don't actually create any sort of blocking
            or opaque tile entry.  
        '''

        self.levelArray = self.levelDict["level"]
        decoder = self.levelDict["decoderRing"]

        self.mapHeight, self.mapWidth = np.array(self.levelArray).shape

        floorTile = ""#Tile("s_floor", blocking=False, seeThru=True)
        self.map = [[floorTile for x in range(self.mapWidth )] for y in range(self.mapHeight)]

        for (i, j) in itertools.product(range(self.mapHeight), range(self.mapWidth)):
            allTiles = self.levelArray[i][j]
            for tileChar in allTiles:
                tileTypeKey = decoder[tileChar]
                if tileTypeKey in TILES.keys():
                    tileDict = TILES[tileTypeKey]
                    self.map[i][j] = Tile(**tileDict)
                    continue

                elif tileTypeKey == "player":
                    # don't use this.  always add player at portal.
                    continue

                elif tileTypeKey in ITEMS.keys():
                    self.addItem(j, i, tileTypeKey)
                    continue

                elif tileTypeKey in MONSTERS.keys():
                    self.addEnemy(j, i, tileTypeKey)
                    continue

                elif tileTypeKey in PORTALS.keys():
                    self.addPortal(j, i, tileTypeKey) 
                    continue

                raise Exception(f"Failed at adding item during level parsing. {tileTypeKey}")

        self.initializeVisibilityMap()

    def initializeVisibilityMap(self) -> None:
        ''' The visibilityMap is a libtcod object for calculating the field of 
        view from any position.  This is a property of the Level.  computeFov() 
        uses this map to generate a Viewer-specific fov from its location.
        '''
        mapHeight, mapWidth = np.array(self.map).shape

        self.visibilityMap = libtcod.map.Map(width=mapWidth, height=mapHeight)
        for (y, x) in itertools.product(range(mapHeight), range(mapWidth)):
            self.visibilityMap.transparent[y][x] = self.map[y][x].seeThru
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
        target = None
        for obj in self.objects:
            if (obj is not excludeObject and
                    obj.x == x and #sub objectAtCoords into here
                    obj.y == y and
                    isinstance(obj, Creature)): #playerclsdd
                return obj
        return None

    def objectsAtCoords(self,x: int,y: int) -> List[Actor]:
        '''Returns all objects at cell (x,y)?'''
        return [obj for obj in self.objects if obj.x == x and obj.y == y]

    def addEnemy(self, coordX: int, coordY: int, 
                       name: str, uniqueName: str =None) -> None:
        ''' Place an enemy of type name (looked up in monsterLib) at coordinate
        cell (x,y).  Unique name is instance name of that particular monster.
        '''
        monsterDict = MONSTERS[name]

        if uniqueName is None:
            uniqueName = random.choice(NAMES) + " the " + name
        inventory = Container(**monsterDict)
        aiInst = getattr(ai,monsterDict['aiName'])() 

        enemy = Creature((coordX, coordY), level=self, container=inventory, 
                         ai=aiInst, uniqueName=uniqueName, **monsterDict)  
 
        self.objects.append(enemy)

    def addPlayer(self, x: int, y: int) -> None:
        ''' place player at (x,y).  This can mean creating a Player instance or
        moving the current one to the new location. 
        '''
        if GAME.player is None:
            playerInventory = Container()
            # playerSpriteDict = SpriteDict('dawnlike/Characters/humanoid0.png',
            playerSpriteDict = SpriteDict('dawnlike/Commissions/Engineer.png',

                                           colIdx=0, rowIdx=0, numSprites=4)
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

        if 'equipment' in itemDict:
            item = Equipment( (coordX, coordY), level=self, **itemDict)
        else:
            item = Item( (coordX, coordY), level=self, **itemDict)
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
