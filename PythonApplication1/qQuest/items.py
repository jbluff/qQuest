from qQuest import constants
from qQuest.game import GAME
from qQuest.graphics import Actor
#from qQuest.lib.monsterLib import MONSTERS 

"""Items are an Actor child which 
- don't move
- can be picked up
- may have perform some function when 'used'

useFunction : called when the item is used, passed self
numCharges : number of items item is used before..
depleteFunction : called (passed self) when charges run out.
    defaults to delete self.  Allows for e.g. turning into an empty bottle
"""


class Item(Actor):
    numItems = 0

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

        self.uniqueID = f'item{Item.numItems}'
        Item.numItems += 1

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
        self.resyncGraphicPosition()
        GAME.addMessage("item " + self.name + " dropped!")

    def use(self, target):
        if self.useFunction is None:
            return False
        else:
            success = self.useFunction(target)
            if not success:
                return False

        self.numCharges -= 1
        if self.numCharges <= 0:
            if self.depleteFunction is None:
                self.currentContainer.inventory.remove(self)
                self.deleted = True

            #self.depleteFunction(self)
            return True


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
        


class Container:
    ''' Containers represent actor attributes which can contain in game items
    e.g. player inventory is a container.  Chest items have containers.  etc.
    '''
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
    
    monster.creatureToItems()


