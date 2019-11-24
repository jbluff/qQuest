from qQuest import magic, actors, ai
from qQuest.graphics import ASSETS

MONSTERS = {}
MONSTERS['jelly'] = {'name' : 'jelly',
                    'animation' : "a_jelly",#ASSETS.a_jelly,
                    'ai' : "aiTest",
                    'deathFunction' : actors.deathMonster,
                    'kwargs' : {}}

MONSTERS['demon'] = {'name' : 'demon',
                    'animation' : "a_demon",#ASSETS.a_demon,
                    'ai' : "aiTest",
                    'deathFunction' : actors.deathMonster,
                    'kwargs' : {}}

NAMES = ['frank', 'james', 'Mephisto, lord of terror',
         'janet', 'juliette', 'Andariel, queen suof the succubi']