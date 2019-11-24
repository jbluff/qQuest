import tcod as libtcod
#import pygame
#import json, os, copy, random
import numpy as np

from qQuest import constants
#from qQuest.qqGlobal import GAME, SURFACE_MAIN

def createFovMap(mapIn):
    ''' the index order gets hosed here.  tcod is weird.
    i have no excuse for this'''

    #mapHeight, mapWidth = np.array(mapIn).shape
    mapWidth, mapHeight = np.array(mapIn).shape

    fovMap = libtcod.map.Map(width=mapWidth, height=mapHeight)
    for y in range(mapHeight):
        for x in range(mapWidth):
            val = mapIn[x][y].blockPath
            fovMap.transparent[y][x] = not val
    return fovMap

def mapCalculateFov(actor):
    ''' the index order gets hosed here.  tcod is weird.'''

    if not actor.fovCalculate:
        return

    actor.fovMap.compute_fov(actor.x,actor.y,
                       radius = constants.FOV_RADIUS,
                       light_walls = constants.FOV_LIGHT_WALLS,
                       algorithm = constants.FOV_ALGO)
    actor.fovCalculate = False

