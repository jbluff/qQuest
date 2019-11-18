import tcod as libtcod
import pygame
import json, os
import numpy as np

#from qQuest import constants
#from qQuest.qqGlobal import GAME, SURFACE_MAIN

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

def makeWalledRoom(width, height):
    mapArray = [["#",] * width,]
    for i in range(height-2):
        mapArray += [["#",] + ["_",] * (width-2) + ["#",],]
    mapArray += [["#",] * width,]
    return np.array(mapArray, dtype=np.str)

def makeRoom(width, height, symbol="_"):
    mapArray = [[symbol,] * width,]*height
    return np.array(mapArray, dtype=np.str)

def placeRoom(mapArray, roomArray, x=0, y=0):
    mapYSize, mapXSize = mapArray.shape
    roomYSize, roomXSize = roomArray.shape

    dx, dy = 0, 0
    if (x<0):
        dx = 0-x #changing the index point
        mapArray = expandMapLeft(mapArray, dx)
        mapYSize, mapXSize = mapArray.shape
        x += dx 
    if (x+roomXSize > mapXSize):
        mapArray = expandMapRight(mapArray, x+roomXSize-mapXSize)
        mapYSize, mapXSize = mapArray.shape
    if (y<0):
        dy = 0-y
        mapArray = expandMapUp(mapArray, dy)
        mapYSize, mapXSize = mapArray.shape
        y += dy
    if (y+roomYSize > mapYSize):
        mapArray = expandMapDown(mapArray, y+roomYSize-mapYSize)
        mapYSize, mapXSize = mapArray.shape

    for i,xRow in enumerate(mapArray):
        for j, el in enumerate(xRow):
            # i becomes y, j becomes x
            if j >= x and j<x+roomXSize and i >= y and i < y+roomYSize:
                mapArray[i][j] = roomArray[i-y][j-x] 
    return mapArray



def expandMapLeft(mapArray, dx):
    ySize, xSize = mapArray.shape
    print("Expanding left")
    newMapArray = makeRoom(xSize+dx, ySize, symbol="#")
    return placeRoom(newMapArray, mapArray, x=dx, y=0)

def expandMapRight(mapArray, dx):
    ySize, xSize = mapArray.shape
    print("Expanding right")
    newMapArray = makeRoom(xSize+dx, ySize, symbol="#")
    return placeRoom(newMapArray, mapArray, x=0, y=0)

def expandMapUp(mapArray, dy):
    ySize, xSize = mapArray.shape
    print("Expanding up")
    newMapArray = makeRoom(xSize, ySize+dy, symbol="#")
    return placeRoom(newMapArray, mapArray, x=0, y=dy)

def expandMapDown(mapArray, dy):
    ySize, xSize = mapArray.shape
    print("Expanding down")
    newMapArray = makeRoom(xSize, ySize+dy, symbol="#")
    return placeRoom(newMapArray, mapArray, x=0, y=0)

if __name__ == "__main__":
    mapArray = np.array([["#",]*10,]*10, dtype=np.str)

    newRoom = makeRoom(3, 3, symbol="_")
    mapArray = placeRoom(mapArray, newRoom, x=2, y=2)

    newRoom = makeRoom(5, 3, symbol="_")
    mapArray = placeRoom(mapArray, newRoom, x=2, y=7)
    print(mapArray)

    #mapArray = expandMapUp(mapArray, 3)
    #print(mapArray)
    pass

    
