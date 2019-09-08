
MAP_WIDTH = 20
MAP_HEIGHT = 20

CELL_WIDTH = 16
CELL_HEIGHT = 16

# Color definitions
COLOR_BLACK = (0, 0, 0)  # RGB for black
COLOR_WHITE = (255, 255, 255)  # RGB for white
COLOR_GREY = (100, 100, 100)

# Game colors
COLOR_DEFAULT_BG = COLOR_GREY

import pygame
S_PLAYER = pygame.image.load('16x16figs/player.png')
S_WALL = pygame.image.load('16x16figs/wall.png')
S_FLOOR = pygame.image.load('16x16figs/floor.png')
S_ENEMY = pygame.image.load('16x16figs/jelly.png')