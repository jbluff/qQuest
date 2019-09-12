import tcod as libtcod

import constants

class structTile:
    def __init__(self, blockPath):
        self.blockPath = blockPath
        self.explored = False

def mapCreate():
    newMap = [[structTile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range(0, constants.MAP_WIDTH)]

    for i in range(constants.MAP_HEIGHT):
        newMap[0][i].blockPath = True
        newMap[constants.MAP_WIDTH-1][i].blockPath = True
    for i in range(constants.MAP_WIDTH):
        newMap[i][0].blockPath = True
        newMap[i][constants.MAP_HEIGHT-1].blockPath = True

    newMap[3][3].blockPath = True
    newMap[5][6].blockPath = True

    fovMap = mapMakeFov(newMap)

    return newMap, fovMap

def mapMakeFov(mapIn):
    ''' the index order gets hosed here.  tcod is weird.'''
    fovMap = libtcod.map.Map(width=constants.MAP_WIDTH, height=constants.MAP_HEIGHT)
    for y in range(constants.MAP_HEIGHT):
        for x in range(constants.MAP_WIDTH):
            val = mapIn[x][y].blockPath
            fovMap.transparent[y][x] = not val
    return fovMap

def mapCalculateFov(doCalculate=0, player=None, fovMap=None):
    ''' the index order gets hosed here.  tcod is weird.'''
    if not doCalculate:
        return

    fovMap.compute_fov(player.x,player.y,
                       radius = constants.FOV_RADIUS,
                       light_walls = constants.FOV_LIGHT_WALLS,
                       algorithm = constants.FOV_ALGO)


    
