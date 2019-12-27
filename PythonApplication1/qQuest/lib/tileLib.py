from qQuest.constants import SpriteDict 

TILES = {}
TILES['wall_dungeon_1'] = {'blocking' : True,
                           'seeThru' : False, 
                           'spriteDict' : (SpriteDict('16x16figs/wall.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1),)}
                           
TILES['floor_dungeon_1'] = {'blocking' : False,
                            'seeThru' : True, 
                            'spriteDict' : (SpriteDict('16x16figs/floor.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1),)}

TILES['grass'] = {'blocking' : False,
                  'seeThru' : True, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/floor.png',
                                colIdx=8,
                                rowIdx=7,
                                numSprites=1),)}

TILES['greenPointy'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=15,
                                rowIdx=28,
                                numSprites=1),)}