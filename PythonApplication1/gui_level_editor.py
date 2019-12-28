import itertools
import math
import copy

import pygame


from qQuest import constants, graphics
from qQuest.graphics import Actor
from qQuest.items import Item
from qQuest.levels import Level, Tile, Portal
from qQuest.characters import Creature
from qQuest.lib.visEffectsLib import EFFECTS
from qQuest.lib.tileLib import TILES
from qQuest.lib.characterLib import CHARACTERS
from qQuest.lib.itemLib import ITEMS
from qQuest.lib.portalLib import PORTALS


'''
trash all of this and draw everything on a true grid system.  kludging in mouse
support afterwards just isn't reasonable.  Either rewrite the main game to use
pygame Sprites or stop trying to use the main game tools to draw something that
uses the mouse.  
'''

cw = constants.CELL_WIDTH
ch = constants.CELL_HEIGHT

MAP_HEIGHT = 20
MAP_WIDTH = 19
SIDEBAR_WIDTH = 10
TOTAL_WIDTH = MAP_WIDTH+SIDEBAR_WIDTH

pygame.init()
SURFACE_MAIN = pygame.display.set_mode((TOTAL_WIDTH*cw, MAP_HEIGHT*ch))
#SURFACE_LEVEL = pygame.Surface((MAP_WIDTH*cw, MAP_HEIGHT*ch))
#SURFACE_SIDEBAR = pygame.Surface((SIDEBAR_WIDTH*cw, MAP_HEIGHT*ch))
MOUSE_OVER_BUTTON = None

class Button(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected = False
        
    def updatePosition(self):
        self.abs_pos = [self.x*cw, self.y*ch]

    def translate(self, dx, dy):
        self.abs_pos[0] += dx
        self.abs_pos[1] += dy

    def toggleSelect(self):
        self.selected += 1
        self.selected %= 2

    def isMouseOver(self):

        startX = self.x*cw
        stopX = (self.x + 1) * cw
        startY = self.y*ch
        stopY = (self.y + 1) * ch
        
        mX, mY = pygame.mouse.get_pos()
        inX = (mX < stopX) and (mX >= startX)
        inY = (mY < stopY) and (mY >= startY)
        return inX and inY

    def draw(self, surface, *args, **kwargs):
        pos = (self.x * cw, self.y * ch)
        sprite = self.getCurrentSprite().copy()

        if self.isMouseOver():
            coverSprite = pygame.Surface((cw, ch))
            coverSprite.fill(constants.COLOR_WHITE)
            coverSprite.set_alpha(200)
            sprite.blit(coverSprite, (0,0))
            global MOUSE_OVER_BUTTON
            MOUSE_OVER_BUTTON = self

        surface.blit(sprite, pos)

    def colorSelected(self):
        pass

    def colorMouseOver(self):
        pass


def mainloop(buttons):
    doBreak = False
    while not doBreak:
        
        doBreak = handleInput()

        drawAll(buttons)

        pygame.display.flip()


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

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f'x={MOUSE_OVER_BUTTON.x}, y={MOUSE_OVER_BUTTON.y}') 

    return False


def drawAll(buttons):
    SURFACE_MAIN.fill(constants.COLOR_WHITE)

    for button in buttons:
        button.draw(SURFACE_MAIN)
        

if __name__ == '__main__':
    #newLevel = populateMapLevel()

    buttons = []
    for (i, j) in itertools.product(range(MAP_HEIGHT), range(MAP_WIDTH)):
        name = 'fireSmall'
        newTile = Button((j,i), name=name,
                              spriteDict=EFFECTS[name]['spriteDict'], level='mapMain')       
        buttons.append(newTile)  

    # buttonsFlattened = []
    # [[buttonsFlattened.append(button) for button in row] for row in allTheThings]

    mainloop(buttons)