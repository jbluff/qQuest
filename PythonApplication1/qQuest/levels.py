import json, os
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
        #self.game = parentGame
        self.levelName = levelName

        self.loadLevelFile()
        self.parseLevelDict()
        #self.map = map_util.loadLevel(levelDict)

        self.fovMap = None
        #self.fovMap = []  ## TODO:  need to add ability to save FovMap when switching back to previous level

        self.objects = []

    def loadLevelFile(self):#,levelName):
        filePath = os.path.join(os.path.dirname(__file__),"..","levels",self.levelName+".lvl")
        with open(filePath, "r") as levelFile:
            self.levelDict = json.load(levelFile)
        levelFile.close()

    def parseLevelDict(self):
        levelArray = self.levelDict["level"]
        decoder = self.levelDict["decoderRing"]

        #clean this up
        mapHeight = len(levelArray)
        mapWidth = len(levelArray[0])
        GAME.mapHeight = len(levelArray)
        GAME.mapWidth = len(levelArray[0])

        self.map = [[structTile(False) for y in range(0, mapHeight)] for x in range(0, mapWidth )]

        for i in range(GAME.mapHeight):
            for j in range(GAME.mapWidth):
                tileType = decoder[levelArray[i][j]]
                if tileType == "wall":
                    self.map[j][i].blockPath = True

        GAME.updateSurfaceSize()


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
                        fovMap=map_util.createFovMap(self.map))    
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
       
        self.currentFovMap = playerFovMap
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

