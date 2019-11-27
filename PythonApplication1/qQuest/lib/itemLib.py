from qQuest import magic

ITEMS = {}
ITEMS['goggles'] = {'name' : 'Goggles!',
                    'animation' : "a_goggles",#ASSETS.a_goggles,
                    'useFunction' : None,
                    'equipment' : True,
                    'kwargs' : {}}
ITEMS['healingPotion'] = {'name' : 'healing potion',
                       'animation' : "a_red_potion",#ASSETS.red_potion,
                       'useFunction' : lambda target: magic.castHeal(target, 5),
                       'kwargs' : {}}
