import pygame
import tcod as libtcod


from qQuest import constants, qqGlobal, graphics, map_util, menus, ai, creatures

from qQuest.qqGlobal import SURFACE_MAIN, CLOCK, GAME

from qQuest.graphics import ASSETS


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
            qqGlobal.SURFACE_MAIN.blit(self.animation[0], (self.x * constants.CELL_WIDTH,
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

            qqGlobal.SURFACE_MAIN.blit(self.animation[self.spriteImageNum], (self.x * constants.CELL_WIDTH,
                                                                    self.y * constants.CELL_HEIGHT))


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

    def drop(self):
        actor = self.currentContainer.owner
        GAME.currentObjects.append(self.owner) #clunky AF
        self.currentContainer.inventory.remove(self.owner)
        self.owner.x = actor.x  
        self.owner.y = actor.y 
        GAME.addMessage("item " + self.name + " dropped!")

    def use(self):
        pass


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
                objs = GAME.objectsAtCoords(PLAYER.x, PLAYER.y)
                for obj in objs:
                    if obj.item:
                        obj.item.pickup(PLAYER)

            # pause menu
            if event.key == pygame.K_p:
                menus.pause(GAME)

            # inventory menu
            if event.key == pygame.K_i:
                menus.inventory(SURFACE_MAIN, PLAYER)

            if event.key == pygame.K_q:
                return "QUIT"
    return "no-action"

def gameExit():
    pygame.quit()
    quit()

def gameMainLoop():
    global GAME, FOV_CALCULATE, FOV_MAP

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

        graphics.drawGame(GAME, FOV_MAP)

        CLOCK.tick(constants.GAME_FPS)

    gameExit()

#temporary and bad
def gameAddEnemy(coordX, coordY, name):
    inventory = comContainer()
    item = comItem(name=name+"'s corpse")
    creature = creatures.Creature(name, deathFunction=lambda x: creatures.deathMonster(GAME, x))
    enemy = objActor(coordX, coordY, "evil jelly", ASSETS.a_jelly,
                     creature=creature, ai=ai.aiTest(), container=inventory, item=item)
    GAME.currentObjects.append(enemy)

def gameAddItem(coordX, coordY, name):
    item = comItem(name="goggles")
    googles = objActor(coordX, coordY, "error", ASSETS.googles, GAME, 
                       item=item)
    GAME.currentObjects.append(googles)


def gameInitialize():
    global  FOV_CALCULATE, FOV_MAP, PLAYER #GAME,

    pygame.init()
    pygame.key.set_repeat(200, 200) # Makes holding down keys work.  

    

    #graphics.initAssets()

    #GAME = objGame()
    GAME.currentMap, FOV_MAP = map_util.mapCreate()
    FOV_CALCULATE = True
    
    # init hero
    container1 = comContainer()
    creatureCom1 = creatures.Creature("jenny")
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

    


