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

class Walker:
    def __init__(self, mapInst, roomIdx):
        self.map = mapInst
        self.roomIdx = roomIdx

        self.room = self.map.rooms[self.roomIdx]

        self.x, self.y = 0, 0
        self.vector = (1, 0) #x, y

        self.distanceTravelled = 0

        self.turnProbability = 0.2
        self.travelDistance = 10

    def render(self):
        self.map.mapArray[self.y][self.x] = "@"

    def chooseRandomBorderPoint(self):
        side = random.randint(0,3) # top, right, bottom, left

        if side==0: # top
            print('top')
            self.y = self.room.y
            self.x = self.room.x  + random.randint(0, self.room.w-1)
            self.vector = (0,-1)
        elif side==2: # bottom
            print('bottom')
            self.y = self.room.y + self.room.h - 1
            self.x = self.room.x  + random.randint(0, self.room.w-1)
            self.vector = (0,+1)
        elif side==1: # right
            print('right')
            self.x = self.room.x + self.room.w - 1
            self.y = self.room.y  + random.randint(0, self.room.h-1)
            self.vector = (+1,0)
        elif side==3: # left
            print('left')
            self.x = self.room.x
            self.y = self.room.y + random.randint(0, self.room.h-1)
            self.vector = (-1,0)

    def travel(self):
        self.x += self.vector[0]
        self.y += self.vector[1]

        print(f'newPosition {self.x},{self.y}')
        newRoom = makeRoom(1, 1, symbol="_", roomType='corridor')
        self.map.placeRoom(newRoom, x=self.x, y=self.y)

        self.distanceTravelled += 1

        if self.distanceTravelled >= self.travelDistance:
            return -1
        else:
            return 0

        self.turnProbability = 0.2
        self.travelDistance = 10

    def translate(self, vector):
        self.x += vector[0]
        self.y += vector[1]

class Room:
    def __init__(self, roomArray, x, y, roomType='room'):
        self.roomArray = np.array(roomArray)
        self.x, self.y = x, y # upper left pt
        self.h, self.w = roomArray.shape
        self.roomType = roomType

    def translate(self, vector):
        self.x += vector[0]
        self.y += vector[1]

class Map:
    def __init__(self, initWidth=10, initHeight=10, walker=None):
        self.mapArray = makeRoom(initWidth, initHeight, symbol="#").roomArray
        self.rooms = [] 
        self.width, self.height = initWidth, initHeight
        self.walker = walker

    def renderArray(self):
        self.mapArray = makeRoom(self.width, self.height, symbol="#").roomArray

        for room in self.rooms:
            # There must be a good numpy way to do this.
            for y, row in enumerate(list(room.roomArray)):
                for x, el in enumerate(row):
                    self.mapArray[room.y+y][room.x+x] = el

    def plot(self):
        print('\n')
        for row in self.mapArray:
            print(''.join(row))
        print('\n')

    # Also offset all existing room datas
    # Signs represent directions -- this function cannot shrink map
    def expandMap(self, deltaTuple):
        dx, dy = deltaTuple

        self.width += abs(dx)
        self.height += abs(dy)

        if (dx < 0):
            for i, room in enumerate(self.rooms):
                room.translate((abs(dx),0))
            if self.walker:
                self.walker.translate((-dx,0))
        if (dy < 0):
            for i, room in enumerate(self.rooms):
                room.translate((0,abs(dy)))
            if self.walker:
                self.walker.translate((0, -dy))
            # if (dy > 0):
        #         

    def placeRoom(self, room, x=None, y=None):#, addRoomIndex=True):
        if x:
            room.x = x
        if y:
            room.y = y
        self.rooms.append(room)

        if x < 0:
            print('expand left')
            self.expandMap((-1*abs(x),0))
        if y < 0:
            print('expand up')
            self.expandMap((0, -1*abs(y)))
        if x + room.w > self.width:
            print('expand right')
            self.expandMap((x+room.w-self.width,0))
        if y + room.h > self.height:
            print('expand down')
            self.expandMap((0, y+room.h-self.height))




def makeRoom(width, height, symbol="_", **kwargs):
    mapArray = [[symbol,] * width,]*height
    return Room(np.array(mapArray, dtype=np.str), 0, 0, **kwargs)



if __name__ == "__main__":
    newMap = Map(8,8)

    newRoom = makeRoom(4,4)
    newMap.placeRoom(newRoom, x=2, y=2)

    if 0:
        newRoom = makeRoom(1,1)
        newMap.placeRoom(newRoom, x=-2, y=8)
        newMap.renderArray()
        newMap.plot()

    if 1:
        fred = Walker(newMap, 0)
        newMap.walker = fred
        fred.chooseRandomBorderPoint()
        for i in range(3):
            fred.travel()
        newMap.renderArray()
        fred.render()
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

    
