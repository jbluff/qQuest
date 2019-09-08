
import pygame
import tcod as libtcodpy
import sys

import constants

class struc_Tile:
    def __init__(self, block_path):
        self.block_path = block_path

class obj_Actor:
    def __init__(self, x, y, name, sprite, creature=None, ai=None):

        self.x, self.y = x, y
        self.name = name
        self.sprite = sprite
 
        self.creature = creature
        if self.creature:
            self.creature.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

    def draw(self):
        SURFACE_MAIN.blit(self.sprite, (self.x * constants.CELL_WIDTH,
                                             self.y * constants.CELL_HEIGHT))

class com_Creature:
    def __init__(self, name_instance, hp = 10):

        self.name_instance = name_instance
        self.hp = hp  

    def move(self, dx, dy):
        tile_is_wall = (GAME.current_map[self.owner.x + dx]
                        [self.owner.y + dy].block_path == True)

        #target = map_check_for_creature(self.owner.x + dx,
        #                                self.owner.y + dy,
        #                                self.owner)

        #if target:
        #    self.attack(target)

        if not tile_is_wall:# and target is None:
            self.owner.x += dx
            self.owner.y += dy

class obj_Game:
    def __init__(self):
        self.current_objects = []
        self.message_history = []
        self.current_map = map_create()

def map_create():
    new_map = [[struc_Tile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range(0, constants.MAP_WIDTH)]

    for i in range(constants.MAP_HEIGHT):
        new_map[0][i].block_path = True
        new_map[constants.MAP_WIDTH-1][i].block_path = True
    for i in range(constants.MAP_WIDTH):
        new_map[i][0].block_path = True
        new_map[i][constants.MAP_HEIGHT-1].block_path = True

    new_map[10][10].block_path = True
    new_map[10][15].block_path = True

    return new_map

def draw_map(map_to_draw):
    for x in range(0, constants.MAP_WIDTH):
        for y in range(0, constants.MAP_HEIGHT):
            if map_to_draw[x][y].block_path == True: 
                SURFACE_MAIN.blit(constants.S_WALL, ( x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
            else:
                SURFACE_MAIN.blit(constants.S_FLOOR, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

def draw_game():
    #global SURFACE_MAIN, GAME

    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
    draw_map(GAME.current_map)

    PLAYER.draw()    
    ENEMY.draw()    

    pygame.display.flip()

def game_handle_keys():

    #global FOV_CALCULATE
    # get player input
    keys_list = pygame.key.get_pressed()
    events_list = pygame.event.get()

    # process input
    for event in events_list:
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN:
            # arrow key up -> move player up
            if event.key == pygame.K_UP:
                PLAYER.creature.move(0, -1)
                return "player-moved"

            # arrow key down -> move player down
            if event.key == pygame.K_DOWN:
                PLAYER.creature.move(0, 1)
                return "player-moved"

            # arrow key left -> move player left
            if event.key == pygame.K_LEFT:
                PLAYER.creature.move(-1, 0)
                return "player-moved"

            # arrow key right -> move player right
            if event.key == pygame.K_RIGHT:
                PLAYER.creature.move(1, 0)
                return "player-moved"

    return "no-action"

def game_exit():
    pygame.quit()
    sys.exit()

def game_main_loop():
    quit = False
    player_action = "no-action"
    while not quit:

        player_action = game_handle_keys()

        if player_action == "QUIT":
            quit = True

        draw_game()
    game_exit()

def game_initialize():
    global SURFACE_MAIN, GAME, PLAYER, ENEMY
    pygame.init()

    SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH*constants.CELL_WIDTH,
                                            constants.MAP_HEIGHT*constants.CELL_HEIGHT))

    GAME = obj_Game()
    GAME.current_map = map_create()

    creature_com1 = com_Creature("greg")
    PLAYER = obj_Actor(2, 2, "python", constants.S_PLAYER, creature = creature_com1)

    creature_com2 = com_Creature("jackie")
    ENEMY = obj_Actor(15, 15, "crab", constants.S_ENEMY, creature = creature_com2)

if __name__ == "__main__":


    game_initialize()
    game_main_loop()

    


