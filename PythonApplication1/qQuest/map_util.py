import tcod as libtcod
import pygame
import json, os, copy, random
import numpy as np

from qQuest import constants
from qQuest.qqGlobal import GAME, SURFACE_MAIN

class structTile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False

def loadLevelFile(levelName):
    filePath = os.path.join(os.path.dirname(__file__),"..","levels",levelName+".lvl")

    with open(filePath, "r") as levelFile:
        levelDict = json.load(levelFile)
    levelFile.close()

    return levelDict

def loadLevel(levelDict):
    levelArray = levelDict["level"]
    decoder = levelDict["decoderRing"]

    mapHeight = len(levelArray)
    mapWidth = len(levelArray[0])
    GAME.mapHeight = len(levelArray)
    GAME.mapWidth = len(levelArray[0])

    print(mapHeight)
    print(mapWidth)
    newMap = [[structTile(False) for y in range(0, mapHeight)] for x in range(0, mapWidth )]

    for i in range(GAME.mapHeight):
        for j in range(GAME.mapWidth):
            tileType = decoder[levelArray[i][j]]
            if tileType == "wall":
                newMap[j][i].blockPath = True

    GAME.updateSurfaceSize()

    return newMap

def createFovMap(mapIn):
    ''' the index order gets hosed here.  tcod is weird.'''
    fovMap = libtcod.map.Map(width=GAME.mapWidth, height=GAME.mapHeight)
    for y in range(GAME.mapHeight):
        for x in range(GAME.mapWidth):
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

