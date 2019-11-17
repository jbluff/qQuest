from qQuest import magic
from qQuest.graphics import ASSETS

ITEMS = {}
ITEMS['goggles'] = {'name' : 'Goggles!',
                    'animation' : ASSETS.a_goggles,
                    'useFunction' : None,
                    'equipment' : True,
                    'kwargs' : {}}
ITEMS['healingPotion'] = {'name' : 'healing potion',
                       'animation' : ASSETS.red_potion,
                       'useFunction' : lambda target: magic.castHeal(target, 5),
                       'kwargs' : {}}