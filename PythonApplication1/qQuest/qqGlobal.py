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
        self.currentLevel = []
        self.currentObjects = []
        self.messageHistory = []

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color))

    # def checkForCreature(self, x, y, exclude_object = None):
    #     '''
    #     Returns target creature instance if target location contains creature
    #     '''
    #     target = None
    #     for object in self.currentObjects:
    #         if (object is not exclude_object and
    #             object.x == x and
    #             object.y == y and
    #             object.creature):
    #             return object
    #     return None

    # def objectsAtCoords(self,x,y):
    #     return [obj for obj in self.currentObjects if obj.x == x and obj.y == y]


    def updateSurfaceSize(self):
        pygame.display.set_mode((self.mapWidth*constants.CELL_WIDTH,
                                 self.mapHeight*constants.CELL_HEIGHT))

    def saveGame(self):
        raise NotImplementedError

    def switchLevel(self):
        self.currentLevel = False
        raise NotImplementedError




GAME = Game()