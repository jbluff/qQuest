import itertools
import collections
import math

import numpy as np

from qQuest import constants, actions
from qQuest.game import GAME
from qQuest.graphics import Actor
from qQuest.items import Item
from qQuest.lib.monsterLib import MONSTERS




class Creature(Actor):
    ''' Creatures are Actor children can move about and, well, do things.
    The handle actions in a queue (implemented as deque), which can 
    take varying amounts of time, but are ticked through once per game update.
    For Creatures with an ai property, the ai is consulted when the queue is 
    empty.
    '''
    def __init__(self, *args,  ai=None, 
                              container=None, speed=0.07, **kwargs):
        super().__init__(*args, **kwargs)
        self.dead = False

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self

        self.actionQueue = collections.deque()
        self.ticksPerMove = 1/speed

        self.activeEmote = None

    def resolveQueueTick(self) -> None:
        ''' Resolve the next entry in the Creature's action queue. Note it reads
        from the right (.pop()), so new queue entries should be added with
        .appendleft()
        '''
        if len(self.actionQueue) == 0:
            if self.ai is not None:
                self.scheduleAI()
            return 

        queueEntry = self.actionQueue.pop()
        self.activeEmote = queueEntry.emoteName
        success = queueEntry.execute()

        if not success:
            return #if it didn't work, don't continue
        if not queueEntry.completed:
            self.actionQueue.append(queueEntry)

    def scheduleMove(self, dx: int, dy: int, **kwargs) -> None:
        ''' Attempt to queue up a tile -> tile movement.
        dx, dy are differential position.  In units of tiles.'''
        MAX_QUEUED_MOVES = 2
        if self.movesInQueue >= MAX_QUEUED_MOVES:
            return 
        if dx==0 and dy==0:
            return

        duration = int(math.ceil(self.ticksPerMove * np.sqrt(dx**2+dy**2)))
        queueEntry = actions.QueuedMove(self, duration, dx, dy, **kwargs)
        self.actionQueue.appendleft(queueEntry)

    @property
    def movesInQueue(self) -> int:
        ''' How many moves have been scheduled?  Helpful for smooth movement. '''
        return sum([isinstance(entry, actions.QueuedMove) for entry in self.actionQueue])

    def scheduleAI(self, **kwargs) -> None:
        queueEntry = actions.QueuedAI(self, self.ai.thinkingDuration, **kwargs)
        self.actionQueue.appendleft(queueEntry)

    def scheduleWait(self, duration=5, **kwargs) -> None:
        queueEntry = actions.QueuedWait(self, duration, **kwargs)
        self.actionQueue.appendleft(queueEntry)

    def pickupObjects(self) -> None:
        ''' Creature picks up all objects at current coords '''
        objs = self.level.objectsAtCoords(self.x, self.y)
        [obj.pickup(self) for obj in objs if isinstance(obj, (Item,))]

    def isOnPortal(self): # -> Portal:
        ''' if Creatre standing on a portal, returns that Portal.  
        Otherwise returns None. '''
        for portal in self.level.portals:
            if self.x == portal.x and self.y == portal.y:
                return portal
        return None

    def creatureToItems(self, **kwargs):
        ''' Destroys a creature, turns it into a corpse and drops its inventory items.
        > inventory item feature unadded
        > also want the ability to change the graphic
        > also kwargs can have e.g. weight, useFunction
        not particularly completed.
        '''
        itemList = []
        corpse = Item((self.x, self.y),
                    name=self.uniqueName +"'s corpse",
                    level=self.level,
                    spriteDict=MONSTERS[self.name]["spriteDictDead"],
                    # ^^ that's gross and opaque.
                    monsterType=self.name,
                    **kwargs)
        
        itemList.append(corpse)
        for el in itemList:
            GAME.currentLevel.objects.append(el)

        self.dead = True
        GAME.currentLevel.objects.remove(self)


class Combatant(Creature):
    ''' Combatant takes the Creature class and adds in health, attacking, etc.'''
    def __init__(self, *args, hp=10, deathFunction=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction
 
    def scheduleAttack(self, target: Actor, dhp=-3, **kwargs) -> None:
        if not isinstance(target, Combatant):
            return
        attackDuration = 30 # inverse "attack speed"
        queueEntry = actions.QueuedAttack(self, attackDuration, target=target, dhp=dhp, **kwargs)
        self.actionQueue.appendleft(queueEntry)

    def scheduleDamage(self, dhp=-3, **kwargs) -> None:
        damageDuration = 5 # inverse "attack speed"
        queueEntry = actions.QueuedDamage(self, damageDuration, dhp=dhp, **kwargs)

        # note the backwards appending here-- this interrupts
        self.actionQueue.append(queueEntry)

    def takeDamage(self, damage: float) -> None:
        self.hp -= damage
        GAME.addMessage(self.name + "'s health is " + str(self.hp) + "/" + str(self.maxHp))

        if self.hp <= 0:
            if self.deathFunction:
                self.deathFunction(self)

    def heal(self, deltaHp: float) -> None:
        #TODO!
        assert deltaHp >= 0
        pass


class Viewer(Actor):
    '''As an Actor instance, it has reference to a level and a position.
    Viewers introduce the functionality of having a field of view, and we can 
    calculate what they can see. They also keep a history of what they have seen 
    (think fog of war.) for each level they've interacted with

    Note:  Viewers are not Cameras.  We might care about what an NPC 
    can see, but we often won't use it to reflect what's drawn in the game. 
    '''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explorationHistory = {}
                
    def recalculateFov(self) -> None:
        ''' Using the level's transparency map, recalculate what can be seen 
        from the Viewer's coordinates'''
        self.fov = self.level.computeFov(self.x, self.y).tolist()   

    def getTileIsVisible(self, x: int, y: int) -> bool:
        ''' Can the Viewer see the square x, y '''
        return self.fov[y][x]

    def initLevelExplorationHistory(self) -> None:
        ''' Initialize a map which depicts, for this level, the history of
        what the Viewer has seen.  Needed for fog of war '''
        levelID = self.level.uniqueID
        if levelID not in self.explorationHistory.keys(): #first time visiting a level
            self.explorationHistory[levelID] = np.zeros_like(self.level.map, dtype=np.bool).tolist()

    def setTileIsExplored(self, x: int, y: int):
        ''' Mark that the tile at (x,y) for this level has been seen by Viewer'''
        levelID = self.level.uniqueID
        self.explorationHistory[levelID][y][x] = True
    
    def getTileIsExplored(self, x: int, y: int) -> bool:
        ''' Has viewer perviousy seen the tile at (x,y) for this level?'''
        levelID = self.level.uniqueID
        return self.explorationHistory[levelID][y][x]


class PlayerClass(Combatant, Viewer):
    ''' This class is a Creature, with a field of view -- this name needs to 
    change once we use NPC AIs that care about FOV.   It'll be used for more 
    than just the player(s).  
    '''
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    # def terminateMovement(self) -> None:
    #     super().terminateMovement()
    #     self.recalculateFov()

