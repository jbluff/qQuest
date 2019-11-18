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

def squareRoom(width, height):
    mapArray = [["_",] * width,]
    for i in range(height-2):
        mapArray += [["_",] + ["_",] * (width-2) + ["_",],]
    mapArray += [["_",] * width,]
    return np.array(mapArray, dtype=np.str)

def placeRoom(mapArray, roomArray, x=0, y=0):
    mapYSize, mapXSize = mapArray.shape
    roomYSize, roomXSize = roomArray.shape

    dx, dy = 0, 0
    if (x<0):
        dx = 0-x #changing the index point
        mapArray = expandMapLeft(mapArray, dx)
        x += dx 
    if (x+roomXSize > mapXSize):
        mapArray = expandMapRight(mapArray, x+roomXSize-mapXSize)
    if (y<0):
        dy = 0-y
        mapArray = expandMapUp(mapArray, dy)
        y += dy
    if (y+roomYSize > mapYSize):
        mapArray = expandMapDown(mapArray, y+roomYSize-mapYSize)

    for i,xRow in enumerate(mapArray):
        for j, el in enumerate(xRow):
            # i becomes y, j becomes x
            if j >= x and j<x+roomXSize and i >= y and i < y+roomYSize:
                mapArray[i][j] = roomArray[i-y][j-x] 
    return mapArray



def expandMapLeft(mapArray, dx):
    ySize, xSize = mapArray.shape
    print("Expanding left")
    newMapArray = np.array([["#",]*(xSize+dx),]*(ySize), dtype=np.str)
    newMapArray = placeRoom(newMapArray, mapArray, x=dx, y=0)
    return newMapArray

def expandMapRight(mapArray, dx):
    ySize, xSize = mapArray.shape
    print("Expanding right")
    newMapArray = np.array([["#",]*(xSize+dx),]*(ySize), dtype=np.str)
    newMapArray = placeRoom(newMapArray, mapArray, x=0, y=0)
    return newMapArray

def expandMapUp(mapArray, dy):
    ySize, xSize = mapArray.shape
    print("Expanding up")
    newMapArray = np.array([["#",]*(xSize),]*(ySize+dy), dtype=np.str)
    newMapArray = placeRoom(newMapArray, mapArray, x=0, y=dy)
    return newMapArray

def expandMapDown(mapArray, dy):
    ySize, xSize = mapArray.shape
    print("Expanding down")
    newMapArray = np.array([["#",]*(xSize),]*(ySize+dy), dtype=np.str)
    newMapArray = placeRoom(newMapArray, mapArray, x=0, y=0)
    return newMapArray


if __name__ == "__main__":
    mapArray = np.array([["#",]*8,]*7, dtype=np.str)
    room = squareRoom(2, 4)

    mapArray = placeRoom(mapArray, room, x=2, y=15)

    print(mapArray)

    #mapArray = expandMapUp(mapArray, 3)
    #print(mapArray)
    pass

    
