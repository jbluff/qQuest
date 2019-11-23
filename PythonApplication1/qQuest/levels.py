from qQuest import map_util
from qQuest import ai
#from qQuest import actors, magic
from qQuest.actors import Actor, Creature, Item, Container, Equipment

from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME
from qQuest.graphics import ASSETS

from qQuest.lib.itemLib import ITEMS
from qQuest.lib.monsterLib import MONSTERS

class Level:
    def __init__(self, parentGame, levelDict): #, fovMap):
        self.game = parentGame
        self.levelDict = levelDict
        self.map = map_util.loadLevel(levelDict)

        self.fovMap = None
        #self.fovMap = []  ## TODO:  need to add ability to save FovMap when switching back to previous level

        self.objects = []

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

    '''
    Only call this once!  Creates a global/singleton.
    '''
    def addPlayer(self, x,y):
        #global PLAYER
        #GAME.player

        playerInventory = Container()
        playerFovMap = map_util.createFovMap(self.map)
        #PLAYER = Creature( (x,y), "hero", ASSETS.a_player, 
        GAME.player = Creature( (x,y), "hero", ASSETS.a_player, 
                    fovMap=playerFovMap,
                    container=playerInventory)
        self.currentFovMap = playerFovMap
        map_util.mapCalculateFov(GAME.player)
        #map_util.mapCalculateFov(PLAYER)

        #self.objects.append(PLAYER)
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

