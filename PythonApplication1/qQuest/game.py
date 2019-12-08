"""
Covers the Game class, as well as the global singletons GAME, CLOCK, and SURFACE_MAIN.
"""

import pygame
from pygame.locals import DOUBLEBUF
import numpy as np

from qQuest import constants
#from qQuest import map_util


#flags = FULLSCREEN | DOUBLEBUF
#screen = pygame.display.set_mode(resolution, flags, bpp)

CLOCK = pygame.time.Clock()
SURFACE_MAIN = pygame.display.set_mode((constants.CAMERA_WIDTH*constants.CELL_WIDTH,
                                        constants.CAMERA_HEIGHT*constants.CELL_HEIGHT),
                                        DOUBLEBUF)

class Game:
    def __init__(self):
        self.messageHistory = []

        # self.currentLevelIdx = None
        self.levels = []
        self.player = None

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color, constants.COLOR_BLACK))

    @property
    def currentLevel(self):
        return self._currentLevel

    @currentLevel.setter
    def currentLevel(self, value):
        self._currentLevel = value

        self.mapHeight, self.mapWidth = np.array(self.currentLevel.levelArray).shape
        # updateSurfaceSize(self) # I think is no longer needed after the camera addition?

    '''
    Look at the entry portal, 
    see what level it points to, 
    switch the current level to that level, 
        - this triggers resizing the main surface
    place the player in the new level at the new portal. 
        - this also triggers recalculating the fovMap 
    '''
    def transitPortal(self, entryPortal):
        destinationPortal = entryPortal.destinationPortal
        newLevel = destinationPortal.level

        self.currentLevel = newLevel
        newLevel.placePlayerAtPortal(destinationPortal)

GAME = Game()

def updateSurfaceSize(game):
    return None
    # pygame.display.set_mode((game.mapWidth*constants.CELL_WIDTH,
    #                          game.mapHeight*constants.CELL_HEIGHT))
    #pygame.display.set_mode((constants.CAMERA_WIDTH*constants.CELL_WIDTH,
    #                         constants.CAMERA_HEIGHT*constants.CELL_HEIGHT))