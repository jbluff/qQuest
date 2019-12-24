from qQuest import magic, items, ai

MONSTERS = {}
MONSTERS['jelly'] = {'name' : 'jelly',
                    'animation' : "a_jelly",
                    'ai' : "aiRandom",
                    'deathFunction' : items.deathMonster,
                    'kwargs' : {}}

MONSTERS['demon'] = {'name' : 'demon',
                    'animation' : "a_demon",
                    'ai' : 'aiDumbCoward',#'aiDumbAggro', #"aiTest",
                    'deathFunction' : items.deathMonster,
                    'kwargs' : {}}

NAMES = ['jonny', 'james', 'Mephisto, lord of terror',
         'janet', 'juliette', 'Andariel, queen of the succubi']