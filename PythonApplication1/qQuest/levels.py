import json, os, itertools
import numpy as np

from qQuest import map_util
from qQuest import ai
#from qQuest import actors, magic
from qQuest.actors import Actor, Creature, Item, Container, Equipment

from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME
from qQuest.graphics import ASSETS

from qQuest.lib.itemLib import ITEMS
from qQuest.lib.monsterLib import MONSTERS

class structTile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False

class Level:
    def __init__(self, levelName):
        self.levelName = levelName

        self.fovMap = None
        self.objects = []

        self.loadLevelFile()
        self.parseLevelDict()

    def loadLevelFile(self):#,levelName):
        filePath = os.path.join(os.path.dirname(__file__),"..","levels",self.levelName+".lvl")
        with open(filePath, "r") as levelFile:
            self.levelDict = json.load(levelFile)
        levelFile.close()

    def parseLevelDict(self):
        self.levelArray = self.levelDict["level"]
        decoder = self.levelDict["decoderRing"]

        self.mapHeight, self.mapWidth = np.array(self.levelArray).shape
        self.map = [[structTile(False) for x in range(0, self.mapWidth )] for y in range(0, self.mapHeight)]

        #itertools
        #for i in range(self.mapHeight):
        #for j in range(self.mapWidth):
        for (i, j) in itertools.product(range(self.mapHeight), range(self.mapWidth)):
            tileType = decoder[self.levelArray[i][j]]
            if tileType == "floor":
                continue

            if tileType == "wall":
                self.map[i][j].blockPath = True
                continue
            
            if tileType == "player":
                self.addPlayer(j, i)
                continue

            if tileType in ITEMS.keys():
                self.addItem(j, i, tileType)
                continue

            raise Exception("Failed at adding item during level parsing.")

        self.updateFovMaps() #needs to be done after all walls placed.

    def updateFovMaps(self):
        for obj in self.objects:
            if obj.fovMap:
                obj.fovMap = map_util.createFovMap(self.map)
                obj.fovCalculate = True
                
    def checkForCreature(self, x, y, exclude_object = None):
        '''
        Returns target creature instance if target location contains creature
        '''
        target = None
        for obj in self.objects:
            if (obj is not exclude_object and
                obj.x == x and #sub objectAtCoords into here
                obj.y == y and
                obj.creature):
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
        if uniqueName:
            name = uniqueName + " the " + name

        inventory = Container(**monsterDict['kwargs'])
        enemy = Creature( (coordX, coordY), name, monsterDict['animation'],
                        ai=getattr(ai,monsterDict['ai'])(), 
                        container=inventory, deathFunction=monsterDict['deathFunction'],
                        fovMap=None)#map_util.createFovMap(self.map))    
        self.objects.append(enemy)


    def addPlayer(self, x,y):
        playerFovMap = map_util.createFovMap(self.map) 
        if GAME.player is None:
            playerInventory = Container()
            GAME.player = Creature( (x,y), "hero", ASSETS.a_player, 
                    fovMap=playerFovMap,
                    container=playerInventory)
        else:
            GAME.player.x = x
            GAME.player.y = y
       
        self.fovMap = playerFovMap
        map_util.mapCalculateFov(GAME.player)
        self.objects.append(GAME.player)

    '''
        Creates Items by type, looking up info in a library file.
    '''
    def addItem(self, coordX, coordY, name):
        itemDict = ITEMS[name]
        if 'equipment' in itemDict.keys():
            item = Equipment( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
                        **itemDict['kwargs'])
        else:
            item = Item( (coordX, coordY), itemDict['name'], itemDict['animation'] ,
                        useFunction=itemDict['useFunction'], **itemDict['kwargs'])

        self.objects.append(item)

