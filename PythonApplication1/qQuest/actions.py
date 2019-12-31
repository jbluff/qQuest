''' Creature actions are handled by a queuing system.  This module contains 
the relevant Action classes. 

I'm not entirely sure I love this construction because its so tightly coupled
to the Creature class but it does make the Creature class a bit easier to parse 
through.'''

from numpy.random import normal

from qQuest import characters 
from qQuest.game import GAME

class QueueEntry():
    def __init__(self, actor: 'characters.Creature', duration: float, emoteName: str=None, **kwargs):
        self.actor = actor
        self.totalDuration = duration
        self.remainingDuration = duration
        self.started = False
        self.emoteName = emoteName

    def tick(self, dt: float=1) -> None:
        self.remainingDuration -= dt
        self.started = True

    @property
    def completed(self) -> bool:
        return self.remainingDuration <= 0

    def execute(self) -> bool:
        ''' returns success.  Non-success means stop this current queued 
        action, completed or not.'''
        raise NotImplementedError("Must be overwritte by child class.")

class QueuedWait(QueueEntry):
    def execute(self) -> bool:
        self.tick()
        return True 

class QueuedMove(QueueEntry):
    def __init__(self, actor: 'characters.Creature', remainingDuration: float, Dx: int, Dy: int, **kwargs):
        self.Dx, self.Dy = Dx, Dy
        super().__init__(actor, remainingDuration, **kwargs)
        # dx and dy are per time tick
        self.dx, self.dy = Dx/self.totalDuration, Dy/self.totalDuration

    def execute(self) -> bool:
        ''' Called each tick and returns success.
        Non-success means stop this current queued movement, completed or not.
        Checks are evaluated if this is the first tick of a QueuedMove.
        '''
        if not self.started:
            nextX = self.actor.x + self.Dx #int tiles
            nextY = self.actor.y + self.Dy   

            level = self.actor.level
            # tileIsBlocking = level.map[nextY][nextX].blocking 
            if level.tileIsBlocking(nextX, nextY):
                return False

            target = level.checkForCreature(nextX, nextY, excludeObject=self)
            if target: 
                self.actor.scheduleAttack(target)
                self.actor.scheduleInteraction(target)
                return False
        
        self.executeMoveTick()

        if self.completed:
            self.terminateMovement()
        return True 

    def executeMoveTick(self) -> None:
        ''' Moves graphic one frame--not root tile position. 
        dx & dy are in units of tile, but can be fractional. 
        '''
        self.actor.graphicX += self.dx
        self.actor.graphicY += self.dy   
        self.tick()

    def terminateMovement(self) -> None:
        ''' Called when movement ends.  Cleans up loose ends. 
        Or it used to, anyways.'''
        self.actor.x = round(self.actor.graphicX)
        self.actor.y = round(self.actor.graphicY)
        if hasattr(self.actor,'recalculateFov'):
            self.actor.recalculateFov()

class QueuedAI(QueueEntry):
    def execute(self) -> bool:
        self.tick()
        if self.completed:
            self.actor.ai.think()
        return True 

class QueuedAttack(QueueEntry):
    ''' The action of attacking and its duration. '''
    def __init__(self, *args, target: 'characters.Combatant'=None, 
                    **kwargs):
        ''' Type  hint should actually be combatant.'''
        self.target = target
        super().__init__(*args, **kwargs)

    def execute(self) -> bool:
        # attack at the start of the duration.
        if not self.started:
            if self.target.dead:
                return False

            GAME.addMessage(f'{self.actor.uniqueName} attacks {self.target.uniqueName}')

            if not dexterityFunction(self.actor, self.target):
                GAME.addMessage(f'... and misses!')
                # add stunned time
                return False

            damage = damageFunction(self.actor, self.target)
            GAME.addMessage(f'... and hits for {damage} hp!')

            self.target.scheduleDamage(dhp=damage, emoteName='fireSmall')        
        self.tick()
        return True 

def dexterityFunction(attacker, target):
    ''' When creature0 attacks creature1, does it succeed? '''
    attackerDex = attacker.dexterity
    targetDex = target.dexterity
    return attackerDex * normal(loc=1.0, scale=0.3) > targetDex

def damageFunction(attacker: 'Combatant', target: 'Combatant'):
    ''' '''
    # attack type..

    attackerStr = attacker.strength
    targetDef = target.defense
    print('in damage function')
    print(f'{attacker.name} has str={attackerStr} during attack')
    print(id(attacker))
    print(id(attacker.container))
    print(attacker.container)
    print("")
    print(id(target))
    print(id(target.container))
    print(target.container)
    dhp = 2*(attackerStr * normal(loc=1.0, scale=0.3) - targetDef)
    dhp = round(dhp)
    return min(-1, -1*dhp)



class QueuedDamage(QueueEntry):
    ''' taking damage (interrupting), and its duration '''
    def __init__(self, *args, dhp:-3, **kwargs):
        self.dhp = dhp
        super().__init__(*args, **kwargs)

    def execute(self) -> bool:
        # damage at the start of the duration.
        # damage type, on fire, stunned etc.
        if not self.started:
            self.actor.takeDamage(-1 * self.dhp)           
        self.tick()
        # if dead return false?
        return True 

class QueuedInteraction(QueueEntry):
    def __init__(self, *args, target: 'characters.Conversationalist'=None, **kwargs):
        ''' Type hint should actually be Conversationalist.'''
        self.target = target
        super().__init__(*args, **kwargs)

    def execute(self) -> bool:
        self.target.interact(self.actor)