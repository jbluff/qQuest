'''Items are an Actor child which 
- don't move
- can be picked up
- may have perform some function when 'used'

'''

from qQuest import constants
from qQuest.game import GAME
from qQuest.graphics import Actor



class Item(Actor):
    numItems = 0

    def __init__(self, *args, volume=1.0, 
                 useFunction=None, numCharges=1, depleteFunction=None, **kwargs):
        '''Items are an Actor child which don't move, can be picked up, may 
        perform some function when 'used', ...'''

        super().__init__(*args, **kwargs)
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

    def __str__(self):
        return f'Item: {self.uniqueName:<0},  uID: {self.uniqueID:<30}'
        
    def pickup(self, actor):
        if actor.container:
            if actor.container.volume_used + self.volume > actor.container.max_volume:
                
                GAME.addMessage(actor.name + " doesn't have enough room")
            else:
                GAME.addMessage(actor.name + " picked up " + self.name)
                actor.container.inventory.append(self)
                GAME.currentLevel.removeObject(self)
                # GAME.currentLevel.objects.remove(self)
                self.currentContainer = actor.container

    def drop(self):
        actor = self.currentContainer.owner
        GAME.currentLevel.addObject(self) #clunky AF
        # GAME.currentLevel.objects.append(self) #clunky AF
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

    @property
    def invString(self) -> str:
        ''' inventory representation. '''
        return self.uniqueName

class Equipment(Item):

    def __init__(self, *args, slot=None, strengthBonus=0, 
                 defenseBonus=0, dexterityBonus=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.slot = slot
        self.strengthBonus = strengthBonus
        self.defenseBonus = defenseBonus
        self.dexterityBonus = dexterityBonus
        self.equipped = False
        self.equipment = True


    def toggleEquip(self) -> None:
        if self.equipped:
            self.unequip()
        else:
            self.equip()

    def unequip(self) -> None:
        #slot stuff
        self.equipped = False
        GAME.addMessage(f'{self.name} unequipped')
        
    def equip(self) -> None:
        #self.canBeEquipped(owner)
        #self.owner.unequipElseInSlot(self)
        #slot stuff
        self.equipped = True
        GAME.addMessage(f'{self.name} equipped')
        
    @property
    def invString(self) -> str:
        ''' inventory representation. '''
        if not self.equipped:
            return f'o  {self.uniqueName}'
        else:
            return f'x  {self.uniqueName}'


class Container:
    ''' Containers represent actor attributes which can contain in game items
    e.g. player inventory is a container.  Chest items have containers.  etc.
    '''
    def __init__(self, volume=10.0, inventory=[], **kwargs):
        self.max_volume = volume
        self.inventory = inventory

    def __getitem__(self, val):
        return self.inventory[val]
        # should Container just inherit list?  maybe.

    def __str__(self):
        repStr= f'Container (owned by {self.owner.uniqueName}):, '
        for item in self.inventory:
            repStr+= f'{str(item)}, '
        return repStr

    @property
    def volume_used(self) -> float:
        #todo:  subtract stufff
        return sum([item.volume for item in self.inventory])
    ## TODO: get names of things in inventory
    ## TODO: get weight?

    def statBonus(self, bonusName:str) -> float:
        bonus = 0
        for item in self:
            if getattr(item, 'equipped', False):
                bonus += getattr(item, bonusName, 0)
        return bonus
            
def deathMonster(monster):
    '''
    What happens when a non-player character dies?
    Monster is actor class instance.
    '''
    GAME.addMessage(monster.name + " has been slain!")
    
    monster.creatureToItems()


