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

class Walker:
    def __init__(self, mapInst, roomIdx):
        self.map = mapInst
        self.roomIdx = roomIdx
        self.room = self.map.rooms[self.roomIdx]

        self.x, self.y = 0, 0
        self.vector = (1, 0) #x, y

        self.turnProbability = self.map.turnProbability
        self.tunnelLength = random.randint(*self.map.tunnelLengthLimits)

    def render(self):
        self.map.mapArray[self.y][self.x] = "@"

    def chooseRandomBorderPoint(self):
        side = random.randint(0,3) # top, right, bottom, left

        if side==0: # top
            self.y = self.room.y
            self.x = self.room.x  + random.randint(0, self.room.w-1)
            self.vector = (0,-1)
        elif side==2: # bottom
            self.y = self.room.y + self.room.h - 1
            self.x = self.room.x  + random.randint(0, self.room.w-1)
            self.vector = (0,+1)
        elif side==1: # right
            self.x = self.room.x + self.room.w - 1
            self.y = self.room.y  + random.randint(0, self.room.h-1)
            self.vector = (+1,0)
        elif side==3: # left
            self.x = self.room.x
            self.y = self.room.y + random.randint(0, self.room.h-1)
            self.vector = (-1,0)

    def travelOneStep(self):
        self.x += self.vector[0]
        self.y += self.vector[1]

        newRoom = makeRoom(1, 1, symbol="_", roomType='corridor')
        self.map.placeRoom(newRoom, x=self.x, y=self.y)

        #self.distanceTravelled += 1

        # branch!
        self.turn()

    def travel(self, numPts=None):
        if numPts == None:
            numPts = self.tunnelLength
        for i in range(numPts):
            self.travelOneStep()
        
        return (self.x+self.vector[0], self.y+self.vector[1])

    def turn(self):
        if (random.random() < self.turnProbability):
            if random.randint(0,1):
                self.turnLeft()
            else:
                self.turnRight()

    def turnLeft(self):
        if self.vector==(-1,0):
            self.vector = (0,-1)
        elif self.vector==(0,-1):
            self.vector = (1,0)
        elif self.vector==(1,0):
            self.vector = (0,1)
        elif self.vector==(0,1):
            self.vector = (-1,0)

    def turnRight(self):
        if self.vector==(-1,0):
            self.vector = (0,1)
        elif self.vector==(0,1):
            self.vector = (1,0)
        elif self.vector==(1,0):
            self.vector = (0,-1)
        elif self.vector==(0,-1):
            self.vector = (-1,0)

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

        self.turnProbability = 0.2
        self.tunnelLengthLimits = (3, 10)
        self.roomSizeLimits = (3,7)

    def checkRoomOverlaps(self, newRoom):
        overlapInfo = []
        for room in self.rooms:
            xOverlap, yOverlap = False, False
            A, B, C, D = room.x, room.x + room.w - 1, newRoom.x, newRoom.x + newRoom.w - 1
            print(f'{A},{B},{C},{D}')
            if (B >= D and A <= D) or (A <= C and B >= C):
                xOverlap = True

            A, B, C, D = room.y, room.y + room.h - 1, newRoom.y, newRoom.y + newRoom.h - 1
            print(f'{A},{B},{C},{D}')
            if (B >= D and A <= D) or (A <= C and B >= C):
                yOverlap = True
            overlapInfo.append((xOverlap, yOverlap))
        return overlapInfo


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
   

    def placeRoom(self, room, x=None, y=None):#, addRoomIndex=True):
        if x:
            room.x = x
        if y:
            room.y = y

        self.rooms.append(room)

        if room.x < 0:
            self.expandMap((-1*abs(room.x),0))
        if room.y < 0:
            self.expandMap((0, -1*abs(room.y)))
        if room.x + room.w > self.width:
            self.expandMap((room.x+room.w-self.width,0))
        if room.y + room.h > self.height:
            self.expandMap((0,room.y+room.h-self.height))

    def chooseWalkerStart(self):
        roomIdcs = [idx for idx,room in enumerate(self.rooms) if room.roomType=="room"]
        return random.sample(roomIdcs, 1)[0]

    def spawnWalker(self):
        
        startIdx = self.chooseWalkerStart()
        self.walker = Walker(self, startIdx)
        self.walker.chooseRandomBorderPoint()
        x, y = self.walker.travel(10)


        self.walker = None

        roomX = random.randint(*self.roomSizeLimits)
        roomY = random.randint(*self.roomSizeLimits)
        newRoom = makeRoom(roomX, roomY, roomType='room')
        self.placeRoom(newRoom, x=x, y=y)

    def spawnMultipleWalkers(self, n):
        for _ in range(n):
            self.spawnWalker()

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

    if 0:
        #newMap.spawnWalker()
        newMap.spawnMultipleWalkers(20)

        newMap.renderArray()
        newMap.plot()


    if 1:
        newRoom = makeRoom(4,4)
        newRoom.x = 6
        newRoom.y = -2
        print(newMap.checkRoomOverlaps(newRoom))
        newMap.placeRoom(newRoom)#, x=6, y=5)
        newMap.renderArray()
        newMap.plot()
        

    
