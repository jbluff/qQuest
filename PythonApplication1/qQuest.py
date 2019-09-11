import pygame
import tcod as libtcod
import random

import constants

class structTile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False

class structAssets:
    '''
    Container class for spriteSheets, sprites, animations
    '''
    def __init__(self):
        self.characterSpriteSheet = objSpriteSheet('dawnlike/Characters/humanoid0.png')
        self.jellySpriteSheet = objSpriteSheet('16x16figs/jellySheet.png')

        self.s_wall = pygame.image.load('16x16figs/wall.png')
        self.s_wall_dark = pygame.image.load('16x16figs/wall_dark.png')
        self.s_floor = pygame.image.load('16x16figs/floor.png')
        self.s_floor_dark = pygame.image.load('16x16figs/floor_dark.png')

        self.a_player = self.characterSpriteSheet.getAnimation(colIdx=0, rowIdx=3, numSprites=3)        
        self.a_jelly = self.jellySpriteSheet.getAnimation(colIdx=0, rowIdx=0, numSprites=2)

class objSpriteSheet:
    ''' grab images from sprite sheet'''
    def __init__(self, fileName, imageUnitX=constants.CELL_WIDTH, imageUnitY=constants.CELL_HEIGHT):
        ''' 
        imageUnitX/Y define the atomic size of an image on the sprite sheet, in pixels.
            images from the sprite sheet can be selected to take up e.g. several atomic units.
            images can also be scaled from their sprite sheet sizes
        
        '''
        self.spriteSheet = pygame.image.load(fileName).convert()
        self.imageUnitX = imageUnitX
        self.imageUnitY = imageUnitY
        
    #def getImage(self, colIdx, rowIdx, **kwargs):
    #    #TODO:  get rid of this function.
    #    return self.getAnimation(colIdx, rowIdx, 1, **kwargs)

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
    

### things that do things ###
class objActor:
    def __init__(self, x, y, name, animation, creature=None, ai=None, container=None, item=None):

        self.x, self.y = x, y
        self.name = name
        self.animation = animation
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg

        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.creature = creature
        if self.creature:
            self.creature.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

    def draw(self):
        global FOV_MAP
        isVisible = FOV_MAP.fov[self.y, self.x]
        if not isVisible:
            return

        if len(self.animation) == 1:
            SURFACE_MAIN.blit(self.animation[0], (self.x * constants.CELL_WIDTH,
                                                  self.y * constants.CELL_HEIGHT))
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

            SURFACE_MAIN.blit(self.animation[self.spriteImageNum], (self.x * constants.CELL_WIDTH,
                                                                    self.y * constants.CELL_HEIGHT))

class comCreature:
    def __init__(self, name, hp=10, deathFunction=None):

        self.name = name
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction

    def takeDamage(self, damage):
        self.hp -= damage
        GAME.addMessage(self.name + "'s health is " + str(self.hp) + "/" + str(self.maxHp))

        if self.hp <= 0:
            if self.deathFunction:
                self.deathFunction(self.owner)

    def move(self, dx, dy):
        tileIsWall = (GAME.currentMap[self.owner.x + dx]
                        [self.owner.y + dy].blockPath == True)

        target = mapCheckForCreature(self.owner.x + dx,
                                        self.owner.y + dy,
                                        exclude_object=self.owner)

        if target:
            GAME.addMessage(self.name + " attacks " + target.name)
            target.takeDamage(3)

        if not tileIsWall and target is None:
            self.owner.x += dx
            self.owner.y += dy

class comContainer:
    def __init__(self, volume=10.0, inventory=[]):
        self.max_volume = volume
        self.inventory = inventory
        #todo:   subtract volume of initialy added items

    @property
    def volume(self):
        ''' free volume '''
        #todo:  subtract stufff
        return self.max_volume 
    ## TODO: get names of things in inventory
    ## TODO: get weight?

class comItem:
    def __init__(self, weight=0.0, volume=0.0, name="itemblaggg"):
        self.weight = weight
        self.volume = volume 
        self.name = name

    def pickup(self, actor):
        if actor.container:
            if actor.container.volume + self.volume > actor.container.max_volume:
                GAME.addMessage(actor.creature.name_instance + "doesn't have enough room")
            else:
                GAME.addMessage(actor.creature.name + " picked up " + self.name)
                actor.container.inventory.append(self.owner)
                GAME.currentObjects.remove(self.owner)
                self.currentContainer = actor.container

    def drop(self, actor):
        GAME.currentObjects.append(self.owner)
        self.currentContainer.inventory.remove(self.owner)
        self.owner.x = actor.x #self.currentContainer.owner.x #why doesn't this work.  hrm. 
        self.owner.y = actor.y #self.currentContainer.owner.y
        GAME.addMessage("item " + self.name + " dropped!")

### NPC behavior things ###
class aiTest:
    def takeTurn(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        self.owner.creature.move(dx,dy)

def deathMonster(monster):
    '''
    What happens when a non-player character dies?
    Monster is actor class instance.
    '''
    GAME.addMessage(monster.creature.name + " has been slain!")
    monster.creature = None
    monster.ai = None

class objGame:
    def __init__(self):
        self.currentObjects = []
        self.messageHistory = []

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color))

### MAP FUNCTIONS ###
def mapCreate():
    newMap = [[structTile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range(0, constants.MAP_WIDTH)]

    for i in range(constants.MAP_HEIGHT):
        newMap[0][i].blockPath = True
        newMap[constants.MAP_WIDTH-1][i].blockPath = True
    for i in range(constants.MAP_WIDTH):
        newMap[i][0].blockPath = True
        newMap[i][constants.MAP_HEIGHT-1].blockPath = True

    newMap[3][3].blockPath = True
    newMap[5][6].blockPath = True

    mapMakeFov(newMap)

    return newMap

def mapCheckForCreature(x, y, exclude_object = None):
    '''
    Returns target creature instance if target location contains creature
    '''
    target = None
    for object in GAME.currentObjects:
        if (object is not exclude_object and
            object.x == x and
            object.y == y and
            object.creature):
            return object.creature
    return None

def mapMakeFov(map_in):
    ''' the index order gets hosed here.  tcod is weird.'''
    global FOV_MAP
    FOV_MAP = libtcod.map.Map(width=constants.MAP_WIDTH, height=constants.MAP_HEIGHT)
    for y in range(constants.MAP_HEIGHT):
        for x in range(constants.MAP_WIDTH):
            val = map_in[x][y].blockPath
            FOV_MAP.transparent[y][x] = not val

def mapCalculateFov():
    ''' the index order gets hosed here.  tcod is weird.'''
    global FOV_CALCULATE, FOV_MAP, PLAYER
    if FOV_CALCULATE:
        FOV_CALCULATE = False
        FOV_MAP.compute_fov(PLAYER.x,PLAYER.y,
                            radius = constants.FOV_RADIUS,
                            light_walls = constants.FOV_LIGHT_WALLS,
                            algorithm = constants.FOV_ALGO)

def mapObjectsAtCoords(x,y):
    return [obj for obj in GAME.currentObjects if obj.x == x and obj.y == y]
    

### DRAWING FUNCTIONS ###
def drawMap(map_to_draw):
    global SURFACE_MAIN, FOV_MAP
    for x in range(0, constants.MAP_WIDTH):
        for y in range(0, constants.MAP_HEIGHT):

            is_visible = FOV_MAP.fov[y, x]
            if is_visible:
                map_to_draw[x][y].explored = True
                if map_to_draw[x][y].blockPath == True: 
                    SURFACE_MAIN.blit(ASSETS.s_wall, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(ASSETS.s_floor, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
            elif map_to_draw[x][y].explored == True:
                if map_to_draw[x][y].blockPath == True: 
                    SURFACE_MAIN.blit(ASSETS.s_wall_dark, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(ASSETS.s_floor_dark, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

def drawGame():
    global SURFACE_MAIN, GAME

    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
    drawMap(GAME.currentMap)

    for gameObj in GAME.currentObjects:
        gameObj.draw()

    drawMessages()
    drawDebug()

    pygame.display.flip()

def drawFPS():
    drawText(SURFACE_MAIN, "fps: " + str(int(CLOCK.get_fps())), (0,0), constants.COLOR_WHITE, 
             bgColor=constants.COLOR_BLACK)

def drawDebug():
    drawFPS()

def drawMessages():
    height = helperTextHeight()
    numMessages = min(len(GAME.messageHistory), constants.NUM_GAME_MESSAGES)
    startY = constants.MAP_HEIGHT * constants.CELL_HEIGHT - numMessages * height
    
    if(numMessages==0):
        return 0
    messages = GAME.messageHistory[-numMessages:]
    for idx, (message, color) in enumerate(messages):
        drawText(SURFACE_MAIN,message, (0, startY+idx*height),color,constants.COLOR_BLACK)  
    
def drawText(displaySurface, text, coords, textColor, bgColor=None):
    textSurf, textRect = helperTextObjects(text, textColor, bgColor=bgColor)
    textRect.topleft = coords
    displaySurface.blit(textSurf, textRect)
 
def helperTextHeight(font=constants.FONT_DEBUG):
    fontObject = font.render('a', False, (0,0,0))
    fontRect = fontObject.get_rect()
    return fontRect.height

def helperTextObjects(text, textColor, bgColor=None):
    ''' Render text, return surface and bounding geometry '''
    textSurface = constants.FONT_DEBUG.render(text, True, textColor, bgColor)
    return textSurface, textSurface.get_rect()


### MAIN GAME FUNCTIONS ### 

def gameHandleKeys():

    global FOV_CALCULATE
    # get player input
    eventsList = pygame.event.get()

    # process input
    for event in eventsList:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN:
            # arrow key up -> move player up
            if event.key == pygame.K_UP:
                PLAYER.creature.move(0, -1)
                FOV_CALCULATE = True
                return "player-moved"

            # arrow key down -> move player down
            if event.key == pygame.K_DOWN:
                PLAYER.creature.move(0, 1)
                FOV_CALCULATE = True
                return "player-moved"

            # arrow key left -> move player left
            if event.key == pygame.K_LEFT:
                PLAYER.creature.move(-1, 0)
                FOV_CALCULATE = True
                return "player-moved"

            # arrow key right -> move player right
            if event.key == pygame.K_RIGHT:
                PLAYER.creature.move(1, 0)
                FOV_CALCULATE = True
                return "player-moved"

            # pickup objects
            # TODO:  break this into a subroutine
            if event.key == pygame.K_g:
                objs = mapObjectsAtCoords(PLAYER.x, PLAYER.y)
                for obj in objs:
                    if obj.item:
                        obj.item.pickup(PLAYER)

            if event.key == pygame.K_d:
                if len(PLAYER.container.inventory) > 0:
                    PLAYER.container.inventory[-1].item.drop(PLAYER)
                        
    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():
    global GAME, CLOCK
    quit = False
    
    GAME.addMessage("oh heyy", constants.COLOR_WHITE)
    playerAction = "no-action"

    while playerAction != "QUIT":
       
        playerAction = gameHandleKeys()

        mapCalculateFov()

        if playerAction == "player-moved":
            for gameObj in GAME.currentObjects:
                if gameObj.ai:
                    gameObj.ai.takeTurn()

        drawGame()

        CLOCK.tick(60)

    gameExit()

def gameInitialize():
    global CLOCK, SURFACE_MAIN, GAME, FOV_CALCULATE, ASSETS, PLAYER

    pygame.init()
    CLOCK = pygame.time.Clock()

    SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH*constants.CELL_WIDTH,
                                            constants.MAP_HEIGHT*constants.CELL_HEIGHT))

    GAME = objGame()
    GAME.currentMap = mapCreate()
    FOV_CALCULATE = True
    
    ASSETS = structAssets()

    # init hero
    container1 = comContainer()
    creatureCom1 = comCreature("jenny")
    PLAYER = objActor(1,1, "hero", ASSETS.a_player, 
                      creature=creatureCom1, 
                      container=container1)
    GAME.currentObjects.append(PLAYER)

    # init the enemy
    item1 = comItem(name="franks's corpse")
    creatureCom2 = comCreature("frank", deathFunction=deathMonster)
    aiCom = aiTest()
    enemy = objActor(5, 7, "evil jelly", ASSETS.a_jelly, 
                     creature=creatureCom2, 
                     ai=aiCom,
                     container=container1,
                     item=item1)
    GAME.currentObjects.append(enemy)

    


if __name__ == "__main__":
    gameInitialize()
    gameMainLoop()

    


