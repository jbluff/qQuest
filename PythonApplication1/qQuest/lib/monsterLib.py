from qQuest import magic, actors, ai
from qQuest.graphics import ASSETS

MONSTERS = {}
MONSTERS['jelly'] = {'name' : 'jelly',
                    'animation' : ASSETS.a_jelly,
                    'ai' : "aiTest",
                    'deathFunction' : actors.deathMonster,
                    'kwargs' : {}}

MONSTERS['demon'] = {'name' : 'demon',
                    'animation' : ASSETS.a_demon,
                    'ai' : "aiTest",
                    'deathFunction' : actors.deathMonster,
                    'kwargs' : {}}