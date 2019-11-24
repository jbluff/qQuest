import json, os, copy, random
import numpy as np


class Walker:
    def __init__(self, mapInst, roomIdx):
        self.map = mapInst
        self.roomIdx = roomIdx
        self.room = self.map.mapObjects[self.roomIdx]

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

        newRoom = makeMapObject(1, 1, symbol="_", objectType='corridor')
        success = self.map.placeMapObject(newRoom, x=self.x, y=self.y)
        #print('placed corridor!')
        #self.distanceTravelled += 1

        # branch!
        self.turn()
        return success

    def travel(self, numPts=None):
        #print(f'travelLen{numPts}')
        if numPts == None:
            numPts = self.tunnelLength
        for i in range(numPts):
            success = self.travelOneStep()
            if not success:
                #print(f'failed to travel after {i} steps')
                break
        
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

class MapObject:
    def __init__(self, roomArray, x, y, objectType='room'):
        self.roomArray = np.array(roomArray)
        self.x, self.y = x, y # upper left pt
        self.h, self.w = roomArray.shape
        self.objectType = objectType

    def translate(self, vector):
        self.x += vector[0]
        self.y += vector[1]

class Map:
    def __init__(self, initWidth=10, initHeight=10, walker=None):
        self.mapArray = makeMapObject(initWidth, initHeight, symbol="#").roomArray
        self.mapObjects = [] 
        self.width, self.height = initWidth, initHeight
        self.walker = walker

        self.turnProbability = 0.2
        self.tunnelLengthLimits = (5, 10)
        self.roomSizeLimits = (3,7)

        self.metaDict = {"level" : self.mapArray,
                         "decoderRing" : {
                            "_" : "floor",
                            "#" : "wall"}}

    def checkOverlaps(self, newObj):
        overlapInfo = []
        for mo in self.mapObjects:
            xOverlap, yOverlap = False, False
            A, B, C, D = mo.x, mo.x + mo.w - 1, newObj.x, newObj.x + newObj.w - 1
            #print(f'{A},{B},{C},{D}')
            if (B >= D and A <= D) or (A <= C and B >= C):
                xOverlap = True

            A, B, C, D = mo.y, mo.y + mo.h - 1, newObj.y, newObj.y + newObj.h - 1
            #print(f'{A},{B},{C},{D}')
            if (B >= D and A <= D) or (A <= C and B >= C):
                yOverlap = True
            overlapInfo.append((xOverlap, yOverlap))
        return overlapInfo


    def renderArray(self):
        self.mapArray = makeMapObject(self.width, self.height, symbol="#").roomArray

        roomIdcs = self.getObjTypeIdcs(objType='room')
        corridorIdcs = self.getObjTypeIdcs(objType='corridor')

        otherIdcs = set(range(len(self.mapObjects)))
        otherIdcs.difference_update(set(roomIdcs+corridorIdcs))
        #+set(corridorIdcs))

        # get ordering right here!
        for room in self.mapObjects:
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
            for i, room in enumerate(self.mapObjects):
                room.translate((abs(dx),0))
            if self.walker:
                self.walker.translate((-dx,0))
        if (dy < 0):
            for i, room in enumerate(self.mapObjects):
                room.translate((0,abs(dy)))
            if self.walker:
                self.walker.translate((0, -dy))
   
    def isOverlappingCorridor(self, newObj):
        if newObj.objectType != 'corridor':
            #print(f'wrongtype')
            return False
        overlaps = self.checkOverlaps(newObj)
        completeOverlaps = [x and y for x, y in overlaps]
        if sum(completeOverlaps)>0:
            #print('overlaps')
            return True
        return False

    def isOverlappingRoom(self, room):
        return False

    def placeMapObject(self, mapObj, x=None, y=None):#, addRoomIndex=True):
        if x:
            mapObj.x = x
        if y:
            mapObj.y = y

        success = not self.isOverlappingCorridor(mapObj)
        if not success:
            #print('failed in placeMapObject')
            return False
        #self.isOverlappingRoom(room)

        self.mapObjects.append(mapObj)

        if mapObj.x < 0:
            self.expandMap((-1*abs(mapObj.x),0))
        if mapObj.y < 0:
            self.expandMap((0, -1*abs(mapObj.y)))
        if mapObj.x + mapObj.w > self.width:
            self.expandMap((mapObj.x+mapObj.w-self.width,0))
        if mapObj.y + mapObj.h > self.height:
            self.expandMap((0,mapObj.y+mapObj.h-self.height))
        return True

    def chooseWalkerStart(self):
        roomIdcs = [idx for idx,mo in enumerate(self.mapObjects) if mo.objectType=="room"]
        return random.sample(roomIdcs, 1)[0]

    def spawnWalker(self):
        
        startIdx = self.chooseWalkerStart()
        self.walker = Walker(self, startIdx)
        self.walker.chooseRandomBorderPoint()
        x, y = self.walker.travel(10) #this should be a random length
        self.walker = None

        roomX = random.randint(*self.roomSizeLimits)
        roomY = random.randint(*self.roomSizeLimits)
        newRoom = makeMapObject(roomX, roomY, objectType='room')
        success = self.placeMapObject(newRoom, x=x, y=y)

    def spawnMultipleWalkers(self, n):
        for _ in range(n):
            success = self.spawnWalker()

    def closeMapEdges(self):
        self.expandMap((-1,-1))
        self.expandMap((1,1))

    def getObjTypeIdcs(self, objType='room'):
        return [ x for (x,room) in enumerate(self.mapObjects) if room.objectType == objType]

    def addEntity(self, symbol, name, rmIdx=None):
        if rmIdx is None:
            roomIdcs = self.getObjTypeIdcs(objType='room')
            roomIdcs = roomIdcs[1:]
            rmIdx = random.sample(roomIdcs, 1)[0]
            print(rmIdx)

        room = self.mapObjects[rmIdx]
        posX = room.x + random.randint(0, room.w-1)
        posY = room.y + random.randint(0, room.h-1)

        # TODO -- check whether we're going to overwrite an existing thing.
        entity = makeMapObject(1,1,symbol=symbol, objectType='entity')
        self.placeMapObject(entity, x=posX, y=posY)

        self.metaDict['decoderRing'][symbol] = name

    def saveMap(self, fname):
        self.metaDict['level'] = self.mapArray.tolist()
        #print(self.metaDict)

        filePath = os.path.join(os.path.dirname(__file__),"..","levels",fname+".lvl")
        print(filePath)
        with open(filePath, "w") as data_file:
            json.dump(self.metaDict, data_file)
        data_file.close()

def makeMapObject(width, height, symbol="_", **kwargs):
    mapArray = [[symbol,] * width,]*height
    return MapObject(np.array(mapArray, dtype=np.str), 0, 0, **kwargs)




if __name__ == "__main__":
    newMap = Map(8,8)

    newRoom = makeMapObject(4,4)
    
    newMap.placeMapObject(newRoom, x=2, y=2)

    if 1:
        #newRoom = makeMapObject(1,1)
        #newMap.placeMapObject(newRoom, x=-2, y=8)
        newMap.spawnWalker()
        newMap.addEntity('p', 'player', rmIdx=0)
        newMap.renderArray()
        newMap.plot()
        newMap.saveMap("testMap")

    if 0:
        #newMap.spawnWalker()
        newMap.spawnMultipleWalkers(20)
        newMap.closeMapEdges()

        newMap.addEntity('p', 'player', rmIdx=0)
        newMap.renderArray()
        newMap.plot()



        mapList = newMap.mapArray.tolist()
        print(type(mapList))
        

        filePath = os.path.join(os.path.dirname(__file__),"newMap1.lvl")
        print(filePath)
        with open(filePath, "w") as data_file:
            json.dump(self.metaDict, data_file)
        data_file.close()


    if 0:
        newRoom = makeMapObject(4,4)
        newRoom.x = 6
        newRoom.y = -2
        print(newMap.checkRoomOverlaps(newRoom))
        newMap.placeMapObject(newRoom)#, x=6, y=5)
        newMap.renderArray()
        newMap.plot()
        

    if 0:
        newMap.spawnMultipleWalkers(20)
        newMap.closeMapEdges()
        newMap.renderArray()
        newMap.plot()
        newMap.addEntity('p', 'player', rmIdx=0)
        newMap.addEntity('h', 'healingPotion', rmIdx=0)
        newMap.addEntity('h', 'healingPotion')
        newMap.addEntity('h', 'healingPotion')
        newMap.addEntity('h', 'healingPotion')
        newMap.addEntity('g', 'goggles')
        newMap.addEntity('g', 'goggles')
        newMap.addEntity('g', 'goggles')
        #for _ in range(10):
        #    newMap.addEntity('e', 'enemy')
        newMap.renderArray()
        newMap.plot()

        #newMap.mapArray = list(newMap.mapArray)

        newMap.saveMap("mapwPG")
    
