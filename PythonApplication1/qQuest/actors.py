import itertools
import collections
import math

import numpy as np

from qQuest import constants
from qQuest.game import GAME
from qQuest.graphics import Actor
from qQuest.items import Item


class QueueEntry():
    def __init__(self, duration: float):
        self.totalDuration = duration
        self.remainingDuration = duration
        self.started = False

    def tick(self, dt: float=1) -> None:
        self.remainingDuration -= dt
        self.started = True

    @property
    def completed(self) -> bool:
        return self.remainingDuration <= 0


class QueuedMove(QueueEntry):
    def __init__(self, remainingDuration: float, Dx: int, Dy: int):
        self.Dx, self.Dy = Dx, Dy
        super().__init__(remainingDuration)
        # dx and dy are per time tick
        self.dx, self.dy = Dx/self.totalDuration, Dy/self.totalDuration

class QueuedAI(QueueEntry):
    pass

class QueuedAttack(QueueEntry):
    def __init__(self, remainingDuration: float, target: Actor):
        self.target = target
        super().__init__(remainingDuration)

class Creature(Actor):
    ''' Creatures are Actor children which can move, fight, die '''
    def __init__(self, *args, hp=10, deathFunction=None, ai=None, 
                              container=None, speed=0.07, **kwargs):
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

    def resolveQueueTick(self) -> None:
        ''' Resolve the next entry in the Creature's action queue. '''
        if len(self.creatureQueue) == 0:
            if self.ai is not None:
                self.scheduleAI()
            return 

        queueEntry = self.creatureQueue.pop()
        if isinstance(queueEntry, QueuedMove):
            success = self.executeMove(queueEntry)
            if queueEntry.completed:
                self.terminateMovement()
 
        if isinstance(queueEntry, QueuedAI):
            success = self.executeAI(queueEntry)

        if isinstance(queueEntry, QueuedAttack):
            success = self.executeAttack(queueEntry)

        if not queueEntry.completed and success:
            self.creatureQueue.append(queueEntry)

    def scheduleMove(self, dx: int, dy: int) -> None:
        ''' Attempt to queue up a tile -> tile movement.
        dx, dy are differential position.  In units of tiles.'''
        MAX_QUEUED_MOVES = 2
        if self.movesInQueue >= MAX_QUEUED_MOVES:
            return 
        if dx==0 and dy==0:
            return

        duration = int(math.ceil(self.ticksPerMove * np.sqrt(dx**2+dy**2)))
        queueEntry = QueuedMove(duration, dx, dy)
        self.creatureQueue.append(queueEntry)

    @property
    def movesInQueue(self) -> int:
        ''' How many moves have been scheduled?  Helpful for smooth movement. '''
        return sum([isinstance(entry, QueuedMove) for entry in self.creatureQueue])

    def executeMove(self, queueEntry: QueuedMove) -> bool:
        ''' Moves graphic, not root tile position. 
        dx & dy are in units of tile, but can be fractional.'''

        # if the move hasn't initiated yet, do some checks.
        if not queueEntry.started:
            nextX = self.x + queueEntry.Dx
            nextY = self.y + queueEntry.Dy
            tileIsBlocking = self.level.map[nextY][nextX].blocking 
            if tileIsBlocking:
                return False

            target = self.level.checkForCreature(nextX, nextY, excludeObject=self)
            if target:
                self.scheduleAttack(target)
                return False

        self.executeMoveTick(queueEntry)
        return True 

    def executeMoveTick(self, queueEntry: QueuedMove) -> None:
        ''' Moves graphic one frame, not root tile position. 
        dx & dy are in units of tile, but can be fractional. '''
        self.graphicX += queueEntry.dx
        self.graphicY += queueEntry.dy   
        queueEntry.tick()

    def terminateMovement(self) -> None:
        ''' Called when movement ends.  Cleans up loose ends. Or it used to, anyways.'''
        self.x = round(self.graphicX)
        self.y = round(self.graphicY)

    def scheduleAI(self) -> None:
        queueEntry = QueuedAI(self.ai.thinkingDuration)
        self.creatureQueue.append(queueEntry)

    def executeAI(self, queueEntry: QueuedAI) -> bool:
        # think at the end of the duration.
        queueEntry.tick()
        if queueEntry.completed:
            self.ai.think()
            return False
        return True 

    def scheduleAttack(self, target: Actor) -> None:
        attackDuration = 30 # inverse "attack speed"
        queueEntry = QueuedAttack(attackDuration, target)
        self.creatureQueue.append(queueEntry)

    def executeAttack(self, queueEntry: QueuedAttack) -> bool:
        # attack at the start of the duration.
        # do fun graphicsy things... or sound effects.  woah.
        if not queueEntry.started:
            GAME.addMessage(self.name + " attacks " + queueEntry.target.name)
            queueEntry.target.takeDamage(3)           
        queueEntry.tick()
        if queueEntry.completed:
            return False
        return True 

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
        
        self.uniqueID = f'portal{Portal.numPortals}'
        Portal.numPortals += 1

        super().__init__(*args, **kwargs)
        self.destinationPortal = destinationPortal
         
    def pickup(self, actor: Actor) -> None:
        return