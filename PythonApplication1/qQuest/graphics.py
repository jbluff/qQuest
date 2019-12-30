''' This module contains all tools needed for drawing the game.

'''

import copy
import itertools
from collections import namedtuple
from functools import lru_cache
from typing import Tuple, List, Callable

import pygame
from pygame.locals import DOUBLEBUF, FULLSCREEN

try:
    from qQuest import constants
    from qQuest.constants import CLOCK #, GAME
    from qQuest.game import GameObject
    from qQuest.lib.visEffectsLib import EFFECTS
except ImportError:
    import constants
    from constants import CLOCK #, GAME
    from game import GameObject
    from lib.visEffectsLib import EFFECTS   


class Camera:
    ''' This class has two related purposes:  
        1.   Deciding what fits into the screen at a given time.
        2.   Deciding where on the screen something should be drawn.
    '''
    def __init__(self, viewer: 'characters.Viewer'=None):
        self.viewer = viewer
        self.updatePositionFromViewer() 

    def updatePositionFromViewer(self) -> None:
        ''' Recenter the camera on a Viewer instance.  The position here is
        stored in units of cells, not pixels, and can be a float.'''
        if self.viewer is not None:
            self.x = self.viewer.graphicX 
            self.y = self.viewer.graphicY 

    def canSee(self, x: int, y: int) -> bool:
        ''' Is coordinate (x,y), in cells, in sight of the camera?'''
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT

        xVisible = (x < self.x+w) and (x > self.x-w) 
        yVisible = (y < self.y+h) and (y > self.y-h)
        return xVisible and yVisible

    def drawPosition(self, x: int, y: int) -> Tuple[int]:
        '''Converts a game map position to a draw position, both still in units 
        of cells.'''
        w = constants.CAMERA_WIDTH
        h = constants.CAMERA_HEIGHT
        return (x - self.x + w/2 - 0.5, y - self.y + h/2 - 0.5)
 
    # def getUpperLeftCorner(self) -> Tuple[float]:
    #     ''' Returned in pixels '''
    #     w = constants.CAMERA_WIDTH
    #     h = constants.CAMERA_HEIGHT 

    #     xDrawingPos = (self.x-w/2+w)*constants.CELL_WIDTH
    #     yDrawingPos = (self.y-h/2+h)*constants.CELL_HEIGHT
    #     return (xDrawingPos, yDrawingPos)

    # def getViewingRect(self) -> pygame.Rect:
    #     w = constants.CAMERA_WIDTH
    #     h = constants.CAMERA_HEIGHT
    #     map_rect = pygame.Rect(*self.getUpperLeftCorner(),
    #                            w*constants.CELL_WIDTH,
    #                            h*constants.CELL_HEIGHT)
    #     return map_rect      


class SpriteSheet:
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
 

class Actor(GameObject):
    ''' This base class is used for everything that will be drawn on the screen.
    '''
    def __init__(self, *args, spriteDict=None, animationSpeed=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.resyncGraphicPosition()

        self.spriteDict = spriteDict
        self.animationSpeed = animationSpeed # in seconds 
        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

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

    def draw(self, surface: pygame.Surface,
                   viewer: 'creatures.Viewer'=None,
                   camera: 'graphics.Camera'=None,
                   drawHistory: bool=False) -> None:
        ''' Blits the Actor's current sprite in the appropriate location
        on the relevant surface.
        drawHistory means rather than assessing if a viewer can see it now, we assess whether a viewer has ever seen it. '''
        if viewer is not None:
            if drawHistory:
                doDraw = viewer.getTileIsExplored(self.x, self.y)
            else:
                doDraw = viewer.getTileIsVisible(self.x, self.y)
            if not doDraw:
                return 

        if camera is not None:
            if not camera.canSee(self.x, self.y):
                return        
            drawX, drawY = camera.drawPosition(self.graphicX, self.graphicY)
        else:
            drawX, drawY = self.x, self.y

        position = (round(drawX * constants.CELL_WIDTH), 
                    round(drawY * constants.CELL_HEIGHT)) 
        
        currentSprite = self.getCurrentSprite()
        surface.blit(currentSprite, position)
        self.addGraphicEffect(surface, position)

    def addGraphicEffect(self, surface, pos, effectName: str=None, 
                            relPos: Tuple[int]=(0, -16)):
        if getattr(self, 'activeEmote', None) is None: 
            return
        drawPos = pos[0]+relPos[0], pos[1]+relPos[1]
        effectSprite = ASSETS[EFFECTS[self.activeEmote]['spriteDict']][0] #no animations here, now
        surface.blit(effectSprite, drawPos)
        

def drawFogOfWar(surface: pygame.Surface, level: 'levels.Level', 
                 camera: 'graphics.Camera', viewer: 'creatures.Viewer') -> None:
    ''' Draws the fog of war.  Importantly-- also updates the Viewer's
    seen status. '''

    # this looping is dumb, we should be looping over the camera range instead of
    # the whole map.
        #     w = constants.CAMERA_WIDTH
        # h = constants.CAMERA_HEIGHT

        # xVisible = (x < self.x+w) and (x > self.x-w) 
        # yVisible = (y < self.y+h) and (y > self.y-h)

    mapHeight = len(level.map)
    mapWidth = len(level.map[0])
    for (x, y) in itertools.product(range(mapWidth), range(mapHeight)):

        if not camera.canSee(x, y):
            continue
        drawX, drawY = camera.drawPosition(x, y)
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
            
        # If the cell has never been seen, we're done.  If not, we may need to
        # add some ragged edges.
        if not tileIsExplored:
            continue

        # First the blacked ragged edges surrounding explored space.
        fowSprite = getFowEdgeSprite(x, y, (mapWidth, mapHeight),                                                       viewer.getTileIsExplored)
        if fowSprite is not None:
            surface.blit(fowSprite, tilePosition)

        # Then the darkened edges around currently visible space
        if not tileIsVisibleToViewer:
            continue
        fowSprite = getFowEdgeSprite(x, y, (mapWidth, mapHeight),                                                           viewer.getTileIsVisible)
        if fowSprite is not None:
            fowSprite.set_alpha(200)
            #print('drawing transparent edge')
            surface.blit(fowSprite, tilePosition)

def getFowEdgeSprite(x: int, y: int, limits: Tuple[int],
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

def drawGameMessages(surface: pygame.Surface, game: 'game.Game') -> None:
    numMessages = min(len(game.messageHistory), constants.NUM_GAME_MESSAGES)
    if numMessages==0:
        return 0
    messages = game.messageHistory[-numMessages:]

    _, height = helperTextDims()
    startY = surface.get_height() - numMessages*height
    drawTextList(surface, messages, startX=0, startY=startY)

def drawDebug(surface: pygame.Surface) -> None:
    drawFPS(surface)

def drawFPS(surface: pygame.Surface) -> None:
    drawText(surface, "fps: " + str(int(CLOCK.get_fps())), (0,0), constants.COLOR_WHITE, 
             bgColor=constants.COLOR_BLACK)

def drawObjects(surface: pygame.Surface, objects: List[Actor], **kwargs) -> None:
    for gameObj in objects:
        if gameObj is None:
            continue
        if getattr(gameObj, "deleted", False):
            return
        gameObj.draw(surface, **kwargs), 

def drawGame(mainSurface, mapSurface, chyronSurface, game: 'game.Game') -> None:

    vcKwargs = {'viewer': game.viewer, 'camera': game.camera, }
    level = game.currentLevel

    mainSurface.fill(constants.COLOR_BLACK)
    
    # the map and such.
    mapSurface.fill(constants.COLOR_BLACK)
    drawObjects(mapSurface, level.tilesFlattened, drawHistory=True, **vcKwargs)
    drawObjects(mapSurface, level.objects, **vcKwargs)
    drawFogOfWar(mapSurface, level, **vcKwargs)
    drawGameMessages(mapSurface, game)
    mainSurface.blit(mapSurface, (0,0))

    # off-map portions of the interface 
    drawChyron(chyronSurface, game)
    mainSurface.blit(chyronSurface, (0,mapSurface.get_height()))

    drawDebug(mainSurface)
    pygame.display.flip()

def drawChyron(surface: pygame.Surface, game: 'game.Game') -> None:
    ''' the bit of the UI drawn below the map'''
    surface.fill(constants.COLOR_GREY)

    # health
    SURFACE_HEALTH = pygame.Surface((11 * constants.CELL_WIDTH, 3*constants.CELL_HEIGHT))
    SURFACE_HEALTH.fill(constants.COLOR_GREY)
    xPos = 0.5*constants.CELL_WIDTH
    yPos = 0.5*constants.CELL_HEIGHT
    fullHeartSprite = ASSETS[EFFECTS['fullHeart']['spriteDict']][0]
    emptyHeartSprite = ASSETS[EFFECTS['emptyHeart']['spriteDict']][0]
    for idx in range(1,game.player.maxHp+1):
        if idx <= game.player.hp:
            SURFACE_HEALTH.blit(fullHeartSprite, (xPos, yPos))
        else:
            SURFACE_HEALTH.blit(emptyHeartSprite, (xPos, yPos))
        xPos += constants.CELL_WIDTH
        if idx % 10 == 0:
            xPos = 0.5*constants.CELL_WIDTH
            yPos += constants.CELL_HEIGHT


    # stats
    pos = [15*constants.CELL_WIDTH, 2*constants.CELL_WIDTH]
    statColorArgs = [constants.COLOR_DARKERGREY, constants.COLOR_GREY]
    statStr = [[f'dex: {game.player.dexterity}({game.player.baseDexterity})',*statColorArgs],
               [f'str: {game.player.strength}({game.player.baseStrength})',*statColorArgs],
               [f'def: {game.player.defense}({game.player.baseDefense})',*statColorArgs]]
    drawTextList(surface, statStr, *pos)

    
    surface.blit(SURFACE_HEALTH, ( 8,8))



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
def loadSpriteSheet(path: str) -> SpriteSheet:
    ''' load a sprite sheet, but memoized. 
    Probably unnecessary for the amount of data we're dealing with.'''
    return SpriteSheet(path)


def spriteDebugger(surface) -> None:
    # show all the sprites in ASSETS, with their names
    surface.fill(constants.COLOR_WHITE)

    attrs = ASSETS.__dict__.keys()

    LINE_HEIGHT = 20
    vertIdx = 0.25
    for attr in attrs:
        if not (attr.startswith("s_") or attr.startswith("a_")):
            continue
        vertPos = vertIdx*LINE_HEIGHT
        drawText(surface, attr, (20, vertPos), constants.COLOR_BLACK, bgColor=constants.COLOR_WHITE)

        attrVal = getattr(ASSETS, attr)
        if type(attrVal) is not list:
            attrVal = [attrVal,]

        horIdx = 0
        for sprite in attrVal:
            pos = (100+horIdx*20, vertPos)
            surface.blit(sprite, pos)
            horIdx += 1

        vertIdx += 1
    pygame.display.flip()

ASSETS = structAssets()
