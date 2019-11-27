import itertools
import numpy as np

import tcod as libtcod
from qQuest import constants

def initializeFovMap(mapIn):
    ''' Takes the existing map make of structTiles, uses it's blockpath properties
    to detemine which fovMap tiles we be considered transparent.'''

    mapHeight, mapWidth = np.array(mapIn).shape

    fovMap = libtcod.map.Map(width=mapWidth, height=mapHeight)
    for (y, x) in itertools.product(range(mapHeight), range(mapWidth)):
        fovMap.transparent[y][x] = not mapIn[y][x].blockPath

    return fovMap


    

