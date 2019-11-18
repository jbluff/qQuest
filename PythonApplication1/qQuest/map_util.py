import tcod as libtcod
import pygame
import json, os, copy
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

# def makeWalledRoom(width, height):
#     mapArray = [["#",] * width,]
#     for i in range(height-2):
#         mapArray += [["#",] + ["_",] * (width-2) + ["#",],]
#     mapArray += [["#",] * width,]
#     return np.array(mapArray, dtype=np.str)
class Map:
    def __init__(self, initWidth=10, initHeight=10):
        self.mapArray = makeRoom(initWidth, initHeight, symbol="#")
        self.rooms = [] #Id'd by four number:  upperLeftX, upperLeftY, lowerRightX, lowerRightY

    def plot(self):
        print('\n')
        for row in self.mapArray:
            print(''.join(row))
        print('\n')

    def expandMapLeft(self, dx):
        self.expandMap((dx, 0), (dx,0))

    def expandMapRight(self, dx):
        self.expandMap((dx, 0), (0,0))

    def expandMapUp(self, dy):
        self.expandMap((0, dy), (0,dy))

    def expandMapDown(self, dy):
        self.expandMap((0, dy), (0,0))

    # Also offset all existing room datas
    def expandMap(self, deltaTuple, offsetTuple):
        ySize, xSize = self.mapArray.shape
        oldRoom = copy.copy(self.mapArray)
        self.mapArray = makeRoom(xSize+deltaTuple[0], ySize+deltaTuple[1], symbol="#")

        dx, dy = offsetTuple
        self.placeRoom(oldRoom, x=dx, y=dy, addRoomIndex=False)
        for i, roomList in enumerate(self.rooms):
            [a, b, c, d] = roomList
            self.rooms[i] = [a+dx, b+dy, c+dx, d+dy]
        del oldRoom

    
    def placeRoom(self, roomArray, x=0, y=0, addRoomIndex=True):
        mapYSize, mapXSize = self.mapArray.shape
        roomYSize, roomXSize = roomArray.shape

        dx, dy = 0, 0
        if (x<0):
            dx = 0-x #changing the index point
            self.expandMapLeft(dx)
            x += dx 
        if (x+roomXSize > self.mapArray.shape[1]):
            self.expandMapRight(x+roomXSize-mapXSize)
        if (y<0):
            dy = 0-y
            self.expandMapUp(dy)
            y += dy
        if (y+roomYSize > self.mapArray.shape[0]):
            self.expandMapDown(y+roomYSize-mapYSize)

        for i,xRow in enumerate(self.mapArray):
            for j, el in enumerate(xRow):
                # i becomes y, j becomes x
                if j >= x and j<x+roomXSize and i >= y and i < y+roomYSize:
                    self.mapArray[i][j] = roomArray[i-y][j-x] 

        #Id'd by four number:  upperLeftX, upperLeftY, lowerRightX, lowerRightY
        if addRoomIndex:
            self.rooms.append([x,y,x+roomXSize-1, y+roomYSize-1])


def makeRoom(width, height, symbol="_"):
    mapArray = [[symbol,] * width,]*height
    return np.array(mapArray, dtype=np.str)


if __name__ == "__main__":
    newMap = Map(5,5)

    newRoom = makeRoom(3,3)
    newMap.placeRoom(newRoom, -1, -1)
    newMap.plot()
    print(newMap.rooms)

    newMap.expandMapLeft(1)
    newMap.plot()
    print(newMap.rooms)

    newMap.expandMapRight(1)
    newMap.plot()
    print(newMap.rooms)

    # mapArray = np.array([["#",]*10,]*10, dtype=np.str)

    # newRoom = makeRoom(3, 3, symbol="_")
    # mapArray = placeRoom(mapArray, newRoom, x=2, y=2)

    # print(mapArray)
    pass

    
