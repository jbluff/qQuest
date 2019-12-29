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

TILES['greenHouse_left'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=14,
                                rowIdx=28,
                                numSprites=1),)}
TILES['greenHouse_backLeft'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=14,
                                rowIdx=27,
                                numSprites=1),)}
TILES['greenHouse_back'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=15,
                                rowIdx=27,
                                numSprites=1),)}
TILES['greenHouse_backRight'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=16,
                                rowIdx=27,
                                numSprites=1),)}
TILES['greenHouse_right'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=16,
                                rowIdx=28,
                                numSprites=1),)}
TILES['greenHouse_frontRight'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=16,
                                rowIdx=29,
                                numSprites=1),)}
TILES['greenHouse_frontLeft'] = {'blocking' : True,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Wall.png',
                                colIdx=14,
                                rowIdx=29,
                                numSprites=1),)}

TILES['bed'] = {'blocking' : True,
                  'seeThru' : True, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Decor0.png',
                                colIdx=0,
                                rowIdx=9,
                                numSprites=1),)}

TILES['door'] = {'blocking' : False,
                  'seeThru' : False, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Door0.png',
                                colIdx=0,
                                rowIdx=0,
                                numSprites=1),)}

TILES['tree'] = {'blocking' : True,
                  'seeThru' : True, 
                  'spriteDict' : (SpriteDict('dawnlike/Objects/Tree0.png',
                                colIdx=3,
                                rowIdx=3,
                                numSprites=1),
                                SpriteDict('dawnlike/Objects/Tree1.png',
                                colIdx=3,
                                rowIdx=3,
                                numSprites=1))}

