import itertools
import copy
from typing import Tuple, List, Callable

import pygame
from pygame.locals import DOUBLEBUF, FULLSCREEN
import numpy as np

from qQuest import constants
from qQuest.game import CLOCK, GAME

SURFACE_MAIN = pygame.display.set_mode((constants.TOTAL_WIDTH_P,                                                            constants.TOTAL_HEIGHT_P ),
                                        FULLSCREEN | DOUBLEBUF)

SURFACE_MAP = pygame.Surface((constants.CAMERA_WIDTH_P, constants.CAMERA_HEIGHT_P))
SURFACE_CHYRON = pygame.Surface((constants.TOTAL_WIDTH_P, constants.CHYRON_HEIGHT_P))



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
                           spanX: int=1, spanY: int=1, scale: float=None
                           ) -> List[pygame.Surface]:
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

    def __init__(self, pos: Tuple[int], name: str, animationName: str, 
        level, **kwargs):
        ''' level type is Level.  dur.'''

        self.x, self.y = pos
        self.resyncGraphicPosition()

        self.name = name
        self.animationName = animationName
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg

        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.level = level

    def resyncGraphicPosition(self) -> None:
        # X and Y are ints and represent grid locations for most logic purposes
        # graphicX and graphicY are where the sprite is drawn, and can be floats.
        self.graphicX, self.graphicY = copy.copy(self.x), copy.copy(self.y)

    @property
    def animation(self) -> List[pygame.Surface]:
        return getattr(ASSETS,self.animationName)

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

        tileSprite = getattr(ASSETS, tile.inFovSpriteName) 
        tilePosition = ((x+camWidth)*constants.CELL_WIDTH, 
                        (y+camHeight)*constants.CELL_HEIGHT)
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
        retSprite = None

    elif numNotVisNeighbors == 1:
        retSprite = ASSETS.s_fow_oneSide[0].copy()

        if belowIsNotVis:
            rotAngle = 0
        if leftIsNotVis:
            rotAngle = -90
        if rightIsNotVis:
            rotAngle = 90
        if aboveIsNotVis:
            rotAngle = 180
        retSprite = pygame.transform.rotate(retSprite, rotAngle)

    elif numNotVisNeighbors == 2:
        
        if leftIsNotVis and rightIsNotVis:
            retSprite = ASSETS.s_fow_twoSideB[0].copy()
            retSprite = pygame.transform.rotate(retSprite, 90)
        elif belowIsNotVis and aboveIsNotVis:
            retSprite = ASSETS.s_fow_twoSideB[0].copy()     
        else:
            retSprite = ASSETS.s_fow_twoSide[0].copy()
            if rightIsNotVis and belowIsNotVis:
                rotAngle = 0
            elif rightIsNotVis and aboveIsNotVis:
                rotAngle=90
            elif aboveIsNotVis and leftIsNotVis:
                rotAngle = 180
            else:
                rotAngle = -90
            retSprite = pygame.transform.rotate(retSprite, rotAngle)

    elif numNotVisNeighbors == 3:
        retSprite = ASSETS.s_fow_threeSide[0].copy()

        if not belowIsNotVis:
            rotAngle = 90
        elif not leftIsNotVis:
            rotAngle = 0
        elif not rightIsNotVis:
            rotAngle = 180
        elif not aboveIsNotVis:
            rotAngle = -90
        retSprite = pygame.transform.rotate(retSprite, rotAngle)

    elif numNotVisNeighbors == 4:
        retSprite = ASSETS.s_fow_fourSide[0].copy() 

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
    #drawChyron()
    SURFACE_MAIN.blit(SURFACE_CHYRON, (0,SURFACE_MAP.get_height()))

    pygame.display.flip()


def drawChyron() -> None:
    ''' the bit of the UI drawn below the map'''

    SURFACE_CHYRON.fill(constants.COLOR_GREY)
    pass

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

        self.slimeSpriteSheet0 = objSpriteSheet(root+'dawnlike/Characters/Slime0.png')
        self.slimeSpriteSheet1 = objSpriteSheet(root+'dawnlike/Characters/Slime1.png')

        self.wall_dungeon_1 = pygame.image.load(root+'16x16figs/wall.png').convert()
        self.floor_dungeon_1 = pygame.image.load(root+'16x16figs/floor.png').convert()

        self.a_player = self.characterSpriteSheet.getAnimation(colIdx=0, rowIdx=3, numSprites=3)        
        self.a_jelly = self.jellySpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=2)
        self.a_jelly_dead = self.jellySpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=1)

        self.a_goggles = self.toolsSpriteSheet.getAnimation(colIdx=3, rowIdx=0, numSprites=1)             
        self.a_red_potion = self.potionSpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=1)        

        self.a_demon = self.demonSpriteSheet0.getAnimation(colIdx=5, rowIdx=1, numSprites=1)  
        self.a_demon.extend(self.demonSpriteSheet1.getAnimation(colIdx=5, rowIdx=1, numSprites=1))
        self.a_demon_dead = self.demonSpriteSheet0.getAnimation(colIdx=5, rowIdx=1, numSprites=1)  

        self.a_slime = self.slimeSpriteSheet0.getAnimation(colIdx=0, rowIdx=4, numSprites=1)  
        self.a_slime.extend(self.slimeSpriteSheet1.getAnimation(colIdx=0, rowIdx=4, numSprites=1))
        self.a_slime_dead = self.slimeSpriteSheet0.getAnimation(colIdx=0, rowIdx=4, numSprites=1)  

        #self.dungeon_ss = pygame.image.load(root+'')
        self.dungeon_ss = objSpriteSheet(root+'16x16figs/dungeon_tileset.png')
        self.s_ladder = self.dungeon_ss.getAnimation(colIdx=9, rowIdx=3, numSprites=1)

        self.fowSpriteSheet = objSpriteSheet(root+'16x16figs/fogOfWarPositiveB.png')
        self.s_fow_oneSide = self.fowSpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=1)
        self.s_fow_twoSide = self.fowSpriteSheet.getAnimation(colIdx=1, rowIdx=0, numSprites=1)
        self.s_fow_threeSide = self.fowSpriteSheet.getAnimation(colIdx=2, rowIdx=0,numSprites=1)
        self.s_fow_fourSide = self.fowSpriteSheet.getAnimation(colIdx=3, rowIdx=0, numSprites=1)
        self.s_fow_twoSideB = self.fowSpriteSheet.getAnimation(colIdx=1, rowIdx=1, numSprites=1)



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
