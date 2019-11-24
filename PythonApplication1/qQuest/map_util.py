import tcod as libtcod
#import pygame
#import json, os, copy, random
import numpy as np

from qQuest import constants
#from qQuest.qqGlobal import GAME, SURFACE_MAIN

def createFovMap(mapIn):
    ''' the index order gets hosed here.  tcod is weird.
    i have no excuse for this'''

    # ''' the index order gets hosed here.  tcod is weird.'''
    # fovMap = libtcod.map.Map(width=GAME.mapWidth, height=GAME.mapHeight)
    # for y in range(GAME.mapHeight):
    #     for x in range(GAME.mapWidth):
    #         val = mapIn[x][y].blockPath
    #         fovMap.transparent[y][x] = not val
    # return fovMap

    #mapHeight, mapWidth = np.array(mapIn).shape
    mapHeight = len(mapIn)
    mapWidth = len(mapIn[0])
    #print(f'mapIn width={mapWidth} height={mapHeight}')
    #mapWidth, mapHeight = np.array(mapIn).shape


    fovMap = libtcod.map.Map(width=mapWidth, height=mapHeight)#,
    #fovMap = libtcod.map.Map(width=mapHeight, height=mapWidth)
    for y in range(mapHeight):
        for x in range(mapWidth):
            val = mapIn[y][x].blockPath
            #fovMap.transparent[x][y] = not val
            fovMap.transparent[y][x] = not val
            # val = mapIn[x][y].blockPath
            # fovMap.transparent[y][x] = not val

    # printArray = np.zeros((len(mapIn),len(mapIn[0])))
    # for i, row in enumerate(mapIn):
    #     for j, el in enumerate(row):
    #         #printArray[i][j] = int(fovMap.transparent[i][j])
    #         printArray[i][j] = int(mapIn[i][j].blockPath)
    # print("blockpath:")
    # print(printArray)

    # printArray = np.zeros((len(mapIn),len(mapIn[0])))
    # for i, row in enumerate(mapIn):
    #     for j, el in enumerate(row):
    #         printArray[i][j] = int(fovMap.transparent[i][j])
    # print("transparent:")
    # print(printArray)


    return fovMap

def mapCalculateFov(actor):
    ''' the index order gets hosed here.  tcod is weird.'''

    if not actor.fovCalculate:
        return
    #print(actor.fovMap.transparent)
    actor.fovMap.compute_fov(actor.x,actor.y,
                       radius = constants.FOV_RADIUS,
                       light_walls = constants.FOV_LIGHT_WALLS,
                       algorithm = constants.FOV_ALGO)
    actor.fovCalculate = False

