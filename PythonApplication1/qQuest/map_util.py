import tcod as libtcod
import json, os

from qQuest import constants

class structTile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False

def loadLevelFile(levelName):
    filePath = os.path.join(os.path.dirname(__file__),"levels",levelName+".lvl")

    with open(filePath, "r") as levelFile:
        levelDict = json.load(levelFile)
    levelFile.close()

    return levelDict

def createMap(levelDict):
    newMap = [[structTile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range(0, constants.MAP_WIDTH)]

    for i in range(constants.MAP_HEIGHT):
        newMap[0][i].blockPath = True
        newMap[constants.MAP_WIDTH-1][i].blockPath = True
    for i in range(constants.MAP_WIDTH):
        newMap[i][0].blockPath = True
        newMap[i][constants.MAP_HEIGHT-1].blockPath = True

    newMap[3][3].blockPath = True
    newMap[5][6].blockPath = True

    return newMap

def createMapOld():
    newMap = [[structTile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range(0, constants.MAP_WIDTH)]

    for i in range(constants.MAP_HEIGHT):
        newMap[0][i].blockPath = True
        newMap[constants.MAP_WIDTH-1][i].blockPath = True
    for i in range(constants.MAP_WIDTH):
        newMap[i][0].blockPath = True
        newMap[i][constants.MAP_HEIGHT-1].blockPath = True

    newMap[3][3].blockPath = True
    newMap[5][6].blockPath = True

    return newMap

def createFovMap(mapIn):
    ''' the index order gets hosed here.  tcod is weird.'''
    fovMap = libtcod.map.Map(width=constants.MAP_WIDTH, height=constants.MAP_HEIGHT)
    for y in range(constants.MAP_HEIGHT):
        for x in range(constants.MAP_WIDTH):
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


    
