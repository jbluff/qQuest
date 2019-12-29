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

    def transitPortal(self, entryPortal: 'level.Portal') -> None:
        destinationPortal = entryPortal.destinationPortal
        newLevel = destinationPortal.level

        self.currentLevel = newLevel
        newLevel.placePlayerAtPortal(destinationPortal)
        
        self.viewer.recalculateFov()
        self.camera.updatePositionFromViewer()

    @staticmethod
    def couplePortals(portal0: 'level.Portal', portal1: 'level.Portal')->None:
        ''' Symmetrically configure two portals. '''
        assert portal0.destinationPortal is None
        assert portal1.destinationPortal is None
        
        portal0.destinationPortal = portal1
        portal1.destinationPortal = portal0    

GAME = Game()

