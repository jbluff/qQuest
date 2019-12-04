import itertools

import numpy as np
# import tcod as libtcod

from qQuest import constants
from qQuest.game import GAME, SURFACE_MAIN, CLOCK
from qQuest.graphics import Actor



'''Creatures are Actor children which represent actors that can move, fight, die
'''
class Creature(Actor):
    def __init__(self, *args, hp=10, deathFunction=None, ai=None, container=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction
        self.creature = True
 
        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self

    def move(self, dx, dy):
        tileIsBlocking = GAME.currentLevel.map[self.y + dy][self.x + dx].blocking 
        target = GAME.currentLevel.checkForCreature(self.x + dx, self.y + dy, exclude_object=self)

        if target:
            GAME.addMessage(self.name + " attacks " + target.name)
            target.takeDamage(3)

        elif not tileIsBlocking:
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
    As an Actor instance, it has reference to a level and a position.
    For each level it's been to, it keeps a history of what it has previously seen (for fog of war/fov)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doRecaculateFov = True
        self.explorationHistory = {}
                
    def recalculateFov(self, force=False):
        if not self.doRecaculateFov and not force:
            return None

        self.fov = self.level.computeFov(self.x, self.y)        
        self.doRecaculateFov = False

    def getTileIsVisible(self, x, y):
        return self.fov[y][x]

    def initLevelExplorationHistory(self):
        levelID = self.level.uniqueID
        if levelID not in self.explorationHistory.keys(): #first time visiting a level
            self.explorationHistory[levelID] = np.zeros_like(self.level.map, dtype=np.bool).tolist()

    def setTileIsExplored(self, x, y):
        levelID = self.level.uniqueID
        self.explorationHistory[levelID][y][x] = True
    
    def getTileIsExplored(self, x, y):
        levelID = self.level.uniqueID
        return self.explorationHistory[levelID][y][x]





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
        #self.item = True
        #self.currentContainer = None

        self.deleted = False
        
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