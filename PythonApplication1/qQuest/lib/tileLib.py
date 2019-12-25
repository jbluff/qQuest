from collections import namedtuple

# yes, I know it's not a dict.  Deal with it.
# this construction is used for hashability & memoization.
SpriteDict = namedtuple('SpriteDict',['path', 'colIdx', 'rowIdx', 'numSprites'])

TILES = {}
TILES['wall_dungeon_1'] = {'blocking' : True,
                           'seeThru' : False, 
                           'kwargs' : {},
                           'spriteDict' : (SpriteDict('16x16figs/wall.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1),)}
                           
TILES['floor_dungeon_1'] = {'blocking' : False,
                            'seeThru' : True, 
                            'kwargs' : {},
                            'spriteDict' : (SpriteDict('16x16figs/floor.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1),)}

TILES['grass'] = {'blocking' : False,
                  'seeThru' : True, 
                  'kwargs' : {},
                  'spriteDict' : (SpriteDict('dawnlike/Objects/floor.png',
                                colIdx=8,
                                rowIdx=7,
                                numSprites=1),)}