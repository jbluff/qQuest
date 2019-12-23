import itertools
import collections

import numpy as np

from qQuest import constants
from qQuest.game import GAME, SURFACE_MAIN, CLOCK
from qQuest.graphics import Actor
from qQuest.items import Item


# TODO:  QueueEntry should be a class.

''' Creatures are Actor children which can move, fight, die
'''
class Creature(Actor):
    def __init__(self, *args, hp=10, deathFunction=None, ai=None, 
                              container=None, speed=0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = hp  
        self.maxHp = hp
        self.deathFunction = deathFunction
 
        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.container = container
        if self.container:
            self.container.owner = self

        self.creatureQueue = collections.deque()
        self.ticksPerMove = 1/speed
        self.moving = False

    def resolveQueueTick(self):
        if len(self.creatureQueue) == 0:
            return 

        eventType, remainingDuration, argsTuple = self.creatureQueue.popleft()
        remainingDuration -= 1

        if eventType == 'move':
            self.executeMove(*argsTuple)

            if remainingDuration <= 0:
                self.terminateMovement()

        if remainingDuration > 0:
            queueEntry = (eventType, remainingDuration, argsTuple)
            self.creatureQueue.append(queueEntry)

    # dx, dy in units of cells.
    def scheduleMove(self, dx, dy):
        if self.moving:
            return 
        if dx==0 and dy==0:
            return

        target = GAME.currentLevel.checkForCreature(self.x + dx, self.y + dy, exclude_object=self)
        if target:
            #this will also become a queud thing later.
            GAME.addMessage(self.name + " attacks " + target.name)
            target.takeDamage(3)
            return 

        tileIsBlocking = GAME.currentLevel.map[self.y + dy][self.x + dx].blocking 
        if not tileIsBlocking:
            # (action type, duration in ticks, argsTuple)
            dt = int(np.ceil(self.ticksPerMove * np.sqrt(dx**2+dy**2)))
            moveTuple = (dx/dt, dy/dt)
            
            queueEntry = ('move', dt, moveTuple)
            self.creatureQueue.append(queueEntry)

    def executeMove(self, dx, dy):
        self.moving = True
        self.graphicX += dx
        self.graphicY += dy    

    def terminateMovement(self) -> None:
        ''' Call this when movement ends.  Cleans up loose ends.'''
        self.x = round(self.graphicX)
        self.y = round(self.graphicY)
        self.moving = False

    def pickupObjects(self) -> None:
        ''' Creature picks up all objects at current coords '''
        objs = GAME.currentLevel.objectsAtCoords(self.x, self.y)
        [obj.pickup(self) for obj in objs if isinstance(obj, (Item,))]

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

    def isOnPortal(self) -> Portal:
        ''' if Creatre standing on a portal, returns that Portal.  
        Otherwise returns None. '''
        for portal in self.level.portals:
            if self.x == portal.x and self.y == portal.y:
                return portal
        return None
  
class Viewer(Actor):
    """As an Actor instance, it has reference to a level and a position.
    Viewers introduce the functionality of having a field of view, and we can calculate what they can see.
    They also keep a history of what they have seen (think fog of war.) for each level they've interacted with

    Note:  Viewers are not (generally) Cameras.  We might care about what an NPC can see, but we often
        won't use it to reflect what's drawn in the game. 
    """
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


''' This class is a Creature, with a field of view -- this name needs to change once we use NPC
AIs that care about FOV.   It'll be used for more than just the player(s).  
'''
class PlayerClass(Creature, Viewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def terminateMovement(self) -> None:
        super().terminateMovement()
        self.recalculateFov()

#  pos, name, animationName, 
#  These will move to their own place..
class Portal(Actor):
    numPortals = 0

    def __init__(self, *args, destinationPortal=None, **kwargs):
        
        self.uniqueID = Portal.numPortals
        Portal.numPortals += 1

        super().__init__(*args, **kwargs)
        self.destinationPortal = destinationPortal
         
    def pickup(self, actor: Actor) -> None:
        return