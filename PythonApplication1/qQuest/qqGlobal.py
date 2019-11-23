import pygame
from qQuest import constants
#from qQuest.map_util import structTile

CLOCK = pygame.time.Clock()

SURFACE_MAIN = pygame.display.set_mode((100,100))
# SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH*constants.CELL_WIDTH,
#                                         constants.MAP_HEIGHT*constants.CELL_HEIGHT))

#class EmptyClass(object):
#    pass

#ASSETS = EmptyClass()  #TODO:  Figure out how to init ASSETS here

#TODO:  move this into its own file.
class Game:
    def __init__(self):
        self.currentObjects = []
        self.messageHistory = []

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color))

    def checkForCreature(self, x, y, exclude_object = None):
        '''
        Returns target creature instance if target location contains creature
        '''
        target = None
        for object in self.currentObjects:
            if (object is not exclude_object and
                object.x == x and
                object.y == y and
                object.creature):
                return object
        return None

    def objectsAtCoords(self,x,y):
        return [obj for obj in self.currentObjects if obj.x == x and obj.y == y]


    def updateSurfaceSize(self):
        pygame.display.set_mode((self.mapWidth*constants.CELL_WIDTH,
                                 self.mapHeight*constants.CELL_HEIGHT))

    # def loadLevel(self, levelDict):
    #     levelArray = levelDict["level"]
    #     decoder = levelDict["decoderRing"]

    #     mapHeight = len(levelArray)
    #     mapWidth = len(levelArray[0])
    #     self.mapHeight = len(levelArray)
    #     self.mapWidth = len(levelArray[0])

    #     print(mapHeight)
    #     print(mapWidth)
    #     newMap = [[structTile(False) for y in range(0, mapHeight)] for x in range(0, mapWidth )]

    #     for i in range(self.mapHeight):
    #         for j in range(self.mapWidth):
    #             tileType = decoder[levelArray[i][j]]
    #             if tileType == "wall":
    #                 newMap[j][i].blockPath = True

    #     GAME.updateSurfaceSize()

    #     self.currentMap = newMap



GAME = Game()