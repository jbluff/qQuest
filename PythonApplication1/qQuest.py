
import pygame
import tcod as libtcod
import random

import constants

### STRUCTS ###
class structTile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False

class objActor:
    def __init__(self, x, y, name, sprite, creature=None, ai=None):

        self.x, self.y = x, y
        self.name = name
        self.sprite = sprite
 
        self.creature = creature
        if self.creature:
            self.creature.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

    def draw(self):
        global FOV_MAP
        is_visible = FOV_MAP.fov[self.y, self.x]
        if (is_visible):
            SURFACE_MAIN.blit(self.sprite, (self.x * constants.CELL_WIDTH,
                                                 self.y * constants.CELL_HEIGHT))

class comCreature:
    def __init__(self, name, hp=10, deathFunction=None):

        self.name = name
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction

    def takeDamage(self, damage):
        self.hp -= damage
        print(self.name + "'s health is " + str(self.hp) + "/" + str(self.maxHp))

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
            print(self.name + " attacks " + target.name)
            target.takeDamage(3)

        if not tileIsWall and target is None:
            self.owner.x += dx
            self.owner.y += dy

class aiTest:
    #def __init__(self):
    #    pass

    def takeTurn(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        self.owner.creature.move(dx,dy)

def deathMonster(monster):
    '''
    Monster is actor class instance
    '''
    print(monster.creature.name + " has been slain!")
    monster.creature = None
    monster.ai = None

class objGame:
    def __init__(self):
        self.correntObjects = []
        self.message_history = []
        self.currentMap = mapCreate()

### MAP FUNCTIONS ###
def mapCreate():
    new_map = [[structTile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range(0, constants.MAP_WIDTH)]

    for i in range(constants.MAP_HEIGHT):
        new_map[0][i].blockPath = True
        new_map[constants.MAP_WIDTH-1][i].blockPath = True
    for i in range(constants.MAP_WIDTH):
        new_map[i][0].blockPath = True
        new_map[i][constants.MAP_HEIGHT-1].blockPath = True

    new_map[3][3].blockPath = True
    new_map[5][6].blockPath = True

    map_make_fov(new_map)

    return new_map

def mapCheckForCreature(x, y, exclude_object = None):
    '''
    Returns target creature instance if target location contains creature
    '''
    global GAME
    target = None
    for object in GAME.correntObjects:
        if (object is not exclude_object and
            object.x == x and
            object.y == y and
            object.creature):
            return object.creature
    return None

def map_make_fov(map_in):
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

### DRAWING FUNCTIONS ###
def drawMap(map_to_draw):
    global SURFACE_MAIN, FOV_MAP
    for x in range(0, constants.MAP_WIDTH):
        for y in range(0, constants.MAP_HEIGHT):

            is_visible = FOV_MAP.fov[y, x]
            if is_visible:
                map_to_draw[x][y].explored = True
                if map_to_draw[x][y].blockPath == True: 
                    SURFACE_MAIN.blit(constants.S_WALL, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(constants.S_FLOOR, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
            elif map_to_draw[x][y].explored == True:
                if map_to_draw[x][y].blockPath == True: 
                    SURFACE_MAIN.blit(constants.S_WALL_DARK, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(constants.S_FLOOR_DARK, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

def drawGame():
    global SURFACE_MAIN, GAME

    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
    drawMap(GAME.currentMap)

    for gameObj in GAME.correntObjects:
        gameObj.draw()

    drawDebug()

    pygame.display.flip()

def drawDebug():
    drawText(SURFACE_MAIN, "fps: " + str(int(CLOCK.get_fps())), (0,0), constants.COLOR_BLACK)

    #drawText(SURFACE_MAIN, "fps:", (0,0), constants.COLOR_BLACK)
    
def drawText(displaySurface, text, coords, textColor):
    textSurf, textRect = helperTextObjects(text, textColor)
    textRect.topleft = coords
    displaySurface.blit(textSurf, textRect)
 

def helperTextObjects(text, textColor):
    ''' Render text, return surface and bounding geometry '''
    background=None
    textSurface = constants.FONT_DEBUG.render(text, True, textColor, background)
    return textSurface, textSurface.get_rect()

### MAIN GAME FUNCTIONS ### 
def gameHandleKeys():

    global FOV_CALCULATE, PLAYER
    # get player input
    keys_list = pygame.key.get_pressed()
    events_list = pygame.event.get()

    # process input
    for event in events_list:
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

    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():
    global GAME, CLOCK
    quit = False
    
    playerAction = "no-action"

    while not quit:
       
        playerAction = gameHandleKeys()

        mapCalculateFov()

        if playerAction == "QUIT":
            quit = True

        elif playerAction == "player-moved":
            for gameObj in GAME.correntObjects:
                if gameObj.ai:
                    gameObj.ai.takeTurn()

        drawGame()

        CLOCK.tick(60)

    gameExit()

def gameInitialize():
    global CLOCK, SURFACE_MAIN, GAME, PLAYER, FOV_CALCULATE
    pygame.init()

    CLOCK = pygame.time.Clock()

    SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH*constants.CELL_WIDTH,
                                            constants.MAP_HEIGHT*constants.CELL_HEIGHT))

    GAME = objGame()
    GAME.currentMap = mapCreate()
    FOV_CALCULATE = True
    
    creature_com1 = comCreature("our_hero")
    PLAYER = objActor(2, 2, "python", constants.S_PLAYER, creature = creature_com1)
    GAME.correntObjects.append(PLAYER)

    creature_com2 = comCreature("evil_jelly", deathFunction=deathMonster)
    ai_com = aiTest()
    enemy = objActor(5, 6, "crab", constants.S_ENEMY, creature = creature_com2, ai=ai_com)
    GAME.correntObjects.append(enemy)

''' WHERE THE MAGIC HAPPENS ''' 
if __name__ == "__main__":
    gameInitialize()
    gameMainLoop()

    


