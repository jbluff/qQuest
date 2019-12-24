import itertools
import collections

import numpy as np

from qQuest import constants
from qQuest.game import GAME
from qQuest.graphics import Actor
from qQuest.items import Item


class QueueEntry():
    def __init__(self, duration: float):
        self.totalDuration = duration
        self.remainingDuration = duration

    def tick(self, dt: float=1) -> None:
        self.remainingDuration -= dt

    @property
    def completed(self) -> bool:
        return self.remainingDuration <= 0


class QueuedMove(QueueEntry):
    def __init__(self, remainingDuration: float, dx: float, dy: float):
        ''' dx and dy are per time tick '''
        self.dx, self.dy = dx, dy
        super().__init__(remainingDuration)


class Creature(Actor):
    ''' Creatures are Actor children which can move, fight, die '''
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

    def resolveQueueTick(self) -> None:
        ''' Resolve the next entry in the Creature's action queue. '''
        if len(self.creatureQueue) == 0:
            return 

        queueEntry = self.creatureQueue.popleft()
        queueEntry.tick()

        if isinstance(queueEntry, QueuedMove):
            self.executeMove(queueEntry.dx, queueEntry.dy)

            if queueEntry.completed:
                self.terminateMovement()

        if not queueEntry.completed:
            self.creatureQueue.append(queueEntry)

    def scheduleMove(self, dx: int, dy: int) -> None:
        ''' Attempt to queue up a tile -> tile movement.
        dx, dy are differential position.  In units of tiles.'''
        if self.movesInQueue > 0:
            return 
        if dx==0 and dy==0:
            return

        target = self.level.checkForCreature(self.x+dx, self.y+dy, excludeObject=self)
        if target: #this will also become a queued thing later.
            GAME.addMessage(self.name + " attacks " + target.name)
            target.takeDamage(3)
            return 

        tileIsBlocking = self.level.map[self.y+dy][self.x+dx].blocking 
        if not tileIsBlocking:
            duration = int(np.ceil(self.ticksPerMove * np.sqrt(dx**2+dy**2)))
            queueEntry = QueuedMove(duration, dx/duration, dy/duration)
            self.creatureQueue.append(queueEntry)

    @property
    def movesInQueue(self) -> int:
        ''' How many moves have been scheduled?  Helpful for smooth movement. '''
        return sum([isinstance(entry, QueuedMove) for entry in self.creatureQueue])

    def executeMove(self, dx: float, dy: float) -> None:
        ''' Moves graphic, not root tile position. 
        dx & dy are in units of tile, but can be fractional.'''
        self.moving = True
        self.graphicX += dx
        self.graphicY += dy    

    def terminateMovement(self) -> None:
        ''' Called when movement ends.  Cleans up loose ends.'''
        self.x = round(self.graphicX)
        self.y = round(self.graphicY)
        self.moving = False

    def pickupObjects(self) -> None:
        ''' Creature picks up all objects at current coords '''
        objs = self.level.objectsAtCoords(self.x, self.y)
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

    def isOnPortal(self): # -> Portal:
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


class PlayerClass(Creature, Viewer):
    ''' This class is a Creature, with a field of view -- this name needs to 
    change once we use NPC AIs that care about FOV.   It'll be used for more 
    than just the player(s).  
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def terminateMovement(self) -> None:
        super().terminateMovement()
        self.recalculateFov()


class Portal(Actor):
    ''' This class represents a location at which a creature can move rapidly
    from one location and another.  These instances point at another instance
    of the same type, generally (but not necessarily) in a different level.
    '''
    numPortals = 0

    def __init__(self, *args, destinationPortal=None, **kwargs): #: Portal=
        
        self.uniqueID = Portal.numPortals
        Portal.numPortals += 1

        super().__init__(*args, **kwargs)
        self.destinationPortal = destinationPortal
         
    def pickup(self, actor: Actor) -> None:
        return