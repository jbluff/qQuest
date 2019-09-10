import pygame
pygame.init()

MAP_WIDTH = 30
MAP_HEIGHT = 20

CELL_WIDTH = 16
CELL_HEIGHT = 16

''' Color definitions '''
COLOR_BLACK = (0, 0, 0)  # RGB for black
COLOR_WHITE = (255, 255, 255)  # RGB for white
COLOR_GREY = (100, 100, 100)

# Game colors
COLOR_DEFAULT_BG = COLOR_GREY

''' Fonts '''
#TODO:  change to pygame.font.match_font(), remove fonts folder
FONT_CONSOLA = pygame.font.Font('fonts/consola.ttf', 14)
FONT_DEBUG = FONT_CONSOLA

''' Sprites '''
S_PLAYER = pygame.image.load('16x16figs/player.png')
S_ENEMY = pygame.image.load('16x16figs/jelly.png')
S_WALL = pygame.image.load('16x16figs/wall.png')
S_FLOOR = pygame.image.load('16x16figs/floor.png')
S_WALL_DARK = pygame.image.load('16x16figs/wall_dark.png')
S_FLOOR_DARK = pygame.image.load('16x16figs/floor_dark.png')

''' FOV stuff '''
import tcod as libtcod
FOV_ALGO = libtcod.FOV_BASIC  # Algorithm for FOV Calculation
FOV_LIGHT_WALLS = True        # Does the FOV shine on the walls?
FOV_RADIUS = 10             # Sight radius for FOV