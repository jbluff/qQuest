from qQuest import magic
from qQuest.constants import SpriteDict 

ITEMS = {}
ITEMS['goggles'] = {'name' : 'Goggles!',
                    'useFunction' : None,
                    'equipment' : True,
                    'spriteDict' : (SpriteDict('dawnlike/Items/Tool.png',
                            colIdx=3,
                            rowIdx=0,
                            numSprites=1),),
                    'defenseBonus' : 20}

ITEMS['healingPotion'] = {'name' : 'Healing Potion',
                       'useFunction' : lambda target: magic.castHeal(target, 5),
                       'spriteDict' : (SpriteDict('dawnlike/Items/Potion.png',
                            colIdx=0,
                            rowIdx=0,
                            numSprites=1),),}

ITEMS['shortSword'] = {'name' : 'Short sword',
                    'useFunction' : None,
                    'equipment' : True,
                    'spriteDict' : (SpriteDict('dawnlike/Items/ShortWep.png',
                            colIdx=0,
                            rowIdx=0,
                            numSprites=1),),
                    'strengthBonus' : 10}