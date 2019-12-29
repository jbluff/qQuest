import itertools
import math
import copy
import string
import os
import json

import pygame

from qQuest import constants, graphics
from qQuest.characters import Creature
from qQuest.graphics import Actor
from qQuest.items import Item
from qQuest.levels import Level, Tile, Portal
from qQuest.lib.characterLib import CHARACTERS
from qQuest.lib.itemLib import ITEMS
from qQuest.lib.portalLib import PORTALS
from qQuest.lib.tileLib import TILES
from qQuest.lib.visEffectsLib import EFFECTS


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
SIDEBAR_WIDTH = 15
TOTAL_WIDTH = MAP_WIDTH+SIDEBAR_WIDTH

pygame.init()
SURFACE_MAIN = pygame.display.set_mode((TOTAL_WIDTH*cw, MAP_HEIGHT*ch))

MOUSE_OVER_BUTTON = None
PALETTE_SELECTION = None

class Button(Actor):
    def __init__(self, *args, palette=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.palette = palette

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
        doBreak = handleInput(mapButtons)
            
        SURFACE_MAIN.fill(constants.COLOR_WHITE)
        drawAll(mapButtons)
        drawAll(paletteButtons)

        pygame.display.flip()
        constants.CLOCK.tick(30)

    exportLevel(mapButtons)
    exitEditor()

def exitEditor():
    pygame.quit()
    quit()

def handleInput(mapButtons):
    eventsList = pygame.event.get()

    for event in eventsList:
        if event.type == pygame.QUIT:
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f'x={MOUSE_OVER_BUTTON.x}, y={MOUSE_OVER_BUTTON.y}, name={MOUSE_OVER_BUTTON.name}') 
            if event.button == 1:
                handleLeftClick(mapButtons)
            if event.button == 3:
                handleRightClick(mapButtons)
    return False

def handleLeftClick(mapButtons):
    global PALETTE_SELECTION
    if MOUSE_OVER_BUTTON.palette:
        
        if not MOUSE_OVER_BUTTON == PALETTE_SELECTION:
            # Make a new palette selection
            PALETTE_SELECTION = MOUSE_OVER_BUTTON
        else:
            # unselect from pallete
            PALETTE_SELECTION = None
        return False
    
    else:
        if PALETTE_SELECTION is None:
            return False
        # place palette selection
        newButton = copy.deepcopy(PALETTE_SELECTION)
        newButton.x = MOUSE_OVER_BUTTON.x
        newButton.y = MOUSE_OVER_BUTTON.y
        newButton.palette = False
        mapButtons.append(newButton)
        return False

def handleRightClick(mapButtons):
    global MOUSE_OVER_BUTTON
    mapButtons.remove(MOUSE_OVER_BUTTON)

def addLibDict(libDict, offset):
    newButtons = []
    keys = libDict.keys()
    for key, (i, j) in zip(libDict, itertools.product(range(MAP_HEIGHT), 
                                                    range(SIDEBAR_WIDTH))):
        j += offset[0]
        i += offset[1]
        newTile = Button((j,i), name=key,  
                         spriteDict=libDict[key]['spriteDict'], palette=True)
        newButtons.append(newTile)  
    return newButtons

def drawAll(buttons):
    for button in buttons:
        button.draw(SURFACE_MAIN)
        
def exportLevel(mapButtons):
    allStrings = list(string.ascii_letters)

    array = [['' for x in range(MAP_WIDTH)] for x in range(MAP_HEIGHT)]
    backwardsDecoderRing = {}
    for button in mapButtons:
        name = button.name

        if name in backwardsDecoderRing:
            symbol = backwardsDecoderRing[name]

        else:
            symbol = allStrings.pop()
            backwardsDecoderRing[name] = symbol
        array[button.y][button.x] += symbol

    print(array)
    print(backwardsDecoderRing)   

    # cleanup()         

    decoderRing = {v:k for k,v in backwardsDecoderRing.items()}
    levelDict = {'level': array, 'decoderRing':decoderRing}

    saveMapFile(levelDict, 'test')
    pass

def saveMapFile(levelDict, fname):
    filePath = os.path.join(os.path.dirname(__file__),"levels",fname+".lvl")

    # filePath = os.path.join(os.path.dirname(__file__),"..","levels",fname+".lvl")
    print(filePath)
    with open(filePath, "w") as data_file:
        json.dump(levelDict, data_file)
    data_file.close()

if __name__ == '__main__':
    #newLevel = populateMapLevel()

    mapButtons = []
    for (i, j) in itertools.product(range(MAP_HEIGHT), range(MAP_WIDTH)):
        name = 'grass'
        newTile = Button((j,i), name=name, spriteDict=TILES[name]['spriteDict'])       
        mapButtons.append(newTile)  

    paletteButtons = []

    paletteButtons.extend(addLibDict(ITEMS, (MAP_WIDTH+1,0)))
    paletteButtons.extend(addLibDict(TILES, (MAP_WIDTH+1,3)))
    paletteButtons.extend(addLibDict(PORTALS, (MAP_WIDTH+1,5)))
    paletteButtons.extend(addLibDict(CHARACTERS, (MAP_WIDTH+1,7)))


    mainloop(mapButtons, paletteButtons)