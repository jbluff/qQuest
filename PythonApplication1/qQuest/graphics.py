import pygame

from qQuest import constants
from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME


#ASSETS = structAssets() #can this be in globals?

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
 
def helperTextDims(text='a',font=constants.FONT_DEBUG):
    fontObject = font.render(text, False, (0,0,0))
    fontRect = fontObject.get_rect()
    return fontRect.width, fontRect.height

def helperTextObjects(text, textColor, bgColor=None):
    ''' Render text, return surface and bounding geometry '''
    textSurface = constants.FONT_DEBUG.render(text, True, textColor, bgColor)
    return textSurface, textSurface.get_rect()

def drawMap(mapToDraw, fovMap):
    surface = SURFACE_MAIN
    for x in range(0, GAME.mapWidth):#constants.MAP_WIDTH):
        for y in range(0, GAME.mapHeight):#constants.MAP_HEIGHT):

            isVisible = fovMap.fov[y, x]
            if isVisible:
                mapToDraw[x][y].explored = True
                if mapToDraw[x][y].blockPath == True: 
                    surface.blit(ASSETS.s_wall, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    surface.blit(ASSETS.s_floor, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
            elif mapToDraw[x][y].explored == True:
                if mapToDraw[x][y].blockPath == True: 
                    surface.blit(ASSETS.s_wall_dark, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    surface.blit(ASSETS.s_floor_dark, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

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

#TODO:  make the fovMap an actor substitutable thing
def drawGame(fovMap=None):
    if fovMap is None:
        fovMap = GAME.currentLevel.currentFovMap
    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
    drawMap(GAME.currentLevel.currentMap, fovMap)

    drawObjects(fovMap)

    drawGameMessages()
    drawDebug()

    pygame.display.flip()

def drawObjects(fovMap):
    for gameObj in GAME.currentLevel.currentObjects:
        if gameObj.item:
            if gameObj.deleted:# or gameObj.currentContainer:
                return
        gameObj.draw(fovMap)

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
    for idx, (message, color) in enumerate(messages):
        drawText(surface,message, (startX, startY+idx*height),color,constants.COLOR_BLACK)  

class structAssets():
    '''
    Container class for spriteSheets, sprites, animations
    '''
    def __init__(self):

        #import os
        #print(os.getcwd())
        root = "pythonApplication1/" #fix this!
        #root = ""
        self.characterSpriteSheet = objSpriteSheet(root+'dawnlike/Characters/humanoid0.png')        
        self.toolsSpriteSheet = objSpriteSheet(root+'dawnlike/Items/Tool.png')
        self.potionSpriteSheet = objSpriteSheet(root+'dawnlike/Items/Potion.png')    
        self.jellySpriteSheet = objSpriteSheet(root+'16x16figs/jellySheet.png')

        self.demonSpriteSheet0 = objSpriteSheet(root+'dawnlike/Characters/Demon0.png')
        self.demonSpriteSheet1 = objSpriteSheet(root+'dawnlike/Characters/Demon1.png')

       
        self.s_wall = pygame.image.load(root+'16x16figs/wall.png')
        self.s_wall_dark = pygame.image.load(root+'16x16figs/wall_dark.png')
        self.s_floor = pygame.image.load(root+'16x16figs/floor.png')
        self.s_floor_dark = pygame.image.load(root+'16x16figs/floor_dark.png')

        self.a_player = self.characterSpriteSheet.getAnimation(colIdx=0, rowIdx=3, numSprites=3)        
        self.a_jelly = self.jellySpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=2)

        self.a_goggles = self.toolsSpriteSheet.getAnimation(colIdx=3, rowIdx=0, numSprites=1)        

        self.a_goggles = self.toolsSpriteSheet.getAnimation(colIdx=3, rowIdx=0, numSprites=1)        
        self.red_potion = self.potionSpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=1)        

        self.a_demon = self.demonSpriteSheet0.getAnimation(colIdx=5, rowIdx=1, numSprites=1)  
        self.a_demon.extend(self.demonSpriteSheet1.getAnimation(colIdx=5, rowIdx=1, numSprites=1))

ASSETS = structAssets()
