from qQuest import magic, items, ai
from qQuest.constants import SpriteDict 
                           

MONSTERS = {}
MONSTERS['jelly'] = {'name' : 'jelly',
                    'aiName' : "aiRandom",
                    'deathFunction' : items.deathMonster,
                    'spriteDict' : (SpriteDict('16x16figs/jellySheet.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=2),),
                    'spriteDictDead' : (SpriteDict('16x16figs/jellySheet.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1),),
                    'kwargs' : {}}

MONSTERS['demon'] = {'name' : 'demon',
                    'aiName' : 'aiDumbAggro', 
                    'deathFunction' : items.deathMonster,
                    'spriteDict' : (SpriteDict('dawnlike/Characters/Demon0.png',
                                           colIdx=5,
                                           rowIdx=1,
                                           numSprites=1),
                                    SpriteDict('dawnlike/Characters/Demon1.png',
                                           colIdx=5,
                                           rowIdx=1,
                                           numSprites=1)),
                    'spriteDictDead' : (SpriteDict('dawnlike/Characters/Demon0.png',
                                           colIdx=5,
                                           rowIdx=1,
                                           numSprites=1),),
                    'kwargs' : {}}

MONSTERS['slime'] = {'name' : 'slime',
                    'aiName' : "aiDumbCoward",
                    'deathFunction' : items.deathMonster,
                    'spriteDict' : (SpriteDict('dawnlike/Characters/Slime0.png',
                                           colIdx=0,
                                           rowIdx=4,
                                           numSprites=1),
                                    SpriteDict('dawnlike/Characters/Slime1.png',
                                           colIdx=0,
                                           rowIdx=4,
                                           numSprites=1)),
                    'spriteDictDead' : (SpriteDict('dawnlike/Characters/Slime0.png',
                                           colIdx=0,
                                           rowIdx=4,
                                           numSprites=1),),
                    'kwargs' : {}}

NAMES = ['jonny', 'james', 'Mephisto, lord of terror',
         'janet', 'juliette', 'Andariel, queen of the succubi']