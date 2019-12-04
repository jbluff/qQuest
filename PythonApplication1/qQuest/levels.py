import json
import os
import itertools
import random

import numpy as np
import tcod as libtcod


from qQuest import ai, constants

from qQuest.actors import Actor, Creature, Item, Container, Equipment, Portal, PlayerClass, Viewer
from qQuest.game import SURFACE_MAIN, CLOCK, GAME
from qQuest.graphics import ASSETS

from qQuest.lib.itemLib import ITEMS
from qQuest.lib.monsterLib import MONSTERS, NAMES
from qQuest.lib.tileLib import TILES

# the tile Sprites will change with level, eventually.
# like caves vs dungeon vs whatever
class Tile:
    def __init__(self, inFovSpriteName, outOfFovSpriteName, blocking=False, seeThru=True):
        self.inFovSpriteName = inFovSpriteName
        self.outOfFovSpriteName = outOfFovSpriteName
        self.blocking = blocking
        self.seeThru = seeThru

    def doDraw(self, viewer=None, camera=None):
        raise NotImplementedError

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
        

    def loadLevelFile(self):
        filePath = os.path.join(os.path.dirname(__file__),"..","levels",self.levelName+".lvl")
        with open(filePath, "r") as levelFile:
            self.levelDict = json.load(levelFile)
        levelFile.close()

    def parseLevelDict(self):
        self.levelArray = self.levelDict["level"]
        decoder = self.levelDict["decoderRing"]

        self.mapHeight, self.mapWidth = np.array(self.levelArray).shape

        floorTile = Tile("s_floor", "s_floor_dark", blocking=False, seeThru=True)
        self.map = [[floorTile for x in range(self.mapWidth )] for y in range(self.mapHeight)]

        for (i, j) in itertools.product(range(self.mapHeight), range(self.mapWidth)):
            tileType = decoder[self.levelArray[i][j]]
            if tileType == "floor":
                continue

            if tileType == "wall":
                self.map[i][j] = Tile("s_wall", "s_wall_dark", blocking=True, seeThru=False)
                continue
            
            if tileType == "player":
                # don't use this.  always add player at portal.
                continue

            if tileType in ITEMS.keys():
                self.addItem(j, i, tileType)
                continue

            if tileType in MONSTERS.keys():
                self.addEnemy(j, i, tileType)
                continue

            if tileType in TILES.keys():
                self.addPortal(j, i, tileType) #this construction is erroneous.
                continue

            raise Exception("Failed at adding item during level parsing.")

        self.initializeVisibilityMap()

    '''
    the visibilityMap is a libtcod object for calculating the field of view from any position.
    '''
    def initializeVisibilityMap(self):
        mapHeight, mapWidth = np.array(self.map).shape

        self.visibilityMap = libtcod.map.Map(width=mapWidth, height=mapHeight)
        for (y, x) in itertools.product(range(mapHeight), range(mapWidth)):
            self.visibilityMap.transparent[y][x] = self.map[y][x].seeThru
        self.recalculateViewerFovs()

    def recalculateViewerFovs(self):
        for obj in self.objects:
            if isinstance(obj, (Viewer, PlayerClass)):
                obj.recalculateFov(force=True)

    def computeFov(self, x, y):
        self.visibilityMap.compute_fov(x, y,
            radius = constants.FOV_RADIUS,
            light_walls = constants.FOV_LIGHT_WALLS,
            algorithm = constants.FOV_ALGO)
        return self.visibilityMap.fov
                
    def checkForCreature(self, x, y, exclude_object = None):
        '''
        Returns target creature instance if target location contains creature
        '''
        target = None
        for obj in self.objects:
            if (obj is not exclude_object and
                    obj.x == x and #sub objectAtCoords into here
                    obj.y == y and
                    isinstance(obj, (Creature, PlayerClass))):
                return obj
        return None

    def objectsAtCoords(self,x,y):
        return [obj for obj in self.objects if obj.x == x and obj.y == y]

    '''
        Creates NPC characters by type, looking qp info in a library file.
    '''
    def addEnemy(self, coordX, coordY, name, uniqueName=None):
        monsterDict = MONSTERS[name]
        name = monsterDict['name']
        if uniqueName is None:
            uniqueName = random.choice(NAMES)
        name = uniqueName + " the " + name

        inventory = Container(**monsterDict['kwargs'])
        enemy = Creature( (coordX, coordY), name, monsterDict['animation'],
                        ai=getattr(ai,monsterDict['ai'])(), 
                        container=inventory, deathFunction=monsterDict['deathFunction'],
                        level=self)    
        self.objects.append(enemy)

    def addPlayer(self, x,y):

        if GAME.player is None:
            playerInventory = Container()
            GAME.player = PlayerClass((x,y), "hero", "a_player",
                                      container=playerInventory, level=self)
        else:
            GAME.player.x = x
            GAME.player.y = y
            GAME.player.level = self
       
        if GAME.player not in self.objects:
            self.objects.append(GAME.player)

        GAME.player.initLevelExplorationHistory()
        self.recalculateViewerFovs()
        #self.reinitializeVisibilityMaps() #needs to be done after all walls AND PLAYER placed.

    '''
        Creates Items by type, looking up info in a library file.
    '''
    def addItem(self, coordX, coordY, name):
        itemDict = ITEMS[name]
        if 'equipment' in itemDict.keys():
            item = Equipment( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
                        **itemDict['kwargs'], level=self)
        else:
            item = Item( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
                        useFunction=itemDict['useFunction'], **itemDict['kwargs'], level=self)
        self.objects.append(item)

    def addPortal(self, coordX, coordY, name):
        itemDict = TILES[name]
        item = Portal( (coordX, coordY), name, itemDict['animation'], level=self, destinationPortal=None)
        self.objects.append(item)
        self.portals.append(item)

    def placePlayerAtPortal(self, portal):
        self.addPlayer(portal.x, portal.y)

    def takeNPCturns(self):
        for gameObj in self.objects:
            #if gameObj.ai:
            #if isinstance(gameObj, Creature): #this isn't perfect.
            if getattr(gameObj, "ai", None):
                gameObj.ai.takeTurn()
