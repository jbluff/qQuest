from qQuest import magic, items, ai
from qQuest.constants import SpriteDict 
                           

CHARACTERS = {}
CHARACTERS['jelly'] = {
       'name' : 'jelly',
       'aiName' : "aiRandom",
       'speed' : 0.07,
       'deathFunction' : items.deathMonster,
       'spriteDict' : (SpriteDict('16x16figs/jellySheet.png',
                                   colIdx=0, rowIdx=0, numSprites=2),),
       'spriteDictDead' : (SpriteDict('16x16figs/jellySheet.png',
                                   colIdx=0, rowIdx=0, numSprites=1),)}

CHARACTERS['demon'] = {
       'name' : 'demon',
       'aiName' : 'aiDumbAggro', 
       'deathFunction' : items.deathMonster,
       'speed' : 0.05,
       'spriteDict' : (SpriteDict('dawnlike/Characters/Demon0.png',
                                   colIdx=5, rowIdx=1, numSprites=1),
                      SpriteDict('dawnlike/Characters/Demon1.png',
                            colIdx=5, rowIdx=1, numSprites=1)),
       'spriteDictDead' : (SpriteDict('dawnlike/Characters/Demon0.png',
                                   colIdx=5,
                                   rowIdx=1,
                                   numSprites=1),)}

CHARACTERS['slime'] = {
       'name' : 'slime',
       'aiName' : "aiDumbCoward",
       'deathFunction' : items.deathMonster,
       'speed' : 0.02,
       'spriteDict' : (SpriteDict('dawnlike/Characters/Slime0.png',
                                   colIdx=0, rowIdx=4,
                                   numSprites=1),
                       SpriteDict('dawnlike/Characters/Slime1.png',
                                   colIdx=0, rowIdx=4, numSprites=1)),
       'spriteDictDead' : (SpriteDict('dawnlike/Characters/Slime0.png',
                                   colIdx=0, rowIdx=4, numSprites=1),)}

CHARACTERS['townNPC'] = {
       'name' : 'townNPC',
       'aiName' : 'aiPassiveNPC',
       'spriteDict' : (SpriteDict('dawnlike/Characters/Dog0.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1),
                      SpriteDict('dawnlike/Characters/Dog1.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1)),
       'combatant': False,
       'conversationalist' : True,
       'script' : {
            'start' : {
                'readText' : 'Would you like to go to A or B?',
                'options' : {
                    'optionA' : {
                        'optionText' : "doesn't A sound great?",
                        'goto' : 'A'
                    },
                    'optionB' : {
                        'optionText' : "doesn't B sound great?",
                        'goto' : 'B'
                    },
                }, 
            },
            'A' : {
                'readText' : 'Welcome to A!',
            }, 
            'B' : {
                'readText' : 'Welcome to B!',
            }              
       }
       }

NAMES = ['jonny', 'james', 'Mephisto, lord of terror',
         'janet', 'juliette', 'Andariel, queen of the succubi']