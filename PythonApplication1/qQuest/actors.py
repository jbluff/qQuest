from qQuest import constants
from qQuest.qqGlobal import GAME, SURFACE_MAIN, CLOCK

'''
All drawn things which are not floor ties.  May reflect player, NPCs, items
'''
class Actor:
    def __init__(self, x, y, name, animation, fovMap=None, creature=None, ai=None, container=None, item=None):

        self.x, self.y = x, y
        self.name = name
        self.animation = animation
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg

        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.fovMap = fovMap
        self.fovCalculate = False

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

    def draw(self, fovMap):
        
        '''
        This generality sets up some flexibility, e.g. if we want to see from an
        NPCs point of view, later
        '''

        isVisible = fovMap.fov[self.y, self.x]
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


'''
Creatures are actor attributes which represent actors that can move, fight, die
'''
class Creature:
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

        if not (self.owner.fovMap is None):
            self.owner.fovCalculate = True

'''
Items are an actor attribute.
useFunction : called when the item is used, passed self
numCharges : number of items item is used before..
depleteFunction : called (passed self) when charges run out.
    defaults to delete self.  Allows for e.g. turning into an empty bottle
'''
class Item:
    def __init__(self, weight=0.0, volume=0.0, name="defaultItemName", 
                 useFunction=None, numCharges=1, depleteFunction=None):
        self.weight = weight
        self.volume = volume 
        self.name = name
        self.useFunction = useFunction
        self.numCharges = numCharges
        self.maxNumCharges = numCharges
        
        #if depleteFunction is None:
        #    depleteFunction = lambda x: self.__del__
        self.depleteFunction = depleteFunction

    #def __del__(self):
    #    del self.owner.container
    #    del self
        
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

    def use(self, target):
        if self.useFunction is None:
            return

        print('using')
        self.useFunction(target)
        self.numCharges -= 1
        if self.numCharges <= 0:
            print("depleting")
            if self.depleteFunction is None:
                self.currentContainer.inventory.remove(self.owner)
            #self.depleteFunction(self)


'''
Containers represent actor attributes which can contain in game items
e.g. player inventory is a container.  Chest items have containers.  etc.
'''
class Container:
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

            
def deathMonster(game, monster):
    '''
    What happens when a non-player character dies?
    Monster is actor class instance.
    '''
    game.addMessage(monster.creature.name + " has been slain!")
    monster.creature = None
    monster.ai = None
