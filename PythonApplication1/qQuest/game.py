'''
Covers the Game class, as well as the non-graphics global singletons.
'''

import pygame
import numpy as np

try:
    from qQuest import constants
except ImportError:
    import constants




class Game:
    ''' This class primarily only exists for saving and loading, which necessitates
    collections of multiple levels.  We also use it to keep track of portals for
    inter-level travel.  It did more, in the past.'''
    def __init__(self):
        self.messageHistory = []

        self.levels = []
        self.currentLevel = None

        self.player = None
        self.camera = None
        self.viewer = None

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color, constants.COLOR_BLACK))

    # @property
    # def currentLevel(self):
    #     return self._currentLevel

    # @currentLevel.setter
    # def currentLevel(self, value):
    #     self._currentLevel = value

        #self.mapHeight, self.mapWidth = np.array(self.currentLevel.map).shape
        # is this actually used anymore?

    def transitPortal(self, entryPortal):
        destinationPortal = entryPortal.destinationPortal
        newLevel = destinationPortal.level

        self.currentLevel = newLevel
        newLevel.placePlayerAtPortal(destinationPortal)
        
        self.viewer.recalculateFov()
        self.camera.updatePositionFromViewer()

GAME = Game()

