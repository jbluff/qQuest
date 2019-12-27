import itertools

import pygame

from graphics import Actor
import constants
from lib.visEffectsLib import EFFECTS


cw = constants.CELL_WIDTH
ch = constants.CELL_HEIGHT


CLOCK = pygame.time.Clock()
LEVEL = MapEditLevel()

mapSize = (19, 20)
LEVEL.tiles = initMap(mapSize)


SURFACE_MAIN = pygame.Surface((30*cw, 20*ch))
SURFACE_LEVEL = pygame.Surface((20*cw, 20*ch))
SURFACE_SIDEBAR = pygame.Surface((10*cw, 20*ch))

class MapEditLevel():
    def __init__(self):
        self.tiles = []

    def drawAllTiles(self):
        for tile in self.tiles:
            for actor in tile:# tile is Actor
                tile.draw(doGameChecks=False)


def mainloop():
    doBreak = False
    while not doBreak:
        
        doBreak = handleInput()
        drawEditor()
        CLOCK.tick(30)
    exitEditor()

def exitEditor():
    pygame.quit()
    quit()

def handleInput():
    eventsList = pygame.event.get()

    for event in eventsList:
        if event.type == pygame.QUIT:
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                return True

    return False

def drawEditor():
    SURFACE_MAIN.fill(constants.COLOR_GREY)
    LEVEL.drawAllTiles()
    drawLevel()
    drawSidebar()
    pygame.display.flip()

def drawLevel():
    SURFACE_LEVEL.blit(SURFACE_SIDEBAR, (0*cw,0))

def drawSidebar():
    SURFACE_MAIN.blit(SURFACE_SIDEBAR, (20*cw,0))
    

def initMap(mapSize):

    levelMap = []
    for (x, y) in itertools.product(range(mapSize[0]), range(mapSize[1])):

        newTile = Actor((x,y), name='foo', 
                               spriteDict=EFFECTS['fireSmall']['spriteDict'], 
                               surface=SURFACE_LEVEL)
        levelMap.append([newTile,])
    return levelMap

    
if __name__ == '__main__':


    mainloop()