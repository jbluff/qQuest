import itertools

import pygame


from qQuest import constants
from qQuest.graphics import Actor
from qQuest.levels import Level, Tile
from qQuest.lib.visEffectsLib import EFFECTS


cw = constants.CELL_WIDTH
ch = constants.CELL_HEIGHT

MAP_HEIGHT = 20
MAP_WIDTH = 19
SIDEBAR_WIDTH = 10

pygame.init()
SURFACE_MAIN = pygame.display.set_mode(((MAP_WIDTH+SIDEBAR_WIDTH)*cw, MAP_HEIGHT*ch))
SURFACE_LEVEL = pygame.Surface((MAP_WIDTH*cw, MAP_HEIGHT*ch))
SURFACE_SIDEBAR = pygame.Surface((SIDEBAR_WIDTH*cw, MAP_HEIGHT*ch))


def mainloop():
    doBreak = False
    while not doBreak:
        
        doBreak = handleInput()
        drawEditor()
        constants.CLOCK.tick(30)
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
    
    drawLevel()
    drawSidebar()
    pygame.display.flip()

def drawLevel(level):
    SURFACE_MAIN.blit(SURFACE_LEVEL, (0*cw,0))
    level.drawAllTiles()

def drawSidebar():
    SURFACE_MAIN.blit(SURFACE_SIDEBAR, (MAP_WIDTH*cw,0))
    
    

if __name__ == '__main__':
    newLevel = Level('newLevel', loadFromFile=False)
    newLevel.mapHeight = MAP_HEIGHT
    newLevel.mapWidth = MAP_WIDTH

    newLevel.map = [["" for x in range(newLevel.mapWidth )] for y in range(newLevel.mapHeight)]

    for (i, j) in itertools.product(range(newLevel.mapHeight), range(newLevel.mapWidth)):
        name = 'fireSmall'
        newTile = Tile((j,i), blocking=False, seeThru=False, name=name,
                              spriteDict=EFFECTS[name]['spriteDict'])       
        newLevel.map[i][j] = newTile
    mainloop()