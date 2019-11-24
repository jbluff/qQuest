import pygame
import numpy as np

from qQuest import constants

CLOCK = pygame.time.Clock()

SURFACE_MAIN = pygame.display.set_mode((100,100))

class Game:
    def __init__(self):
        
        self.currentObjects = []
        self.messageHistory = []

        self.currentLevelIdx = None
        self.levels = []

        self.player = None

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color))

    def updateSurfaceSize(self):
        pygame.display.set_mode((self.mapWidth*constants.CELL_WIDTH,
                                 self.mapHeight*constants.CELL_HEIGHT))

    def saveGame(self):
        raise NotImplementedError

    def switchLevel(self):
        self.currentLevel = False
        raise NotImplementedError

    # is the property() construction necessary?  no. 
    @property
    def currentLevel(self):
        return self.levels[self.currentLevelIdx]

    @currentLevel.setter
    def currentLevel(self, value):
        if type(value) == int:
            self.currentLevelIdx = value
        else:
            for idx, level in enumerate(self.levels):
                if level == value:
                    self.currentLevelIdx = idx
                    break

GAME = Game()