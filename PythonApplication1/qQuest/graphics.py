import itertools
import copy

import pygame
import numpy as np

from qQuest import constants
from qQuest.game import SURFACE_MAIN, CLOCK, GAME

class Camera:
    def __init__(self, viewer=None):
        self.viewer = viewer
        self.updatePositionFromViewer() # in cells

    
    def updatePositionFromViewer(self):
        if self.viewer is not None:
            self.x = self.viewer.graphicX # x
            self.y = self.viewer.graphicY # y

    def canSee(self, x, y):
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT

        #isVisisble = (x < self.x+w/2) and (x > self.x-w/2) and (y < self.y+h/2) and (y > self.y-h/2)
        #xVisible = (x < self.x+w/2) and (x > self.x-w/2) 
        xVisible = (x < self.x+w) and (x > self.x-w) 
        yVisible = (y < self.y+h) and (y > self.y-h)

        return xVisible and yVisible

    def getUpperLeftCorner(self):
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT 

        # the -w/2 and -h/2 are to center the camera,
        # the +w and +h are to deal with the map buffer
        # return (self.x-w/2+w)*constants.CELL_WIDTH, (self.y-h/2+h)*constants.CELL_HEIGHT
        xDrawingPos = (self.x-w/2+w)*constants.CELL_WIDTH
        yDrawingPos = (self.y-h/2+h)*constants.CELL_HEIGHT
        return (xDrawingPos, yDrawingPos)


    def getViewingRect(self):
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT
        map_rect = pygame.Rect(*self.getUpperLeftCorner(),
                               w*constants.CELL_WIDTH,
                               h*constants.CELL_HEIGHT)
        return map_rect

    '''Converts a game map position to a draw position, both still in units of cells'''
    def drawPosition(self, x, y):
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT

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
        self.resyncGraphicPosition()

        self.name = name
        self.animationName = animationName
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg

        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.level = level

    def resyncGraphicPosition(self):
        # X and Y are ints annd represent grid locations for most logic purposes
        # graphicX and graphicY are where the sprite is drawn, and can be floats.
        self.graphicX, self.graphicY = copy.copy(self.x), copy.copy(self.y)

    @property
    def animation(self):
        return getattr(ASSETS,self.animationName)

    def getCurrentSprite(self):
        if len(self.animation) == 1:
            return self.animation[0]
        
        if CLOCK.get_fps() > 0.0:
            self.flickerTimer += 1/CLOCK.get_fps() 

        if self.flickerTimer > self.flickerSpeed:
            self.flickerTimer = 0
            self.spriteImageNum += 1
                
            if self.spriteImageNum >= len(self.animation): #modulo
                self.spriteImageNum = 0
        return self.animation[self.spriteImageNum]

    def draw(self):
        isInViewerFov = GAME.viewer.getTileIsVisible(self.x, self.y)
        if not isInViewerFov:
            return 

        if not GAME.camera.canSee(self.x, self.y):
            return

        currentSprite = self.getCurrentSprite()
        drawX, drawY = GAME.camera.drawPosition(self.graphicX, self.graphicY)
        position = (round(drawX * constants.CELL_WIDTH), 
                    round(drawY * constants.CELL_HEIGHT)) 
        SURFACE_MAIN.blit(currentSprite, position)

''' Blits together all of the images that make up the background of a given map.
This only needs to be called roughly once, when a level is first instantiated.
'''
def compileBackgroundTiles(level=None) -> pygame.Surface:
    if level is None:
        level = GAME.currentLevel

    mapHeight, mapWidth = np.array(level.map).shape
    camWidth, camHeight = constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT

    # note the +/- camWidth and camHeight buffer regions.
    level_surface = pygame.Surface(((mapWidth+2*camWidth)*constants.CELL_WIDTH,
                                    (mapHeight+2*camHeight)*constants.CELL_HEIGHT))

    for (x, y) in itertools.product(range(mapWidth), range(mapHeight)):
        tile = level.map[y][x]

        tileSprite = getattr(ASSETS, tile.inFovSpriteName) 
        tilePosition = ((x+camWidth)*constants.CELL_WIDTH, 
                        (y+camHeight)*constants.CELL_HEIGHT)
        level_surface.blit(tileSprite, tilePosition)

    return level_surface

# draws the pre-compiled background tiles (walls, floor, etc)
def drawBackground(surface, level):    
    map_rect = GAME.camera.getViewingRect()
    map_surface = ASSETS.compiledLevelMaps[level.uniqueID]
    map_subsurface = map_surface.subsurface(map_rect)
    # I don't actually know where this offset comes from.
    pos = (round(-0.5*constants.CELL_WIDTH),round(-0.5*constants.CELL_HEIGHT))
    surface.blit(map_subsurface, pos)

''' The draws the game map.  Everything other than objects and menus and text. '''
def drawLevel(viewer=None):
    if viewer is None:
        viewer = GAME.viewer
    level = GAME.currentLevel
    surface = SURFACE_MAIN

    drawBackground(surface, level)

    # this looping is dumb, we should be looping over the camera range instead of
    # the whole map.
    mapHeight, mapWidth = np.array(level.map).shape
    for (x, y) in itertools.product(range(mapWidth), range(mapHeight)):

        if not GAME.camera.canSee(x, y):
            continue
        drawX, drawY = GAME.camera.drawPosition(x, y)
        tilePosition = (round(drawX*constants.CELL_WIDTH), 
                        round(drawY*constants.CELL_HEIGHT))

        tileIsVisibleToViewer = viewer.getTileIsVisible(x, y)
        tileIsExplored = viewer.getTileIsExplored(x, y)

        if tileIsVisibleToViewer:
            viewer.setTileIsExplored(x, y)

        else: 
            # blankTile = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
            # blankTile.fill(constants.COLOR_BLACK)

            blankTile = getNeighborDependentTile(viewer, x, y, (mapWidth, mapHeight))
            # seen it before tho -- fog of war.
            if tileIsExplored:
                blankTile.set_alpha(200)
            surface.blit(blankTile, tilePosition)

def getNeighborDependentTile(viewer, x, y, limits):

    aboveIsVis = False if (y==0) else viewer.getTileIsVisible(x, y-1)
    leftIsVis = False if (x==0) else viewer.getTileIsVisible(x-1, y)
    belowIsVis = False if (y==limits[1]-1) else viewer.getTileIsVisible(x, y+1)
    rightIsVis = False if (x==limits[0]-1) else viewer.getTileIsVisible(x+1, y)

    numVisNeighbors = aboveIsVis+leftIsVis+belowIsVis+rightIsVis

    blankTile = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
    blankTile.fill(constants.COLOR_BLACK)
    return blankTile

    numVisNeighbors = aboveIsVis+leftIsVis+belowIsVis+rightIsVis

    
    # blankTile = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
    # blankTile.fill(constants.COLOR_BLACK)
    # return blankTile

    if numVisNeighbors == 0:
        return ASSETS.s_fow_full[0]#.copy()

    if numVisNeighbors == 1:
        if aboveIsVis:
            pass
            #return ASSETS.s_fow_threeNeighbor[0].copy()

    return ASSETS.s_fow_full[0]#.copy()


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

    SURFACE_MAIN.fill(constants.COLOR_BLACK)

    drawLevel()
    drawObjects()
    drawGameMessages()
    drawDebug()

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
    ''' StartX and startY show upper left coordinate of textList on surface.
    '''
    _, height = helperTextDims()
    for idx, (message, textColor, bgColor) in enumerate(messages):
        drawText(surface,message, (startX, startY+idx*height),textColor,bgColor)  

class structAssets():
    ''' Container class for spriteSheets, sprites, animations
    This super-duper needs to get refactored.  Kinda weird.
    '''
    def __init__(self):

        self.compiledLevelMaps = {}

        root = "pythonApplication1/" #fix this!
        #root = ""
        self.characterSpriteSheet = objSpriteSheet(root+'dawnlike/Characters/humanoid0.png')        
        self.toolsSpriteSheet = objSpriteSheet(root+'dawnlike/Items/Tool.png')
        self.potionSpriteSheet = objSpriteSheet(root+'dawnlike/Items/Potion.png')    
        self.jellySpriteSheet = objSpriteSheet(root+'16x16figs/jellySheet.png')

        self.demonSpriteSheet0 = objSpriteSheet(root+'dawnlike/Characters/Demon0.png')
        self.demonSpriteSheet1 = objSpriteSheet(root+'dawnlike/Characters/Demon1.png')

       
        self.s_wall = pygame.image.load(root+'16x16figs/wall.png').convert()
        # self.s_wall_dark = pygame.image.load(root+'16x16figs/wall_dark.png').convert()
        self.s_floor = pygame.image.load(root+'16x16figs/floor.png').convert()
        # self.s_floor_dark = pygame.image.load(root+'16x16figs/floor_dark.png').convert()

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

        self.fowSpriteSheet = objSpriteSheet(root+'16x16figs/fogOfWar.png')
        self.s_fow_full = self.fowSpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=1)
        self.s_fow_threeNeighbor = self.fowSpriteSheet.getAnimation(colIdx=1, rowIdx=0, numSprites=1)#, convAlpha=True)
        self.s_fow_twoNeighbor = self.fowSpriteSheet.getAnimation(colIdx=2, rowIdx=0, numSprites=1)
        self.s_fow_twoNeighborAcross = self.fowSpriteSheet.getAnimation(colIdx=3, rowIdx=0, numSprites=1)
        self.s_fow_oneNeighbor = self.fowSpriteSheet.getAnimation(colIdx=4, rowIdx=0, numSprites=1)
        self.s_fow_noNeighbors = self.fowSpriteSheet.getAnimation(colIdx=5, rowIdx=0, numSprites=1)


ASSETS = structAssets()
