import itertools

import pygame
import numpy as np

from qQuest import constants
from qQuest.game import SURFACE_MAIN, CLOCK, GAME

class Camera:
    def __init__(self, viewer=None):
        self.viewer = viewer
        self.updatePositionFromViewer()

    
    def updatePositionFromViewer(self):
        if self.viewer is not None:
            self.x = self.viewer.x
            self.y = self.viewer.y

    def canSee(self, x, y):
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT

        isVisisble = (x < self.x+w/2) and (x > self.x-w/2) and (y < self.y+h/2) and (y > self.y-h/2)

        #if self.viewer is not None:

        return isVisisble

    '''Converts a game map position to a draw position, both still in units of cells'''
    def drawPosition(self, x, y):
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT

        #dx = constants.CELL_WIDTH
        #dy = constants.CELL_HEIGHT

        return (x - self.x + w/2 - 0.5, y - self.y + h/2 - 0.5)
        

class objSpriteSheet:
    ''' loads a sprite sheet, allows pulling out animations '''
    def __init__(self, fileName, imageUnitX=constants.CELL_WIDTH, imageUnitY=constants.CELL_HEIGHT):
        ''' 
        imageUnitX/Y define the atomic size of an image on the sprite sheet, in pixels.
            images from the sprite sheet can be selected to take up e.g. several atomic units.
            images can also be scaled from their sprite sheet sizes
        
        '''
        self.spriteSheet = pygame.image.load(fileName).convert()
        self.imageUnitX = imageUnitX
        self.imageUnitY = imageUnitY
        
    def getAnimation(self, colIdx=0, rowIdx=0, numSprites=1, spanX=1, spanY=1, scale=None):
        ''' 
        spanX and spanY define size of image on the spriteSheet, in units of imageUnitX/Y
        
        scale is a tuple of scale factors, applied later
        '''
        startX, startY = colIdx * self.imageUnitX, rowIdx * self.imageUnitY
        width, height = spanX * self.imageUnitX, spanY * self.imageUnitY

        imageList = []
        for idx in range(numSprites):
            
            image = pygame.Surface([width, height]).convert()
            image.blit(self.spriteSheet, (0,0), (startX+idx*width, startY, width, height))
            image.set_colorkey(constants.COLOR_BLACK)

            if scale:
                newWidth = self.imageUnitX*spanX*scale[0]
                newHeight = self.imageUnitY*spanY*scale[1]
                image = pygame.transform.scale(image, (newWidth, newHeight))
            imageList.append(image)
        return imageList
 

'''Actors are all drawn things which are not floor ties.  May reflect player, NPCs, items'''
class Actor():
    def __init__(self, pos, name, animationName, level=None, **kwargs):

        self.x, self.y = pos
        self.name = name
        self.animationName = animationName
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg

        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.level = level

    @property
    def animation(self):
        return getattr(ASSETS,self.animationName)

    def draw(self):
        #isInViewerFov = GAME.viewer.fov[self.y][self.x]
        isInViewerFov = GAME.viewer.getTileIsVisible(self.x, self.y)
        if not isInViewerFov:
            return 

        if not GAME.camera.canSee(self.x, self.y):
            return

        if len(self.animation) == 1:
            currentSprite = self.animation[0]
 
        else:
            if CLOCK.get_fps() > 0.0:
                '''update the animation's timer.  Note draw() is called once per frame.'''
                self.flickerTimer += 1/CLOCK.get_fps() 

            if self.flickerTimer > self.flickerSpeed:
                self.flickerTimer = 0
                self.spriteImageNum += 1
                    
                #TODO, use remainder division
                if self.spriteImageNum >= len(self.animation):
                    self.spriteImageNum = 0
            currentSprite = self.animation[self.spriteImageNum]

        drawX, drawY = GAME.camera.drawPosition(self.x, self.y)
        shapeTuple = (drawX * constants.CELL_WIDTH, drawY * constants.CELL_HEIGHT) #really position, not shape

        # shapeTuple = (self.x * constants.CELL_WIDTH, self.y * constants.CELL_HEIGHT) #really position, not shape
        SURFACE_MAIN.blit(currentSprite, shapeTuple)


'''We'd like to the viewing history to be more than "explored" or "not explored".
    - if the map changes out-of-sight, the fog of war needs to reflect the tiles before they changes.
    - that's a change for down the road, but decoupling to a viewer's personal history will help
'''
def drawLevelTiles(viewer=None):
    if viewer is None:
        viewer = GAME.viewer
    level = GAME.currentLevel
    surface = SURFACE_MAIN

    mapHeight, mapWidth = np.array(level.map).shape
    for (x, y) in itertools.product(range(mapWidth), range(mapHeight)):
        tile = level.map[y][x]
        tileSprite = None
        fogRect = None

        tileIsVisibleToViewer = viewer.getTileIsVisible(x, y)
        tileIsExplored = viewer.getTileIsExplored(x, y)

        if not GAME.camera.canSee(x, y):
            continue
        
        if tileIsVisibleToViewer:
            viewer.setTileIsExplored(x, y)
            tileSprite = getattr(ASSETS, tile.inFovSpriteName) #bad bad bad

        elif tileIsExplored:

            #tileSprite = getattr(ASSETS, tile.outOfFovSpriteName)
            tileSprite = getattr(ASSETS, tile.inFovSpriteName) #bad bad bad
            # drawX, drawY = GAME.camera.drawPosition(x, y)
            # tilePosition = (drawX*constants.CELL_WIDTH, drawY*constants.CELL_HEIGHT)

            # fogRect = pygame.Rect(0,#drawX*constants.CELL_WIDTH,
            #                       0,#drawY*constants.CELL_HEIGHT,
            #                       constants.CELL_WIDTH,
            #                       constants.CELL_HEIGHT)
            # SURFACE_FOG.blit
            pass

        if tileSprite is not None:
            drawX, drawY = GAME.camera.drawPosition(x, y)

            #tilePosition = (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT)
            tilePosition = (drawX*constants.CELL_WIDTH, drawY*constants.CELL_HEIGHT)
            surface.blit(tileSprite, tilePosition)

            if tileIsExplored and not tileIsVisibleToViewer:

                #tileSprite = getattr(ASSETS, tile.outOfFovSpriteName)
                #tileSprite = getattr(ASSETS, tile.inFovSpriteName) #bad bad bad
                #drawX, drawY = GAME.camera.drawPosition(x, y)
                #tilePosition = (drawX*constants.CELL_WIDTH, drawY*constants.CELL_HEIGHT)

                fogSurface = pygame.Surface((constants.CELL_WIDTH,
                                             constants.CELL_HEIGHT))
                fogSurface.set_alpha(200)
                surface.blit(fogSurface, tilePosition)


def helperTextDims(text='a',font=constants.FONT_DEBUG):
    fontObject = font.render(text, False, (0,0,0))
    fontRect = fontObject.get_rect()
    return fontRect.width, fontRect.height

def helperTextObjects(text, textColor, bgColor=None):
    ''' Render text, return surface and bounding geometry '''
    textSurface = constants.FONT_DEBUG.render(text, True, textColor, bgColor)
    return textSurface, textSurface.get_rect()

def drawGameMessages():
    numMessages = min(len(GAME.messageHistory), constants.NUM_GAME_MESSAGES)
    if(numMessages==0):
        return 0
    messages = GAME.messageHistory[-numMessages:]

    _, height = helperTextDims()
    startY = SURFACE_MAIN.get_height() - numMessages*height

    drawTextList(SURFACE_MAIN, messages, startX=0, startY=startY)

def drawDebug():
    drawFPS()

def drawFPS():
    drawText(SURFACE_MAIN, "fps: " + str(int(CLOCK.get_fps())), (0,0), constants.COLOR_WHITE, 
             bgColor=constants.COLOR_BLACK)

def drawGame():

    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)

    drawLevelTiles()
    drawObjects()
    drawGameMessages()
    drawDebug()

    #SURFACE_MAIN.blit(SURFACE_FOG, (0,0))

    pygame.display.flip()

def drawObjects():
    for gameObj in GAME.currentLevel.objects:
        if getattr(gameObj, "deleted", False):
            return
        gameObj.draw()

def drawText(displaySurface, text, coords, textColor, bgColor=None):
    textSurf, textRect = helperTextObjects(text, textColor, bgColor=bgColor)
    textRect.topleft = coords
    displaySurface.blit(textSurf, textRect)
 
def drawTextList(surface, messages, startX=0, startY=0):
    '''
    Draw a list of text.  
    StartX and startY show upper left coordinate of textList on surface.
    '''
    _, height = helperTextDims()
    for idx, (message, textColor, bgColor) in enumerate(messages):
        drawText(surface,message, (startX, startY+idx*height),textColor,bgColor)  

class structAssets():
    '''
    Container class for spriteSheets, sprites, animations
    This super-duper needs to get refactored.  Kinda weird.
    '''
    def __init__(self):

        root = "pythonApplication1/" #fix this!
        #root = ""
        self.characterSpriteSheet = objSpriteSheet(root+'dawnlike/Characters/humanoid0.png')        
        self.toolsSpriteSheet = objSpriteSheet(root+'dawnlike/Items/Tool.png')
        self.potionSpriteSheet = objSpriteSheet(root+'dawnlike/Items/Potion.png')    
        self.jellySpriteSheet = objSpriteSheet(root+'16x16figs/jellySheet.png')

        self.demonSpriteSheet0 = objSpriteSheet(root+'dawnlike/Characters/Demon0.png')
        self.demonSpriteSheet1 = objSpriteSheet(root+'dawnlike/Characters/Demon1.png')

       
        self.s_wall = pygame.image.load(root+'16x16figs/wall.png').convert()
        self.s_wall_dark = pygame.image.load(root+'16x16figs/wall_dark.png').convert()
        self.s_floor = pygame.image.load(root+'16x16figs/floor.png').convert()
        self.s_floor_dark = pygame.image.load(root+'16x16figs/floor_dark.png').convert()

        self.a_player = self.characterSpriteSheet.getAnimation(colIdx=0, rowIdx=3, numSprites=3)        
        self.a_jelly = self.jellySpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=2)
        self.a_jelly_dead = self.jellySpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=1)

        self.a_goggles = self.toolsSpriteSheet.getAnimation(colIdx=3, rowIdx=0, numSprites=1)             
        self.a_red_potion = self.potionSpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=1)        

        self.a_demon = self.demonSpriteSheet0.getAnimation(colIdx=5, rowIdx=1, numSprites=1)  
        self.a_demon.extend(self.demonSpriteSheet1.getAnimation(colIdx=5, rowIdx=1, numSprites=1))
        self.a_demon_dead = self.demonSpriteSheet0.getAnimation(colIdx=5, rowIdx=1, numSprites=1)  

        #self.dungeon_ss = pygame.image.load(root+'')
        self.dungeon_ss = objSpriteSheet(root+'16x16figs/dungeon_tileset.png')
        # self.stairsDownSpriteSheet = objSpriteSheet(root+'32x32figs/stone_stairs_down.png',
        #                                                 imageUnitX=32, imageUnitY=32)
        self.s_ladder = self.dungeon_ss.getAnimation(colIdx=9, rowIdx=3, numSprites=1)
        
ASSETS = structAssets()
