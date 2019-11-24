import itertools
import numpy as np

import tcod as libtcod
from qQuest import constants

def createFovMap(mapIn):
    ''' Takes the existing map make of structTiles, uses it's blockpath properties
    to detemine which fovMap tiles we be considered transparent.'''

    mapHeight, mapWidth = np.array(mapIn).shape

    fovMap = libtcod.map.Map(width=mapWidth, height=mapHeight)
    for (y, x) in itertools.product(range(mapHeight), range(mapWidth)):
        fovMap.transparent[y][x] = not mapIn[y][x].blockPath

    #fovMap.transparent = np.array([[not el.blockPath for x, el in enumerate(row)] for y, row in enumerate(mapIn)])
    return fovMap

def mapCalculateFov(actor):
    ''' recalculate Fov based on fovmap and position. '''

    if not actor.fovCalculate:
        return
    actor.fovMap.compute_fov(actor.x,actor.y,
                       radius = constants.FOV_RADIUS,
                       light_walls = constants.FOV_LIGHT_WALLS,
                       algorithm = constants.FOV_ALGO)
    actor.fovCalculate = False

