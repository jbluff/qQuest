import tcod as libtcod
import pygame
import json, os, copy, random
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
class Room:
    def __init__(self, roomArray, x, y, corridor=False):
        self.roomArray = np.array(roomArray)
        self.x = x # x address of upper left pt
        self.y = y # y address of upper left pt

        self.w = roomArray.shape[1]
        self.h = roomArray.shape[0]

        self.cooridor = corridor

    def translate(self, vector):
        self.x += vector[0]
        self.y += vector[1]

class Map:
    def __init__(self, initWidth=10, initHeight=10):
        self.mapArray = makeRoom(initWidth, initHeight, symbol="#").roomArray
        self.rooms = [] 

        self.width, self.height = initWidth, initHeight

    def renderArray(self):
        self.mapArray = makeRoom(self.width, self.height, symbol="#").roomArray

        for room in self.rooms:
            # There must be a good numpy way to do this.
            for y, row in enumerate(list(room.roomArray)):
                for x, el in enumerate(row):
                    self.mapArray[room.y+y][room.x+x] = el

            #self.mapArray[room.y:room.y+room.h-1][room.x:room.x+room.w-1] = room.roomArray

    def plot(self):
        print('\n')
        for row in self.mapArray:
            print(''.join(row))
        print('\n')

    # def expandMapLeft(self, dx):
    #     self.expandMap((dx, 0), (dx,0))

    # def expandMapRight(self, dx):
    #     self.expandMap((dx, 0), (0,0))

    # def expandMapUp(self, dy):
    #     self.expandMap((0, dy), (0,dy))

    # def expandMapDown(self, dy):
    #     self.expandMap((0, dy), (0,0))

    # Also offset all existing room datas
    # Signs represent directions -- this function cannot shrink map
    def expandMap(self, deltaTuple):

        dx, dy = deltaTuple

        self.width += abs(dx)
        self.height += abs(dy)

        if (dx < 0):
            for i, room in enumerate(self.rooms):
                room.translate((abs(dx),0))
        if (dy < 0):
            for i, room in enumerate(self.rooms):
                room.translate((0,abs(dy)))

    
    def placeRoom(self, room, x=None, y=None):#, addRoomIndex=True):

        if x:
            room.x = x
        if y:
            room.y = y

        self.rooms.append(room)

        if x < 0:
            self.expandMap((abs(x,0)))
        if y < 0:
            self.expandMap((abs(y,0)))


        if x + room.w > self.width:
            self.expandMap((x+room.w-self.width,0))

        if y + room.h > self.height:
            self.expandMap((0, y+room.h-self.height))




    # def placeRoomAtPoint(self, roomArray, point, vector, **kwargs):
    #     roomYSize, roomXSize = roomArray.shape

    #     if (vector == (0,+1)).all(): # facing right
    #         x = point[0]+1
    #         y = point[1] + round((random.random()-0.5) * roomYSize)

    #         self.placeRoom(roomArray, x=0, y=0, **kwargs)



def makeRoom(width, height, symbol="_", **kwargs):
    mapArray = [[symbol,] * width,]*height
    return Room(np.array(mapArray, dtype=np.str), 0, 0, **kwargs)

#  Given a room tuple, return a point on the edge and the normal vector
def chooseRandomBorderPoint(roomList):
    # upperLeftX, upperLeftY, lowerRightX, lowerRightY
    side = random.randint(0,3) # top, right, bottom, left
   
    roomWidth = roomList[2] - roomList[0]
    roomHeight = roomList[3] - roomList[1]

    if side==0: # top
        yLoc = roomList[1]
        xLoc = roomList[0]  + random.randint(0, roomWidth-1)
        vector = (0,-1)
    elif side==2: # bottom
        yLoc = roomList[3]
        xLoc = roomList[0]  + random.randint(0, roomWidth-1)
        vector = (0,+1)
    elif side==1: # right
        xLoc = roomList[2]
        yLoc = roomList[1]  + random.randint(0, roomHeight-1)
        vector = (+1,0)
    elif side==3: # left
        xLoc = roomList[0]
        yLoc = roomList[1]  + random.randint(0, roomHeight-1)
        vector = (-1,0)

    return np.array([xLoc, yLoc]), np.array(vector)

# returns what would be the next point (where a new room might start..)
def tunnelOut(map, roomIdx, numPnts):
    # TODO:  add turning
    point, vector = chooseRandomBorderPoint(newMap.rooms[roomIdx])
    singleTile = makeRoom(1,1,symbol="_")
    
    point += vector
    newMap.placeRoom(singleTile, *point, addRoomIndex=False)
    for i in range(numPnts-1):
        point += vector
        print(point)
        newMap.placeRoom(singleTile, *point, addRoomIndex=False)       
    
    return point, vector


if __name__ == "__main__":
    newMap = Map(8,8)

    newRoom = makeRoom(4,5)
    newMap.placeRoom(newRoom, x=2, y=2)
    newMap.renderArray()
    newMap.plot()

    #newMap.expandMap((1,1))
    #newMap.renderArray()
    #newMap.plot()
    #newMap.expandMapLeft(1)

    #point, vector = tunnelOut(newMap, 0, 5)
    #newMap.plot()

    #newMap.placeRoomAtPoint(newRoom, point, vector, addRoomIndex=True)
    #newMap.plot()

    # point, vector = chooseRandomBorderPoint(newMap.rooms[0])
    # newMap.mapArray[point[1], point[0]] = "+"
    # newMap.mapArray[point[1]+vector[1], point[0]+vector[0]] = "Q"
    # newMap.plot()
    # print(point)
    # print(vector)


    # mapArray = np.array([["#",]*10,]*10, dtype=np.str)

    # newRoom = makeRoom(3, 3, symbol="_")
    # mapArray = placeRoom(mapArray, newRoom, x=2, y=2)

    # print(mapArray)
    pass

    
