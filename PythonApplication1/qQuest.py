
import pygame
import tcod as libtcod
import random
import numpy as np

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
        global FOV_MAP
        is_visible = FOV_MAP.fov[self.y, self.x]
        if (is_visible):
            SURFACE_MAIN.blit(self.sprite, (self.x * constants.CELL_WIDTH,
                                                 self.y * constants.CELL_HEIGHT))

class com_Creature:
    def __init__(self, name, hp=10, death_function=None):

        self.name = name
        self.hp = hp  
        self.max_hp = hp
        self.death_function = death_function

    def take_damage(self, damage):
        self.hp -= damage
        print(self.name + "'s health is " + str(self.hp) + "/" + str(self.max_hp))

        if self.hp <= 0:
            if self.death_function:
                self.death_function(self.owner)

    def move(self, dx, dy):
        tile_is_wall = (GAME.current_map[self.owner.x + dx]
                        [self.owner.y + dy].block_path == True)

        target = map_check_for_creature(self.owner.x + dx,
                                        self.owner.y + dy,
                                        exclude_object=self.owner)

        if target:
            print(self.name + " attacks " + target.name)
            target.take_damage(3)

        if not tile_is_wall and target is None:
            self.owner.x += dx
            self.owner.y += dy

class ai_Test:
    #def __init__(self):
    #    pass

    def take_turn(self):
        dx = random.randint(-1,1)
        dy = random.randint(-1,1)
        self.owner.creature.move(dx,dy)

def death_monster(monster):
    '''
    Monster is actor class instance
    '''
    print(monster.creature.name + " has been slain!")
    monster.creature = None
    monster.ai = None

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

    new_map[3][3].block_path = True
    new_map[5][6].block_path = True

    map_make_fov(new_map)

    return new_map

def map_check_for_creature(x, y, exclude_object = None):
    '''
    Returns target creature instance if target location contains creature
    '''
    global GAME
    target = None
    for object in GAME.current_objects:
        if (object is not exclude_object and
            object.x == x and
            object.y == y and
            object.creature):
            return object.creature
    return None

def map_make_fov(map_in):
    ''' the index order gets hosed here.  tcod is weird.'''
    global FOV_MAP
    FOV_MAP = libtcod.map.Map(width=constants.MAP_WIDTH, height=constants.MAP_HEIGHT)
    for y in range(constants.MAP_HEIGHT):
        for x in range(constants.MAP_WIDTH):
            val = map_in[x][y].block_path
            FOV_MAP.transparent[y][x] = not val

def map_calculate_fov():
    ''' the index order gets hosed here.  tcod is weird.'''
    global FOV_CALCULATE, FOV_MAP, PLAYER
    if FOV_CALCULATE:
        FOV_CALCULATE = False
        FOV_MAP.compute_fov(PLAYER.x,PLAYER.y,
                            radius = constants.FOV_RADIUS,
                            light_walls = constants.FOV_LIGHT_WALLS,
                            algorithm = constants.FOV_ALGO)

def draw_map(map_to_draw):
    global SURFACE_MAIN, FOV_MAP
    for x in range(0, constants.MAP_WIDTH):
        for y in range(0, constants.MAP_HEIGHT):

            is_visible = FOV_MAP.fov[y, x]
            if is_visible:
                if map_to_draw[x][y].block_path == True: 
                    SURFACE_MAIN.blit(constants.S_WALL, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(constants.S_FLOOR, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
            else:
                if map_to_draw[x][y].block_path == True: 
                    SURFACE_MAIN.blit(constants.S_WALL_DARK, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
                else:
                    SURFACE_MAIN.blit(constants.S_FLOOR_DARK, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))

def draw_game():
    global SURFACE_MAIN, GAME

    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
    draw_map(GAME.current_map)

    for game_obj in GAME.current_objects:
        game_obj.draw()

    pygame.display.flip()

def game_handle_keys():

    global FOV_CALCULATE, PLAYER
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
                FOV_CALCULATE = True
                return "player-moved"

            # arrow key down -> move player down
            if event.key == pygame.K_DOWN:
                PLAYER.creature.move(0, 1)
                FOV_CALCULATE = True
                return "player-moved"

            # arrow key left -> move player left
            if event.key == pygame.K_LEFT:
                PLAYER.creature.move(-1, 0)
                FOV_CALCULATE = True
                return "player-moved"

            # arrow key right -> move player right
            if event.key == pygame.K_RIGHT:
                PLAYER.creature.move(1, 0)
                FOV_CALCULATE = True
                return "player-moved"

    return "no-action"

def game_exit():
    pygame.quit()
    quit()
    #sys.exit()

def game_main_loop():
    global GAME
    quit = False
    
    player_action = "no-action"

    while not quit:
       
        player_action = game_handle_keys()

        map_calculate_fov()

        if player_action == "QUIT":
            quit = True

        elif player_action == "player-moved":
            for game_obj in GAME.current_objects:
                if game_obj.ai:
                    game_obj.ai.take_turn()

        draw_game()
    game_exit()

def game_initialize():
    global SURFACE_MAIN, GAME, PLAYER, FOV_CALCULATE
    pygame.init()

    SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH*constants.CELL_WIDTH,
                                            constants.MAP_HEIGHT*constants.CELL_HEIGHT))

    GAME = obj_Game()
    GAME.current_map = map_create()
    FOV_CALCULATE = True

    creature_com1 = com_Creature("our_hero")
    PLAYER = obj_Actor(2, 2, "python", constants.S_PLAYER, creature = creature_com1)
    GAME.current_objects.append(PLAYER)

    creature_com2 = com_Creature("evil_jelly", death_function=death_monster)
    ai_com = ai_Test()
    enemy = obj_Actor(5, 6, "crab", constants.S_ENEMY, creature = creature_com2, ai=ai_com)
    GAME.current_objects.append(enemy)

if __name__ == "__main__":
    game_initialize()
    game_main_loop()

    


