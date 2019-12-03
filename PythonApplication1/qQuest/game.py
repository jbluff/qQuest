"""
Covers the Game class, as well as the global singletons GAME, CLOCK, and SURFACE_MAIN.
"""

import pygame
import numpy as np

from qQuest import constants
#from qQuest import map_util

CLOCK = pygame.time.Clock()
SURFACE_MAIN = pygame.display.set_mode((100,100))

class Game:
    def __init__(self):
        self.messageHistory = []

        # self.currentLevelIdx = None
        self.levels = []
        self.player = None

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color))

    def switchLevel(self):
        self.currentLevel = False
        raise NotImplementedError

    @property
    def currentLevel(self):
        return self._currentLevel

    @currentLevel.setter
    def currentLevel(self, value):
        self._currentLevel = value

        self.mapHeight, self.mapWidth = np.array(self.currentLevel.levelArray).shape
        updateSurfaceSize(self)

    '''
    Look at the entry portal, 
    see what level it points to, 
    switch the current level to that level, 
        - this triggers resizing the main surface
    place the player in the new level at the new portal. 
        - this also triggers recalculating the fovMap 
    '''
    def transitPortal(self, entryPortal):
        print(f'yer goin thru a portal, Harry!')

        destinationPortal = entryPortal.destinationPortal
        newLevel = destinationPortal.level

        self.currentLevel = newLevel
        newLevel.placePlayerAtPortal(destinationPortal)

GAME = Game()

def updateSurfaceSize(game):
    pygame.display.set_mode((game.mapWidth*constants.CELL_WIDTH,
                             game.mapHeight*constants.CELL_HEIGHT))