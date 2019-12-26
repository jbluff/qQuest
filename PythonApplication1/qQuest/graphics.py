import itertools
import copy
from typing import Tuple, List, Callable
from functools import lru_cache
from collections import namedtuple

import pygame
from pygame.locals import DOUBLEBUF, FULLSCREEN
import numpy as np

from qQuest import constants
from qQuest.game import CLOCK, GAME
from qQuest.lib.visEffectsLib import EFFECTS

SURFACE_MAIN = pygame.display.set_mode((constants.TOTAL_WIDTH_P,                                                            constants.TOTAL_HEIGHT_P ),
                                        FULLSCREEN | DOUBLEBUF)

SURFACE_MAP = pygame.Surface((constants.CAMERA_WIDTH_P, constants.CAMERA_HEIGHT_P))
SURFACE_CHYRON = pygame.Surface((constants.TOTAL_WIDTH_P, constants.CHYRON_HEIGHT_P))

SURFACE_HEALTH = pygame.Surface((11 * constants.CELL_WIDTH, 3*constants.CELL_HEIGHT))


class Camera:
    def __init__(self, viewer=None):
        self.viewer = viewer
        self.updatePositionFromViewer() # in cells

    
    def updatePositionFromViewer(self) -> None:
        if self.viewer is not None:
            self.x = self.viewer.graphicX # x
            self.y = self.viewer.graphicY # y

    def canSee(self, x: int, y: int) -> bool:
        ''' is the specified cell within the range of the camera?'''
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT

        xVisible = (x < self.x+w) and (x > self.x-w) 
        yVisible = (y < self.y+h) and (y > self.y-h)
        return xVisible and yVisible

    def getUpperLeftCorner(self) -> Tuple[float]:
        ''' Returned in pixels '''
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT 

        xDrawingPos = (self.x-w/2+w)*constants.CELL_WIDTH
        yDrawingPos = (self.y-h/2+h)*constants.CELL_HEIGHT
        return (xDrawingPos, yDrawingPos)

    def getViewingRect(self) -> pygame.Rect:
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT
        map_rect = pygame.Rect(*self.getUpperLeftCorner(),
                               w*constants.CELL_WIDTH,
                               h*constants.CELL_HEIGHT)
        return map_rect

    def drawPosition(self, x: int, y: int) -> Tuple[int]:
        '''Converts a game map position to a draw position, both still in units 
        of cells.'''
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT
        return (x - self.x + w/2 - 0.5, y - self.y + h/2 - 0.5)
        

class objSpriteSheet:
    ''' loads a sprite sheet, allows pulling out animations. '''
    def __init__(self, fileName: str, 
                       imageUnitX: int=constants.CELL_WIDTH, 
                       imageUnitY: int=constants.CELL_HEIGHT) -> None:
        ''' 
        imageUnitX/Y define the atomic size of an image on the sprite sheet, in pixels.
            images from the sprite sheet can be selected to take up e.g. several atomic units.
            images can also be scaled from their sprite sheet sizes
        '''
        self.spriteSheet = pygame.image.load(fileName).convert()
        self.imageUnitX = imageUnitX
        self.imageUnitY = imageUnitY
        
    def getAnimation(self, colIdx: int=0, rowIdx: int=0, numSprites: int=1, 
                           spanX: int=1, spanY: int=1, scale: float=None,
                           **kwargs) -> List[pygame.Surface]:
        ''' 
        spanX and spanY define size of image on the spriteSheet, in units of imageUnitX/Y
        colIdx and rowIdx should where to find the first sprite on the spritesheet
        numSprites is how many (in a row) to take to define an animation.
        '''
        startX, startY = colIdx * self.imageUnitX, rowIdx * self.imageUnitY
        width, height = spanX * self.imageUnitX, spanY * self.imageUnitY

        imageList = []

        for idx in range(numSprites):
            image = pygame.Surface([width, height])#.convert()
            image.blit(self.spriteSheet, (0,0), (startX+idx*width, startY, width, height))
            image.set_colorkey(constants.COLOR_BLACK)

            if scale:
                raise NotImplementedError
                newWidth = self.imageUnitX*spanX*scale[0]
                newHeight = self.imageUnitY*spanY*scale[1]
                image = pygame.transform.scale(image, (newWidth, newHeight))
            imageList.append(image)
        return imageList
 

class Actor():
    '''Actors are all drawn things which are not floor ties.  May reflect player, NPCs, items'''

    def __init__(self, pos: Tuple[int], name: str='defaultName', 
        level=None, uniqueName='', spriteDict=None, **kwargs):
        ''' level type is Level.  dur.'''

        self.x, self.y = pos
        self.resyncGraphicPosition()

        self.name = name
        self.uniqueName = uniqueName if uniqueName != '' else name

        self.spriteDict = spriteDict
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg
        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.level = level

        #todo:  spriteDict will become required here

    def resyncGraphicPosition(self) -> None:
        # X and Y are ints and represent grid locations for most logic purposes
        # graphicX and graphicY are where the sprite is drawn, and can be floats.
        self.graphicX, self.graphicY = copy.copy(self.x), copy.copy(self.y)

    @property
    def animation(self) -> List[pygame.Surface]:
        return ASSETS[self.spriteDict]

    def getCurrentSprite(self) -> pygame.Surface:
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

    def draw(self) -> None:
        isInViewerFov = GAME.viewer.getTileIsVisible(self.x, self.y)
        if not isInViewerFov:
            return 

        if not GAME.camera.canSee(self.x, self.y):
            return

        currentSprite = self.getCurrentSprite()
        drawX, drawY = GAME.camera.drawPosition(self.graphicX, self.graphicY)
        position = (round(drawX * constants.CELL_WIDTH), 
                    round(drawY * constants.CELL_HEIGHT)) 
     
        SURFACE_MAP.blit(currentSprite, position)
        self.addGraphicEffect(position)

    # def emote(self, effectName:str, relPos: Tuple[int]=(0, 10),
    #                 duration:int=10) -> None:
    #     ''' Emotes things near an Actor.  This command starts them.'''
    #     self.emoteEffectName = effectName
    #     pass

    def addGraphicEffect(self, pos, effectName: str=None, 
                            relPos: Tuple[int]=(0, -16)):
        #self.currentEffectsList
        if getattr(self, 'activeEmote', None) is None: #self.activeEmote is None:
            return
        drawPos = pos[0]+relPos[0], pos[1]+relPos[1]

        # if not isInViewerFov:
        #     return 

        # if not GAME.camera.canSee(self.x, self.y):
        #     return

        effectSprite = ASSETS[EFFECTS[self.activeEmote]['spriteDict']][0] #no animations here, now
        SURFACE_MAP.blit(effectSprite, drawPos)
        

def compileBackgroundTiles(level=None) -> pygame.Surface:
    ''' Blits together all of the images that make up the background of a given map.
    This only needs to be called roughly once, when a level is first instantiated.
    level is Level instance.
    '''

    if level is None:
        level = GAME.currentLevel

    mapHeight, mapWidth = np.array(level.map).shape
    camWidth, camHeight = constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT

    # note the +/- camWidth and camHeight buffer regions.
    level_surface = pygame.Surface(((mapWidth+2*camWidth)*constants.CELL_WIDTH,
                                    (mapHeight+2*camHeight)*constants.CELL_HEIGHT))

    for (x, y) in itertools.product(range(mapWidth), range(mapHeight)):
        tile = level.map[y][x]

        tilePosition = ((x+camWidth)*constants.CELL_WIDTH, 
                        (y+camHeight)*constants.CELL_HEIGHT)
        tileSprite = ASSETS[tile.spriteDict][0] # no animations here
        level_surface.blit(tileSprite, tilePosition)

    return level_surface

def drawBackground():    
    ''' blits the pre-compiled background tiles (walls, floor, etc)'''
    level = GAME.currentLevel
    surface = SURFACE_MAP

    map_rect = GAME.camera.getViewingRect()
    map_surface = ASSETS.compiledLevelMaps[level.uniqueID]
    map_subsurface = map_surface.subsurface(map_rect)
    # I don't actually know where this offset comes from.
    pos = (round(-0.5*constants.CELL_WIDTH),round(-0.5*constants.CELL_HEIGHT))
    surface.blit(map_subsurface, pos)

def drawFogOfWar(viewer=None) -> None:
    ''' viewer is Viewer instance. '''
    if viewer is None:
        viewer = GAME.viewer
    level = GAME.currentLevel
    surface = SURFACE_MAP

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
            tileIsExplored = True
        else: 
            # can't see the tile-- it should be blacked entirely or darkened
            blankTile = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
            blankTile.fill(constants.COLOR_BLACK)
 
            if tileIsExplored:
                blankTile.set_alpha(200) # only darken
            surface.blit(blankTile, tilePosition)
            
        # Now we add the ragged edges, if applicable. 
        if not tileIsExplored:
            continue

        # First the blacked ragged edges surrounding explored space.
        fowSprite = drawFowEdges(x, y, (mapWidth, mapHeight),                                                       viewer.getTileIsExplored)
        if fowSprite is not None:
            surface.blit(fowSprite, tilePosition)

        # Then the darkened edges around currently visible space
        if not tileIsVisibleToViewer:
            continue
        fowSprite = drawFowEdges(x, y, (mapWidth, mapHeight),                                                       viewer.getTileIsVisible)
        if fowSprite is not None:
            fowSprite.set_alpha(200)
            surface.blit(fowSprite, tilePosition)

def drawFowEdges(x: int, y: int, limits: Tuple[int],
                 testFunction: Callable[[int,int], bool]) -> None:
    ''' On a visible tile, draw the overhanging FOW effect, if applicable.
    We could replace this (in fewer LOC) with just doing each side as needed
    and rotating and reblitting. a single image.  Maybe we should, dunno, but I like 
    the flexibility, because later we won't get away with that trick for walls.
    Meh.  Need to find something a bit more elegant, eventually.'''
    aboveIsNotVis = True if (y==0) else not testFunction(x, y-1)
    leftIsNotVis = True if (x==0) else not testFunction(x-1, y)
    belowIsNotVis = True if (y==limits[1]-1) else not testFunction(x, y+1)
    rightIsNotVis = True if (x==limits[0]-1) else not testFunction(x+1, y)

    numNotVisNeighbors = aboveIsNotVis+leftIsNotVis+belowIsNotVis+rightIsNotVis

    if numNotVisNeighbors == 0:
        return None

    elif numNotVisNeighbors == 1:
        spriteDict = EFFECTS['fow_oneSide']['spriteDict']
        if belowIsNotVis: rotAngle = 0
        elif leftIsNotVis: rotAngle = -90
        elif rightIsNotVis: rotAngle = 90
        elif aboveIsNotVis: rotAngle = 180
 
    elif numNotVisNeighbors == 2:
        if leftIsNotVis and rightIsNotVis:
            spriteDict = EFFECTS['fow_twoSideB']['spriteDict']
            rotAngle = 90
        elif belowIsNotVis and aboveIsNotVis:
            spriteDict = EFFECTS['fow_twoSideB']['spriteDict']
            rotAngle = 0
        else:  
            spriteDict = EFFECTS['fow_twoSide']['spriteDict']
            if rightIsNotVis and belowIsNotVis: rotAngle = 0
            elif rightIsNotVis and aboveIsNotVis: rotAngle=90
            elif aboveIsNotVis and leftIsNotVis: rotAngle = 180
            else: rotAngle = -90

    elif numNotVisNeighbors == 3:
        spriteDict = EFFECTS['fow_threeSide']['spriteDict']
        if not belowIsNotVis: rotAngle = 90
        elif not leftIsNotVis: rotAngle = 0
        elif not rightIsNotVis: rotAngle = 180
        elif not aboveIsNotVis: rotAngle = -90

    elif numNotVisNeighbors == 4:
        rotAngle = 0
        spriteDict = EFFECTS['fow_fourSide']['spriteDict']

    retSprite = ASSETS[spriteDict][0].copy()  
    retSprite = pygame.transform.rotate(retSprite, rotAngle)
    return retSprite

def helperTextDims(text='a',font=constants.FONT_DEBUG) -> Tuple[int]:
    fontObject = font.render(text, False, (0,0,0))
    fontRect = fontObject.get_rect()
    return fontRect.width, fontRect.height

def helperTextObjects(text, textColor, bgColor=None):
    ''' Render text, return surface and bounding geometry '''
    textSurface = constants.FONT_DEBUG.render(text, True, textColor, bgColor)
    return textSurface, textSurface.get_rect()

def drawGameMessages() -> None:
    numMessages = min(len(GAME.messageHistory), constants.NUM_GAME_MESSAGES)
    if(numMessages==0):
        return 0
    messages = GAME.messageHistory[-numMessages:]

    _, height = helperTextDims()
    startY = SURFACE_MAP.get_height() - numMessages*height

    drawTextList(SURFACE_MAP, messages, startX=0, startY=startY)

def drawDebug() -> None:
    drawFPS()

def drawFPS() -> None:
    drawText(SURFACE_MAP, "fps: " + str(int(CLOCK.get_fps())), (0,0), constants.COLOR_WHITE, 
             bgColor=constants.COLOR_BLACK)

def drawGame() -> None:

    SURFACE_MAIN.fill(constants.COLOR_BLACK)
    
    ''' draw the map and such '''
    drawBackground()
    drawObjects()
    drawFogOfWar()
    
    drawGameMessages()
    drawDebug()
    SURFACE_MAIN.blit(SURFACE_MAP, (0,0))

    ''' off-map portions of the interface '''
    drawChyron()
    SURFACE_MAIN.blit(SURFACE_CHYRON, (0,SURFACE_MAP.get_height()))

    pygame.display.flip()

def drawChyron() -> None:
    ''' the bit of the UI drawn below the map'''
    SURFACE_CHYRON.fill(constants.COLOR_GREY)

    SURFACE_HEALTH.fill(constants.COLOR_GREY)
    xPos = 0.5*constants.CELL_WIDTH
    yPos = 0.5*constants.CELL_HEIGHT
    fullHeartSprite = ASSETS[EFFECTS['fullHeart']['spriteDict']][0]
    emptyHeartSprite = ASSETS[EFFECTS['emptyHeart']['spriteDict']][0]
    for idx in range(1,GAME.player.maxHp+1):
        if idx < GAME.player.hp:
            SURFACE_HEALTH.blit(fullHeartSprite, (xPos, yPos))
        else:
            SURFACE_HEALTH.blit(emptyHeartSprite, (xPos, yPos))
        xPos += constants.CELL_WIDTH
        if idx % 10 == 0:
            xPos = 0.5*constants.CELL_WIDTH
            yPos += constants.CELL_HEIGHT
    
    SURFACE_CHYRON.blit(SURFACE_HEALTH, ( 8,8))

def drawObjects() -> None:
    for gameObj in GAME.currentLevel.objects:
        if getattr(gameObj, "deleted", False):
            return
        gameObj.draw()

def drawText(displaySurface: pygame.Surface, text: str, coords: Tuple[int], 
             textColor: Tuple[int], bgColor: Tuple[int]=None) -> None:
    textSurf, textRect = helperTextObjects(text, textColor, bgColor=bgColor)
    textRect.topleft = coords
    displaySurface.blit(textSurf, textRect)
 
def drawTextList(surface: pygame.Surface, messages: tuple, 
                 startX: int=0, startY: int=0) -> None:
    ''' StartX and startY show upper left coordinate of textList on surface.
    '''
    _, height = helperTextDims()
    for idx, (message, textColor, bgColor) in enumerate(messages):
        drawText(surface,message, (startX, startY+idx*height),textColor,bgColor)  

class structAssets():
    ''' Container class for sprites, animations, and compiled level backgrounds.
    It starts empty and gets filled via requests & memoization.
    '''
    def __init__(self):
        self.compiledLevelMaps = {}
        self.root = "pythonApplication1/" #fix this!

    @lru_cache(maxsize=256)
    def __getitem__(self, dictTuple: Tuple[namedtuple]) -> List[pygame.Surface]:
        '''
        Key should be a tuple of namedtuples with {'path', 'colIdx', 'rowIdx', 'numSprites=1'}.
        Output is an Animation (list of Surfaces).

        the 'dictTuple' entries/spriteDicts are actually namedtuples, which are hashable.

        Memoized
        '''
        if type(dictTuple) == namedtuple:
            dictTuple = (dictTuple,)
        
        animationOut = []
        for spriteDict in dictTuple:
            #spriteDict = spriteDict._asdict() #From namedtuple to dict.
            sheet = loadSpriteSheet(self.root+spriteDict.path)
            spriteSurface = sheet.getAnimation(colIdx=spriteDict.colIdx,
                                               rowIdx=spriteDict.rowIdx,
                                               numSprites=spriteDict.numSprites)
            animationOut.extend(spriteSurface)
        return animationOut


@lru_cache(maxsize=256)
def loadSpriteSheet(path: str) -> objSpriteSheet:
    ''' load a sprite sheet, but memoized. 
    Probably unnecessary for the amount of data we're dealing with.'''
    return objSpriteSheet(path)


def spriteDebugger() -> None:
    # show all the sprites in ASSETS, with their names
    SURFACE_MAIN.fill(constants.COLOR_WHITE)

    attrs = ASSETS.__dict__.keys()

    LINE_HEIGHT = 20
    vertIdx = 0.25
    for attr in attrs:
        if not (attr.startswith("s_") or attr.startswith("a_")):
            continue
        vertPos = vertIdx*LINE_HEIGHT
        drawText(SURFACE_MAIN, attr, (20, vertPos), constants.COLOR_BLACK, bgColor=constants.COLOR_WHITE)

        attrVal = getattr(ASSETS, attr)
        if type(attrVal) is not list:
            attrVal = [attrVal,]

        horIdx = 0
        for sprite in attrVal:
            pos = (100+horIdx*20, vertPos)
            SURFACE_MAIN.blit(sprite, pos)
            horIdx += 1

        vertIdx += 1
    pygame.display.flip()

ASSETS = structAssets()
