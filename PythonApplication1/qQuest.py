import pygame
import tcod as libtcod
import random

import graphics
import constants
import map_util





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

        target = GAME.checkForCreature(self.owner.x + dx, self.owner.y + dy, exclude_object=self.owner)

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


### MENU FUNCTIONS ###
def menuPause():
    ''' dummy function, sort of dumb '''
    GAME.addMessage("paused!")

    menuText = "paused"
    #TODO:  font flexibility
    windowWidth = constants.CELL_WIDTH*constants.MAP_WIDTH
    windowHeight = constants.CELL_HEIGHT*constants.MAP_HEIGHT

    textWidth, textHeight = helperTextDims(text="menuText") # font=

    coordY = (windowHeight-textHeight)/2
    coordX = (windowWidth-textWidth)/2

    breakMenuLoop = False
    while not breakMenuLoop:
        eventsList = pygame.event.get()
        for event in eventsList:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    breakMenuLoop = 1

        drawText(SURFACE_MAIN, menuText, (coordX, coordY), constants.COLOR_WHITE, bgColor=constants.COLOR_BLACK)
        CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()

def updateSelected(invList, selectedIdx):
    #TODO:  bgColor
    numItems = len(invList)-1
    for idx in range(1,numItems+1):
        if idx == selectedIdx+1:
            invList[idx][1] = constants.COLOR_RED
        else:
            invList[idx][1] = constants.COLOR_GREY
    return invList

def menuInventory():
    owner = PLAYER #alternately, pass an an inventory..
    parentSurface = SURFACE_MAIN
    menuWidth = 200
    menuHeight = 300
    #Font..

    windowWidth = parentSurface.get_width()
    windowHeight = parentSurface.get_height()

    coordY = (windowHeight-menuHeight)/2
    coordX = (windowWidth-menuWidth)/2

    inventorySurface = pygame.Surface((menuWidth, menuHeight))

    #TODO:  bgColor
    invList = [["Inventory:", constants.COLOR_WHITE],]
    invList.extend([[obj.item.name,constants.COLOR_GREY] for obj in owner.container.inventory])
    selected = 0
    invList = updateSelected(invList, selected)

    breakMenuLoop = False
    while not breakMenuLoop:
        # Clear
        inventorySurface.fill(constants.COLOR_BLACK)

        # Register changes
        eventsList = pygame.event.get()
        for event in eventsList:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_q:
                    breakMenuLoop = True
                    break

                elif event.key == pygame.K_DOWN:
                    if selected < len(invList) - 2:
                        selected += 1

                elif event.key == pygame.K_UP:
                    if selected > 0:
                        selected -= 1
                   
                elif event.key == pygame.K_d:
                    owner.container.inventory[selected].item.drop(PLAYER) #fix this nonsense.
                    del invList[selected+1]
                    if selected > 0:
                        selected -= 1

                invList = updateSelected(invList, selected)
                
        # Draw
        graphics.drawTextList(inventorySurface, invList)

        # Display
        parentSurface.blit(inventorySurface, (coordX, coordY))
        CLOCK.tick(constants.GAME_FPS)
        pygame.display.flip()
        


### MAIN GAME FUNCTIONS ### 

class objGame:
    def __init__(self):
        self.currentObjects = []
        self.messageHistory = []

    def addMessage(self, messageText, color=constants.COLOR_WHITE):
        self.messageHistory.append((messageText, color))

    def checkForCreature(self, x, y, exclude_object = None):
        '''
        Returns target creature instance if target location contains creature
        '''
        target = None
        for object in self.currentObjects:
            if (object is not exclude_object and
                object.x == x and
                object.y == y and
                object.creature):
                return object.creature
        return None

    def objectsAtCoords(self,x,y):
        return [obj for obj in self.currentObjects if obj.x == x and obj.y == y]

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
                objs = GAME.objectsAtCoords(PLAYER.x, PLAYER.y)
                for obj in objs:
                    if obj.item:
                        obj.item.pickup(PLAYER)

            # pause menu
            if event.key == pygame.K_p:
                menuPause()

            # inventory menu
            if event.key == pygame.K_i:
                menuInventory()

            if event.key == pygame.K_q:
                return "QUIT"
    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():
    global GAME, CLOCK, FOV_CALCULATE, FOV_MAP
    quit = False
    
    GAME.addMessage("oh heyy", constants.COLOR_WHITE)
    playerAction = "no-action"

    while playerAction != "QUIT":
       
        playerAction = gameHandleKeys()

        map_util.mapCalculateFov(doCalculate=FOV_CALCULATE, player=PLAYER, fovMap=FOV_MAP)
        FOV_CALCULATE = False

        if playerAction == "player-moved":
            for gameObj in GAME.currentObjects:
                if gameObj.ai:
                    gameObj.ai.takeTurn()

        graphics.drawGame(GAME, SURFACE_MAIN, FOV_MAP, clock=CLOCK)

        CLOCK.tick(constants.GAME_FPS)

    gameExit()

#temporary and bad
def gameAddEnemy(coordX, coordY, name):
    inventory = comContainer()
    item = comItem(name=name+"'s corpse")
    creature = comCreature(name, deathFunction=deathMonster)
    ai = aiTest()
    enemy = objActor(coordX, coordY, "evil jelly", ASSETS.a_jelly, 
                     creature=creature, ai=ai, container=inventory, item=item)
    GAME.currentObjects.append(enemy)

def gameInitialize():
    global CLOCK, SURFACE_MAIN, GAME, FOV_CALCULATE, FOV_MAP, ASSETS, PLAYER

    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  
    CLOCK = pygame.time.Clock()

    SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH*constants.CELL_WIDTH,
                                            constants.MAP_HEIGHT*constants.CELL_HEIGHT))

    ASSETS = graphics.initAssets()

    GAME = objGame()
    GAME.currentMap, FOV_MAP = map_util.mapCreate()
    FOV_CALCULATE = True
    
    

    # init hero
    container1 = comContainer()
    creatureCom1 = comCreature("jenny")
    PLAYER = objActor(1,1, "hero", ASSETS.a_player, 
                      creature=creatureCom1, 
                      container=container1)
    GAME.currentObjects.append(PLAYER)

    # init the enemy
    gameAddEnemy(5,7,"frank")

    gameAddEnemy(10,3,"george")




if __name__ == "__main__":
    gameInitialize()
    gameMainLoop()

    


