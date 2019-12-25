from collections import namedtuple

# yes, I know it's not a dict.  Deal with it.
SpriteDict = namedtuple('SpriteDict',['path', 'colIdx', 'rowIdx', 'numSprites'])

TILES = {}
TILES['wall_dungeon_1'] = {'animation' : "wall_dungeon_1",
                           'blocking' : True,
                           'seeThru' : False, 
                           'kwargs' : {},
                           'spriteDict' : (SpriteDict('16x16figs/wall.png',
                                           colIdx=0,
                                           rowIdx=0,
                                           numSprites=1),)
                           }
TILES['floor_dungeon_1'] = {'animation' : "floor_dungeon_1",
                           'blocking' : False,
                           'seeThru' : True, 
                           'kwargs' : {}}
TILES['grass'] = {'animation' : "grass_1",
                           'blocking' : False,
                           'seeThru' : True, 
                           'kwargs' : {}}