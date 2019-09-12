
def deathMonster(game, monster):
    '''
    What happens when a non-player character dies?
    Monster is actor class instance.
    '''
    game.addMessage(monster.creature.name + " has been slain!")
    monster.creature = None
    monster.ai = None
