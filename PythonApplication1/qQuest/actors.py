import itertools

import numpy as np
# import tcod as libtcod

from qQuest import constants
from qQuest.game import GAME, SURFACE_MAIN, CLOCK
from qQuest.graphics import ASSETS

'''
All drawn things which are not floor ties.  May reflect player, NPCs, items
'''

class Actor():
    def __init__(self, pos, name, animationName, ai=None, container=None, item=None, level=None, **kwargs):

        self.x, self.y = pos
        self.name = name
        self.animationName = animationName
        self.animationSpeed = 0.5 # in seconds  -- TODO:  make kwarg

        self.flickerSpeed = self.animationSpeed / len(self.animation)
        self.flickerTimer = 0
        self.spriteImageNum = 0

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self

        #self.creature = None #overwritten by Creature.__init__
        #self.item = None #overwritten by Item.__init__
        self.deleted = False
        self.level = level

    @property
    def animation(self):
        return getattr(ASSETS,self.animationName)

    def draw(self):#, fov):#visibilityMap):
        '''
        This generality sets up some flexibility, e.g. if we want to see from an
        NPCs point of view, later.
        '''

        #isVisible = visibilityMap.fov[self.y, self.x]
        isVisible = GAME.viewer.fov[self.y][self.x]

        if not isVisible:
            return 

        if len(self.animation) == 1:
            currentSprite = self.animation[0]
 
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
            currentSprite = self.animation[self.spriteImageNum]

        shapeTuple = (self.x * constants.CELL_WIDTH, self.y * constants.CELL_HEIGHT)
        SURFACE_MAIN.blit(currentSprite, shapeTuple)

'''
Creatures are actor attributes which represent actors that can move, fight, die
'''
class Creature(Actor):
    def __init__(self, *args, hp=10, deathFunction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction
        self.creature = True

    def move(self, dx, dy):
        tileIsWall = GAME.currentLevel.map[self.y + dy][self.x + dx].blockPath 
        target = GAME.currentLevel.checkForCreature(self.x + dx, self.y + dy, exclude_object=self)

        if target:
            GAME.addMessage(self.name + " attacks " + target.name)
            target.takeDamage(3)

        elif not tileIsWall:
            self.x += dx
            self.y += dy

    def pickupObjects(self):
        objs = GAME.currentLevel.objectsAtCoords(self.x, self.y)
        [obj.pickup(self) for obj in objs if isinstance(obj, (Item,))]

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

    def isOnPortal(self):
        for portal in self.level.portals:
            if self.x == portal.x and self.y == portal.y:
                return portal
        return None
  
class Viewer(Actor):
    """
    As an Actor instance, it has reference to a level and a position
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doRecaculateFov = True
        
    # def initializeVisibilityMap(self, mapIn):
    #     mapHeight, mapWidth = np.array(mapIn).shape

    #     self.visibilityMap = libtcod.map.Map(width=mapWidth, height=mapHeight)
    #     for (y, x) in itertools.product(range(mapHeight), range(mapWidth)):
    #         self.visibilityMap.transparent[y][x] = not mapIn[y][x].blockPath
    #     self.recalculateFov(force=True)
                
    def recalculateFov(self, force=False):
        if not self.doRecaculateFov and not force:
            return None

        # self.visibilityMap.compute_fov(self.x,self.y,
        #     radius = constants.FOV_RADIUS,
        #     light_walls = constants.FOV_LIGHT_WALLS,
        #     algorithm = constants.FOV_ALGO)

        self.fov = self.level.computeFov(self.x, self.y)
        
        self.doRecaculateFov = False


class PlayerClass(Creature, Viewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def move(self, dx, dy):
        super().move(dx, dy)
        self.doRecaculateFov = True

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
        #self.currentContainer = None
        
    def pickup(self, actor):
        if actor.container:
            if actor.container.volume + self.volume > actor.container.max_volume:
                GAME.addMessage(actor.name + "doesn't have enough room")
            else:
                GAME.addMessage(actor.name + " picked up " + self.name)
                actor.container.inventory.append(self)
                GAME.currentLevel.objects.remove(self)
                self.currentContainer = actor.container

    def drop(self):
        actor = self.currentContainer.owner
        GAME.currentLevel.objects.append(self) #clunky AF
        self.currentContainer.inventory.remove(self)
        #self.currentContainer = None
        self.x = actor.x  
        self.y = actor.y 
        GAME.addMessage("item " + self.name + " dropped!")

    def use(self, target):
        print("use was called")
        print(self.useFunction)
        if self.useFunction is None:
            return
        print("found useFunction")
        success = self.useFunction(target)
        if not success:
            return 

        self.numCharges -= 1
        if self.numCharges <= 0:
            if self.depleteFunction is None:
                self.currentContainer.inventory.remove(self)
                self.deleted = True
            #self.depleteFunction(self)

# let's be serious, this should use inheritance.
class Equipment(Item):

    def __init__(self, *args, slot=None, attackBonus=0, 
                 defenseBonus=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.slot = slot
        self.attackBonus = attackBonus
        self.defenseBonus = defenseBonus
        self.equipped = False
        self.equipment = True

    def toggleEquip(self):
        if self.eqipped:
            self.unequip()
        else:
            self.eqipp()

    def unequip(self):
        #slot stuff
        GAME.addMessage("item unequipped")
        
    def equip(self):
        #slot stuff
        GAME.addMessage("item equipped")
        

'''
Containers represent actor attributes which can contain in game items
e.g. player inventory is a container.  Chest items have containers.  etc.
'''
class Container:
    def __init__(self, volume=10.0, inventory=[], **kwargs):
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

    #inventory = creature.container.inventory
    #if inventory:
    #    itemList.extend(inventory)

    corpse = Item((creature.x, creature.y),
                  creature.name+"'s corpse",
                  creature.animationName+"_dead",
                  #[creature.animation[0],],  #this is kinda broke.  
                  **kwargs)
    
    itemList.append(corpse)

    for el in itemList:
        GAME.currentLevel.objects.append(el)

    GAME.currentLevel.objects.remove(creature)

#  pos, name, animationName, 
#
class Portal(Actor):
    numPortals = 0

    def __init__(self, *args, destinationPortal=None, **kwargs):
        
        self.uniqueID = Portal.numPortals
        Portal.numPortals += 1

        super().__init__(*args, **kwargs)
        self.destinationPortal = destinationPortal
         
    def pickup(self, actor):
        return