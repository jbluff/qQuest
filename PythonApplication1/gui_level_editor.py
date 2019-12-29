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
PALETTE_SELECTION = None

class Button(Actor):
    def __init__(self, *args, palette=False, **kwargs):
        super().__init__(*args, **kwargs)
        # self.selected = False
        self.palette = palette
        
    def updatePosition(self):
        self.abs_pos = [self.x*cw, self.y*ch]

    def translate(self, dx, dy):
        self.abs_pos[0] += dx
        self.abs_pos[1] += dy

    # def toggleSelect(self):
    #     self.selected += 1
    #     self.selected %= 2

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

        if self == PALETTE_SELECTION:
            coverSprite = pygame.Surface((cw, ch))
            coverSprite.fill(constants.COLOR_RED)
            coverSprite.set_alpha(200)
            sprite.blit(coverSprite, (0,0))            

        surface.blit(sprite, pos)

    def colorSelected(self):
        pass

    def colorMouseOver(self):
        pass


def mainloop(mapButtons, paletteButtons):
    doBreak = False
    while not doBreak:
        
        doBreak, newButton = handleInput(mapButtons)
        if newButton is not None:
            mapButtons.append(newButton)
            
        SURFACE_MAIN.fill(constants.COLOR_WHITE)
        drawAll(mapButtons)
        drawAll(paletteButtons)

        pygame.display.flip()


        constants.CLOCK.tick(30)
    exitEditor()

def exitEditor():
    pygame.quit()
    quit()

def handleInput(mapButtons):
    global PALETTE_SELECTION
    eventsList = pygame.event.get()

    for event in eventsList:
        if event.type == pygame.QUIT:
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f'x={MOUSE_OVER_BUTTON.x}, y={MOUSE_OVER_BUTTON.y}, name={MOUSE_OVER_BUTTON.name}') 
            if MOUSE_OVER_BUTTON.palette :
                if not MOUSE_OVER_BUTTON == PALETTE_SELECTION:
                    PALETTE_SELECTION = MOUSE_OVER_BUTTON
                else:
                    PALETTE_SELECTION = None
                continue
            
            else:
                if PALETTE_SELECTION is None:
                    continue
                newButton = copy.deepcopy(PALETTE_SELECTION)
                newButton.x = MOUSE_OVER_BUTTON.x
                newButton.y = MOUSE_OVER_BUTTON.y
                return False, newButton

    return False, None


def drawAll(buttons):
    for button in buttons:
        button.draw(SURFACE_MAIN)
        

if __name__ == '__main__':
    #newLevel = populateMapLevel()

    mapButtons = []
    for (i, j) in itertools.product(range(MAP_HEIGHT), range(MAP_WIDTH)):
        name = 'fireSmall'
        newTile = Button((j,i), name=name,
                              spriteDict=EFFECTS[name]['spriteDict'], level='mapMain')       
        mapButtons.append(newTile)  

    paletteButtons = []

    keys = ITEMS.keys()
    for key, (i, j) in zip(ITEMS, itertools.product(range(MAP_HEIGHT), range(SIDEBAR_WIDTH))):
        j += MAP_WIDTH+1

        newTile = Button((j,i), name=key,
                              spriteDict=ITEMS[key]['spriteDict'], level='mapMain', palette=True)       
        paletteButtons.append(newTile)  

    mainloop(mapButtons, paletteButtons)