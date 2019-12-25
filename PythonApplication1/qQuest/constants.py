import pygame
pygame.init()

#MAP_WIDTH = 30
#MAP_HEIGHT = 20

''' width of a game tile, in pixels '''
CELL_WIDTH = 16
CELL_HEIGHT = 16


CAMERA_WIDTH =  30# 20 # in cells
CAMERA_HEIGHT = 20# 15 # in cells

CHYRON_HEIGHT = 6 # in cells.

CAMERA_WIDTH_P = CAMERA_WIDTH*CELL_WIDTH
CAMERA_HEIGHT_P = CAMERA_HEIGHT*CELL_HEIGHT
CHYRON_HEIGHT_P = CHYRON_HEIGHT*CELL_HEIGHT
TOTAL_WIDTH_P = CAMERA_WIDTH_P
TOTAL_HEIGHT_P = CAMERA_HEIGHT_P+CHYRON_HEIGHT_P

''' Color definitions '''
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (100, 100, 100)
COLOR_DGREY = (50, 50, 50)
COLOR_DARKERGREY = (25, 25, 25)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)


COLOR_DEFAULT_BG = COLOR_GREY

''' Fonts '''
#TODO:  change to pygame.font.match_font(), remove fonts folder
FONT_CONSOLA = pygame.font.Font(pygame.font.match_font('consola'), 14)
FONT_DEBUG = FONT_CONSOLA


''' FOV stuff '''
import tcod as libtcod
FOV_ALGO = libtcod.FOV_BASIC  # Algorithm for FOV Calculation
FOV_LIGHT_WALLS = True        # Does the FOV shine on the walls?
FOV_RADIUS = 10             # Sight radius for FOV

''' message window stuff '''
NUM_GAME_MESSAGES = 4

GAME_FPS = 60



from collections import namedtuple
# this shouldn't really be here.  to be fixed.
# yes, I know it's not a dict.  Deal with it.
# this construction is used for hashability & memoization.
SpriteDict = namedtuple('SpriteDict',['path', 'colIdx', 'rowIdx', 'numSprites'])
