from qQuest import constants
from qQuest.qqGlobal import GAME, SURFACE_MAIN, CLOCK

'''
All drawn things which are not floor ties.  May reflect player, NPCs, items
'''
class Actor:
    def __init__(self, pos, name, animation, fovMap=None, ai=None, container=None, item=None, **kwargs):
        #fovMap shouldn't be here.

        self.x, self.y = pos
        self.name = name
        self.animation = animation
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg

        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.fovMap = fovMap
        self.fovCalculate = False

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self


        self.creature = None #overwritten by Creature.__init__
        self.item = None #overwritten by Item.__init__

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
class Creature(Actor):
    def __init__(self, *args, hp=10, deathFunction=None, **kwargs):
        print(args)
        super().__init__(*args, **kwargs)
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction
        self.creature = True

    def takeDamage(self, damage):
        self.hp -= damage
        GAME.addMessage(self.name + "'s health is " + str(self.hp) + "/" + str(self.maxHp))

        if self.hp <= 0:
            if self.deathFunction:
                self.deathFunction(self)

    def heal(self, deltaHp):
        #TODO!
        assert deltaHp >= 0
        pass

    def move(self, dx, dy):
        tileIsWall = (GAME.currentMap[self.x + dx]
                        [self.y + dy].blockPath == True)

        target = GAME.checkForCreature(self.x + dx, self.y + dy, exclude_object=self)
        if target:
            GAME.addMessage(self.name + " attacks " + target.name)
            target.takeDamage(3)

        if not tileIsWall and target is None:
            self.x += dx
            self.y += dy

        if not (self.fovMap is None):
            self.fovCalculate = True


'''
Items are an actor attribute.
useFunction : called when the item is used, passed self
numCharges : number of items item is used before..
depleteFunction : called (passed self) when charges run out.
    defaults to delete self.  Allows for e.g. turning into an empty bottle
'''
class Item(Actor):
    def __init__(self, *args, weight=0.0, volume=0.0, 
                 useFunction=None, numCharges=1, depleteFunction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.weight = weight
        self.volume = volume 
        self.useFunction = useFunction
        self.numCharges = numCharges
        self.maxNumCharges = numCharges
        
        #if depleteFunction is None:
        #    depleteFunction = lambda x: self.__del__
        self.depleteFunction = depleteFunction
        self.item = True

    #def __del__(self):
    #    del self.owner.container
    #    del self
        
    def pickup(self, actor):
        if actor.container:
            if actor.container.volume + self.volume > actor.container.max_volume:
                GAME.addMessage(actor.name + "doesn't have enough room")
            else:
                GAME.addMessage(actor.name + " picked up " + self.name)
                actor.container.inventory.append(self)
                GAME.currentObjects.remove(self)
                self.currentContainer = actor.container

    def drop(self):
        actor = self.currentContainer.owner
        GAME.currentObjects.append(self) #clunky AF
        self.currentContainer.inventory.remove(self)
        self.x = actor.x  
        self.y = actor.y 
        GAME.addMessage("item " + self.name + " dropped!")

    def use(self, target):
        if self.useFunction is None:
            return

        success = self.useFunction(target)
        if not success:
            return 

        self.numCharges -= 1
        if self.numCharges <= 0:
            if self.depleteFunction is None:
                self.currentContainer.inventory.remove(self.owner)
            #self.depleteFunction(self)

# let's be serious, this should use inheritance.
class Equipment:

    def __init__(self, slot, attackBonus=0, defenseBonus=0):
        self.slot = slot
        self.attackBonus = attackBonus
        self.defenseBonus = defenseBonus
        self.equipped = False

    def toggleEquip(self):
        if self.eqipped:
            self.unequip()
        else:
            self.eqipp()

    def unequip(self):
        GAME.addMessage("item unequipped")
        
    def equip(self):
        GAME.addMessage("item equipped")
        

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

            
def deathMonster(monster):
    '''
    What happens when a non-player character dies?
    Monster is actor class instance.
    '''
    GAME.addMessage(monster.name + " has been slain!")
    
    creatureToItems(monster)


'''
Destroys a creature, turns it into a corpse and drops its inventory items.
> inventory item feature unadded
> also want the ability to change the graphic
> also kwargs can have e.g. weight, useFunction
'''
def creatureToItems(creature, **kwargs):

    itemList = []

    inventory = creature.container.inventory
    if inventory:
        itemList.extend(inventory)

    corpse = Item((creature.x, creature.y),
                  creature.name+"'s corpse",
                  [creature.animation[0],],
                  **kwargs)
    
    itemList.append(corpse)

    for el in itemList:
        GAME.currentObjects.append(el)

    GAME.currentObjects.remove(creature)
