"""
Covers the Game class, as well as the global singletons GAME, CLOCK, and SURFACE_MAIN.
"""

import pygame
from pygame.locals import DOUBLEBUF
import numpy as np

from qQuest import constants
#from qQuest import map_util


#flags = FULLSCREEN | DOUBLEBUF

CLOCK = pygame.time.Clock()
cameraWidthInPix = constants.CAMERA_WIDTH*constants.CELL_WIDTH
cameraHeightInPix = constants.CAMERA_HEIGHT*constants.CELL_HEIGHT
SURFACE_MAIN = pygame.display.set_mode((cameraWidthInPix, cameraHeightInPix),
                                        pygame.FULLSCREEN)

class Game:
    def __init__(self):
        self.messageHistory = []
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
        self.viewer.recalculateFov()
GAME = Game()

