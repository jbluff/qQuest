import pygame
import numpy as np

from qQuest import constants, map_util

CLOCK = pygame.time.Clock()

SURFACE_MAIN = pygame.display.set_mode((100,100))


class Game:
    def __init__(self):
        
        #self.currentObjects = []
        self.messageHistory = []

        self.currentLevelIdx = None
        self.levels = []

        self.player = None

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color))

    def switchLevel(self):
        self.currentLevel = False
        raise NotImplementedError

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

        self.mapHeight, self.mapWidth = np.array(self.currentLevel.levelArray).shape
        updateSurfaceSize(self)

    def recalculateFov(self):
        map_util.mapCalculateFov(self.viewer)



GAME = Game()

def updateSurfaceSize(game):
    pygame.display.set_mode((game.mapWidth*constants.CELL_WIDTH,
                             game.mapHeight*constants.CELL_HEIGHT))