import pygame
import math
from pygame.locals import *
import numpy as np
import random

random.seed()

CWIDTH = 16
CHEIGHT = 16
STATE_CHASE = 0
STATE_SHOP = 1
STATE_FLEE = 2
STATE_REVIVE = 3

RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3

c_white = (255, 255, 255)
c_black = (0, 0, 0)
c_blue = (30, 30, 255)
c_red = (255, 30, 30)
c_orange = (255, 120, 120)
c_dkorange = (180, 100, 100)
c_pink = (255, 200, 200)
c_yellow = (255, 255, 0)
c_dkblue = (0, 0, 120)
c_ltblue = (120, 120, 255)


class Game:
    path_grid = []
    instance_list = []
    window = None
    window_created = False

    def __init__(self, grid_source):
        f = open(grid_source, "r")
        f_read = f.readlines()
        # get initial width
        line_sample = f_read[0]
        w = len(line_sample) - 1  # subtract 1 for newline
        h: int = len(f_read)
        f.close()
        self.path_grid = Grid(w, h)
        self.pacman = None
        self.ghosts = []
        self.game_over = False
        self.game_over_timer = 0
        self.ending = False
        self.end_timer = 0
        self.game_over_object = None
        self.font = pygame.font.SysFont('couriernew', 24)
        self.bigfont = pygame.font.SysFont('couriernew', 48)
        self.main_menu = False
        self.main_menu_object = None
        self.highscores = False
        self.highscore_object = None
        self.window_width = w * CWIDTH
        self.window_height = h * CHEIGHT
        self.score = 0
        self.score_text = self.font.render("0", True, c_white)
        self.score_indicator = self.font.render("SCORE", True, c_white)
        self.pellets_collected = 0
        self.pacman_pos = None

    def start(self, grid_source):
        if self.main_menu_object is not None:
            del self.main_menu_object
        f = open(grid_source, "r")
        f_read = f.readlines()
        # get initial width
        line_sample = f_read[0]
        w = len(line_sample)-1  # subtract 1 for newline
        h: int = len(f_read)
        self.path_grid = Grid(w, h)
        self.pacman = None
        self.ghosts = []
        self.game_over = False
        self.game_over_timer = 0
        self.ending = False
        self.end_timer = 0
        self.main_menu = False
        self.main_menu_object = None
        self.highscores = False
        self.highscore_object = None
        self.pellets_collected = 0
        self.pacman_pos = None
        for j in range(h):
            line = f_read[j]
            for i in range(w):
                if len(line) <= i:
                    char = ' '
                else:
                    char = line[i]
                if char is 'X' or char is '#':
                    self.path_grid.setval(i, j, -1)
                    if char is 'X':
                        instance_create(Wall(i * CWIDTH, j * CHEIGHT), self.instance_list)
                else:
                    self.path_grid.setval(i, j, 1)
                    if char is '.':
                        instance_create(Pellet(i * CWIDTH + CWIDTH/2, j * CHEIGHT + CHEIGHT/2), self.instance_list)
                    elif char is 'o':
                        instance_create(PowerPellet(i * CWIDTH + CWIDTH/2, j * CHEIGHT + CHEIGHT/2), self.instance_list)
                    elif char is '=':
                        instance_create(SpawnBarrier(i * CWIDTH, j * CHEIGHT),
                                        self.instance_list)
                    elif char is 'N':
                        self.ghosts.append(instance_create(Pinky(i * CWIDTH + CWIDTH/2, j * CHEIGHT + CHEIGHT/2),
                                                           self.instance_list))
                    elif char is 'B':
                        self.ghosts.append(instance_create(Blinky(i * CWIDTH + CWIDTH / 2, j * CHEIGHT + CHEIGHT / 2),
                                                           self.instance_list))
                    elif char is 'I':
                        self.ghosts.append(instance_create(Inky(i * CWIDTH + CWIDTH / 2, j * CHEIGHT + CHEIGHT / 2),
                                                           self.instance_list))
                    elif char is 'C':
                        self.ghosts.append(instance_create(Clyde(i * CWIDTH + CWIDTH / 2, j * CHEIGHT + CHEIGHT / 2),
                                                           self.instance_list))
                    elif char is 'P':
                        self.pacman_pos = (i * CWIDTH, j * CHEIGHT + CHEIGHT/2)
        if self.pacman_pos is not None:
            self.pacman = instance_create(Pacman(self.pacman_pos[0], self.pacman_pos[1]), self.instance_list)
        # self.path_grid.print_grid()
        f.close()
        pygame.mixer_music.stop()

    def update(self):
        for inst in self.instance_list:
            inst.update(self)
        if self.pellets_collected == 30:
            self.pellets_collected = 0
            instance_create(Fruit(self.pacman_pos[0], self.pacman_pos[1]), self.instance_list)
        self.game_over_timer = max(self.game_over_timer-1, 0)
        self.end_timer = max(self.end_timer-1, 0)
        if self.game_over and self.game_over_timer <= 0:
            del self.game_over_object
            self.game_over_object = None
            self.game_over = False
            self.main_menu = True
            self.show_highscores()
            print("transitioning from game over")
        if self.ending and self.end_timer <= 0:
            self.end()
        if self.main_menu_object is not None:
            self.main_menu_object.update(self)
        if self.highscore_object is not None:
            self.highscore_object.update(self)

    def draw(self):
        for inst in self.instance_list:
            inst.draw(self)
        if self.game_over_object is not None:
            self.game_over_object.draw(self)
        if self.main_menu_object is not None:
            self.main_menu_object.draw(self)
        if self.highscore_object is not None:
            self.highscore_object.draw(self)
        if self.game_over_object is None and self.main_menu_object is None and self.highscore_object is None:
            self.window.blit(self.score_indicator, (self.window_width / 2, 5))
            self.window.blit(self.score_text, (self.window_width - self.score_text.get_width() - 5, 5))

    def get_grid(self):
        return self.path_grid

    def get_pacman(self):
        return self.pacman

    def get_ghosts(self):
        return self.ghosts

    def end(self):
        for i in range(len(self.instance_list)):
            # print(i, '/', len(self.instance_list))
            del self.instance_list[0]
        self.game_over = True
        self.game_over_timer = 5000
        del self.path_grid
        self.path_grid = []
        self.ghosts.clear()
        self.pacman = None
        self.ending = False
        self.show_game_over()
        write_to_highscores(self.score)
        self.score = 0

    def show_game_over(self):
        self.game_over_object = GameOver(self)

    def show_main_menu(self):
        self.main_menu_object = MainMenu(self)
        pygame.mixer_music.load('theme.mp3')
        pygame.mixer_music.play(-1)

    def show_highscores(self):
        self.highscore_object = Highscore(self)
        pygame.mixer_music.stop()

    def add_score(self, amount):
        self.score += amount
        self.score_text = self.font.render(str(self.score), True, c_white)


class GameOver:

    def __init__(self, game):
        self.text = game.font.render("GAME OVER", True, c_white)

    def draw(self, game):
        game.window.blit(self.text, (game.window_width / 2 - self.text.get_width()/2,
                                     game.window_height / 2 - self.text.get_height()/2))


class MainMenu:

    def __init__(self, game):
        self.title = game.bigfont.render("PACMAN PORTAL", True, c_white)
        self.start = game.font.render("PLAY", True, c_white)
        self.hs = game.font.render("HIGH SCORES", True, c_white)
        self.chase_state = 0
        self.chase_x = -300
        self.ghosts = [('s_blinky_r1.png', 's_inky_r1.png', 's_pinky_r1.png'),
                       ('s_blinky_r2.png', 's_inky_r2.png', 's_pinky_r2.png')]
        self.vulnghosts = ['s_ghost_vuln1.png', 's_ghost_vuln2.png']
        self.image_index = 0
        self.pacman_arc_offset = 0
        self.pacman_arc_increasing = True
        self.selection = 0
        self.inky_text = game.font.render("INKY", True, c_ltblue)
        self.pinky_text = game.font.render("PINKY", True, c_pink)
        self.blinky_text = game.font.render("BLINKY", True, c_red)
        self.clyde_text = game.font.render("CLYDE", True, c_orange)
        self.inky_sprite = pygame.image.load('s_inky_l2.png')
        self.pinky_sprite = pygame.image.load('s_pinky_u1.png')
        self.blinky_sprite = pygame.image.load('s_blinky_d2.png')
        self.clyde_sprite = pygame.image.load('s_blinky_r1.png')
        self.chase_timer = 0
        self.selection_timer = 0
        self.delay_timer = 200

    def update(self, game):
        self.delay_timer -= 1
        self.selection_timer = max(self.selection_timer-1, 0)
        keys = pygame.key.get_pressed()
        if keys[K_UP] == 1 or keys[K_DOWN] == 1 or keys[K_w] == 1 or keys[K_s] == 1:
            if self.selection_timer == 0:
                self.selection = (self.selection+1) % 2
                self.selection_timer = 100
        if self.delay_timer <= 0 and keys[K_RETURN] == 1:
            if self.selection == 0:
                game.score = 0
                game.start('pacman_grid.txt')
            else:
                # open highscores
                game.show_highscores()
                del game.main_menu_object
                game.main_menu_object = None
        if self.chase_state == 0:
            self.chase_x += 0.1
            if self.chase_x > 500:
                self.chase_state = 1
        elif self.chase_state == 1:
            self.chase_x -= 0.1
            if self.chase_x < -100:
                self.chase_state = 2
                self.chase_timer = 10000
        elif self.chase_state == 2:
            self.chase_timer -= 1
            if self.chase_timer <= 0:
                self.chase_state = 0

        if self.pacman_arc_increasing:
            self.pacman_arc_offset += math.pi/256
            if self.pacman_arc_offset >= math.pi/4:
                self.pacman_arc_increasing = False
        else:
            self.pacman_arc_offset -= math.pi/256
            if self.pacman_arc_offset <= 0:
                self.pacman_arc_increasing = True

    def draw(self, game):
        game.window.blit(self.title, (game.window_width / 2 - self.title.get_width() / 2,
                                      game.window_height / 4 - self.title.get_height() / 2))
        ty = game.window_height * 9/12 - self.start.get_height()/2 - 10
        if self.selection == 1:
            ty += game.window_height/12
        h = self.start.get_height() + 20
        pygame.draw.rect(game.window, (40, 40, 40), (game.window_width/3, ty, game.window_width/3, h))
        game.window.blit(self.start, (game.window_width / 2 - self.start.get_width() / 2,
                                      game.window_height * 9 / 12 - self.start.get_height() / 2))
        game.window.blit(self.hs, (game.window_width / 2 - self.hs.get_width() / 2,
                                   game.window_height * 5 / 6 - self.hs.get_height() / 2))
        if self.chase_state == 0:
            self.image_index += 0.01
            if self.image_index >= len(self.ghosts):
                self.image_index = 0
            for i in range(3):
                img = pygame.image.load(self.ghosts[math.floor(self.image_index)][i])
                game.window.blit(img, (self.chase_x + i * (CWIDTH+4), game.window_height/2))
            if self.pacman_arc_offset == 0:
                pygame.draw.circle(game.window, c_yellow, (int(self.chase_x) + CWIDTH*5,
                                                           int(game.window_height/2) + 2), 8)
            else:
                pygame.draw.arc(game.window, c_yellow, (int(self.chase_x) + CWIDTH*5, game.window_height/2 + 2, 16, 16),
                                self.pacman_arc_offset, -self.pacman_arc_offset, 8)

        elif self.chase_state == 1:
            self.image_index += 0.01
            if self.image_index >= len(self.vulnghosts):
                self.image_index = 0
            for i in range(3):
                img = pygame.image.load(self.vulnghosts[math.floor(self.image_index)])
                game.window.blit(img, (self.chase_x - (i+1) * (CWIDTH+4), game.window_height/2))
            if self.pacman_arc_offset == 0:
                pygame.draw.circle(game.window, c_yellow, (int(self.chase_x),
                                                           int(game.window_height/2) + 2), 8)
            else:
                pygame.draw.arc(game.window, c_yellow, (int(self.chase_x), game.window_height/2 + 2, 16, 16),
                                self.pacman_arc_offset + math.pi, -self.pacman_arc_offset + math.pi, 8)
        elif self.chase_state == 2:
            game.window.blit(self.inky_sprite, (game.window_width/4, game.window_height*2/5))
            game.window.blit(self.inky_text, (game.window_width/4 + 24, game.window_height*2/5-5))
            game.window.blit(self.pinky_sprite, (game.window_width/2, game.window_height*2/5))
            game.window.blit(self.pinky_text, (game.window_width/2 + 24, game.window_height*2/5-5))
            game.window.blit(self.blinky_sprite, (game.window_width/4, game.window_height*3/5))
            game.window.blit(self.blinky_text, (game.window_width/4 + 24, game.window_height*3/5-5))
            game.window.blit(self.clyde_sprite, (game.window_width/2, game.window_height*3/5))
            game.window.blit(self.clyde_text, (game.window_width/2 + 24, game.window_height*3/5-5))


class Highscore:

    def __init__(self, game):
        f = open('highscores.txt', 'r')
        text = f.readlines()
        self.scorelist = []
        f.close()
        num = 0
        newtext = ""
        for line in text:
            r = range(len(line)-1)
            if num == len(text)-1:
                r = range(len(line))
            for i in r:
                newtext += line[i]
            if num % 2 == 0:
                newtext += "      "
            else:
                self.scorelist.append(game.font.render(newtext, True, c_white))
                newtext = ""
            num += 1
        self.title = game.font.render("HIGHSCORES", True, c_white)
        self.delay_timer = 200

    def update(self, game):
        self.delay_timer -= 1
        if self.delay_timer <= 0:
            for key in pygame.key.get_pressed():
                if key == 1:
                    game.show_main_menu()
                    del game.highscore_object
                    game.highscore_object = None

    def draw(self, game):
        game.window.blit(self.title, (game.window_width/2 - self.title.get_width()/2,
                                      game.window_height/4 - self.title.get_height()/2))
        offset = 0
        for img in self.scorelist:
            game.window.blit(img, (game.window_width/2 - img.get_width()/2,
                                   game.window_height/2 - img.get_height()*2/5 + offset))
            offset += 32


class Grid:
    _grid = []
    _width = 0
    _height = 0

    def __init__(self, width, height):
        self._grid = [0] * height
        for i in range(height):
            self._grid[i] = [0] * width
        self._width = width
        self._height = height

    def print_grid(self):
        for row in self._grid:
            print(row)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def setval(self, x, y, val):
        # print('setting ', x, ',', y, ' to ', val)
        self._grid[y][x] = val

    def getval(self, x, y):
        return self._grid[y][x]


class Node:
    _f = 9999
    _g = 9999
    _xpos = -1
    _ypos = -1
    _prev = None

    def __init__(self, x, y):
        self._xpos = x
        self._ypos = y

    def get_x(self):
        return self._xpos

    def get_y(self):
        return self._ypos

    def get_f(self):
        return self._f

    def get_g(self):
        return self._g

    def previous(self):
        return self._prev

    def set_cost(self, previous_node, xgoal, ygoal):
        new_f = previous_node.get_f() + 1
        new_g = np.sqrt(np.abs(xgoal - self._xpos)**2 + np.abs(ygoal - self._ypos)**2)
        if new_f + new_g < self._f + self._g:
            self._f = new_f
            self._g = new_g
            self._prev = previous_node

    def get_cost(self):
        return self._f + self._g

    def initialize_node(self, xgoal, ygoal):
        self._f = 0
        self._g = np.sqrt(np.abs(xgoal - self._xpos) ** 2 + np.abs(ygoal - self._ypos) ** 2)


class Path:
    _len = 0
    _nodes = []

    def clear(self):
        self._nodes = []

    def get_next(self):
        if len(self._nodes) is 0:
            return None
        else:
            ret = self._nodes[0]
            ret[0] = ret[0] * CWIDTH + CWIDTH/2
            ret[1] = ret[1] * CHEIGHT + CHEIGHT/2
            return ret

    def length(self):
        return len(self._nodes)

    def pop_front(self):
        if len(self._nodes) is 0:
            return None
        else:
            return self._nodes.pop(0)

    # A* pathfinding implementation
    def path_create(self, grid, xstart, ystart, xgoal, ygoal):
        self.clear()
        if xstart is xgoal and ystart is ygoal:
            # print('Path creation failed: Already at destination')
            # already at goal
            return True
        if grid.getval(xgoal, ygoal) < 0:
            # print('Path creation failed: Destination nonpathable')
            # goal unreachable
            return False
        # initialize map
        node_map = []
        for j in range(grid.height()):
            row = []
            for i in range(grid.width()):
                row.append(Node(i, j))
            node_map.append(row)
        open_list = [node_map[ystart][xstart]]
        closed_list = []
        open_list[0].initialize_node(xgoal, ygoal)
        success = False
        steps = 0
        # print('BEGINNING PATH; GOAL: ', xgoal, ', ', ygoal)
        while len(open_list) > 0:
            """
            print_string = "["
            for node in open_list:
                print_string += "(" + str(node.get_x()) + ", " + str(node.get_y()) + ") "
            print_string += "]"
            print(print_string)
            """
            current = open_list[0]
            closed_list.append(open_list.pop(0))
            cx = current.get_x()
            cy = current.get_y()
            if cx == xgoal and cy == ygoal:
                success = True
                break
            new_nodes = []
            if cy > 0:
                new_nodes.append(node_map[cy-1][cx])
            if cy < len(node_map)-1:
                new_nodes.append(node_map[cy+1][cx])
            if cx > 0:
                new_nodes.append(node_map[cy][cx-1])
            if cx < len(node_map[0])-1:
                new_nodes.append(node_map[cy][cx+1])
            for n in new_nodes:
                if n not in closed_list and n not in open_list:
                    if grid.getval(n.get_x(), n.get_y()) >= 0:
                        n.set_cost(current, xgoal, ygoal)
                        index = 0
                        for i in open_list:
                            # print('comparing ', n.get_cost(), ' to ', i.get_cost())
                            if n.get_cost() < i.get_cost():
                                break
                            index += 1
                        if index >= len(open_list):
                            open_list.append(n)
                        else:
                            open_list.insert(index, n)
                    else:
                        closed_list.append(n)
            steps += 1
        if success is False:
            # print('Path creation failed in ', steps, ' steps.')
            return False  # path failed to create
        # print('Path created in ', steps, ' steps!')
        node = node_map[ygoal][xgoal]
        new_path = [[xgoal, ygoal]]
        while node.previous() is not None:
            new_path.insert(0, [node.previous().get_x(), node.previous().get_y()])
            node = node.previous()
        self._nodes = new_path
        return True

    def get_path(self):
        return self._nodes


class Actor:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawnpoint = [self.x, self.y]
        self.xprevious = self.x
        self.yprevious = self.y
        self.movement_progress = 0

    def draw(self, game):
        pass

    def update(self, game):
        pass

    def is_centered(self):
        return self.x % 16 == 8 and self.y % 16 == 8

    """
    def get_bbox(self):
        spr_left = self.x - self.sprite.xoffset
        spr_top = self.x - self.sprite.yoffset
        return spr_left, spr_top, spr_left + self.sprite.width, spr_top + self.sprite.height

    def in_collision(self, other):
        me = self.get_bbox()
        oth = other.get_bbox()
        if True:
            return True
        return False
    """


class Pacman(Actor):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.arc_offset = 0
        self.arc_offset_increasing = True
        self.moving = False
        self.dir = RIGHT
        self.dying = False
        self.num_portals = 0
        self.portal_ball_active = False
        self.next_portal_color = c_blue
        self.portal1 = None
        self.portal2 = None
        self.snd_waka = pygame.mixer.Sound('pacman_waka.ogg')
        self.waka_timer = 0
        self.snd_death = pygame.mixer.Sound('pacman_death.ogg')
        self.snd_shootportal = pygame.mixer.Sound('portal_fire.wav')
        self.snd_teleport = pygame.mixer.Sound('portal_transport.wav')

    def update(self, game):
        # reset our x and y to int just in case
        self.x = int(self.x)
        self.y = int(self.y)

        # timers
        self.waka_timer = max(self.waka_timer - 1, 0)

        # update arc
        if self.moving is True and self.dying is False:
            if self.arc_offset_increasing:
                self.arc_offset += math.pi/256
                if self.arc_offset >= math.pi/4:
                    self.arc_offset_increasing = False
            else:
                self.arc_offset -= math.pi/256
                if self.arc_offset <= 0:
                    self.arc_offset_increasing = True

        elif self.dying is True:
            self.dir = 0
            self.arc_offset += math.pi/256

        # movement
        if not self.dying:
            if not self.moving or (self.x % CWIDTH is 8 and self.y % CHEIGHT is 8):
                current_direction = self.dir
                start_moving = self.moving
                keys = pygame.key.get_pressed()
                if keys[K_a] or keys[K_LEFT]:
                    self.moving = True
                    self.dir = LEFT
                elif keys[K_d] or keys[K_RIGHT]:
                    self.moving = True
                    self.dir = RIGHT
                elif keys[K_w] or keys[K_UP]:
                    self.moving = True
                    self.dir = UP
                elif keys[K_s] or keys[K_DOWN]:
                    self.moving = True
                    self.dir = DOWN
                if self.dir is not current_direction:
                    spawn_barriers = []
                    ports = []
                    if self.portal1 is not None:
                        ports.append(self.portal1)
                    if self.portal2 is not None:
                        ports.append(self.portal2)
                    for p in ports:
                        game.get_grid().setval(math.floor(p.x / CWIDTH), math.floor(p.y / CHEIGHT), 1)
                    for inst in game.instance_list:
                        if isinstance(inst, SpawnBarrier):
                            game.get_grid().setval(math.floor(inst.x / CWIDTH), math.floor(inst.y / CHEIGHT), -1)
                            spawn_barriers.append(inst)
                    if get_grid_adjacent(game.get_grid(), self.x, self.y, self.dir) < 0:
                        if self.dir == current_direction:
                            self.moving = False
                        else:
                            self.dir = current_direction
                            self.moving = start_moving
                    for sb in spawn_barriers:
                        game.get_grid().setval(math.floor(sb.x / CWIDTH), math.floor(sb.y / CHEIGHT), 1)
                    for p in ports:
                        game.get_grid().setval(math.floor(p.x / CWIDTH), math.floor(p.y / CHEIGHT), -1)

            if self.x % CWIDTH is 8 and self.y % CHEIGHT is 8:
                can_access = get_grid_adjacent(game.get_grid(), self.x, self.y, self.dir)
                if self.portal1 is not None and self.portal2 is not None and\
                    (dist((self.portal1.x, self.portal1.y), (self.x, self.y)) <= 8 or
                        dist((self.portal2.x, self.portal2.y), (self.x, self.y))):
                    can_access = 1
                if can_access < 0:
                    self.moving = False

            if self.moving:
                # screen wrap
                if self.x <= -CWIDTH/2:
                    self.x = game.get_grid().width() * CWIDTH + CWIDTH/2 - 1
                elif self.x >= game.get_grid().width() * CWIDTH + CWIDTH/2:
                    self.x = -CWIDTH/2 + 1
                if self.waka_timer == 0:
                    self.snd_waka.play()
                    self.waka_timer = 80
                self.movement_progress += 0.51
                if self.movement_progress >= 1:
                    self.movement_progress -= 1
                    if self.dir is RIGHT:
                        self.x += 1
                    elif self.dir is LEFT:
                        self.x -= 1
                    elif self.dir is UP:
                        self.y -= 1
                    elif self.dir is DOWN:
                        self.y += 1

                    # check if we're in a portal
                    if self.portal1 is not None and self.portal2 is not None and\
                            ((self.x == self.portal1.x and self.y == self.portal1.y) or
                                (self.x == self.portal2.x and self.y == self.portal2.y)):
                        if self.x == self.portal1.x:
                            self.x, self.y = self.portal2.x, self.portal2.y
                            self.dir = (self.portal2.dir + 2) % 4
                        else:
                            self.x, self.y = self.portal1.x, self.portal1.y
                            self.dir = (self.portal1.dir + 2) % 4
                        self.snd_teleport.play()
                        # portals are one-use-only
                        self.portal1.snd_close.play()
                        for i in range(len(game.instance_list)):
                            if game.instance_list[i] == self.portal1:
                                del game.instance_list[i]
                                self.portal1 = None
                                break
                            elif game.instance_list[i] == self.portal2:
                                del game.instance_list[i]
                                self.portal2 = None
                                break
                        for i in range(len(game.instance_list)):
                            if game.instance_list[i] == self.portal1:
                                del game.instance_list[i]
                                self.portal1 = None
                                break
                            elif game.instance_list[i] == self.portal2:
                                del game.instance_list[i]
                                self.portal2 = None
                                break

            # eat pellets, fruit, etc.
            if self.moving and self.is_centered():
                for inst in game.instance_list:
                    if isinstance(inst, Pellet):
                        if inst.x == self.x and inst.y == self.y:
                            game.add_score(10)
                            game.instance_list.remove(inst)
                            del inst
                            game.pellets_collected += 1
                    elif isinstance(inst, PowerPellet):
                        if inst.x == self.x and inst.y == self.y:
                            game.add_score(100)
                            game.instance_list.remove(inst)
                            del inst
                            for _inst in game.get_ghosts():
                                # if isinstance(_inst, Clyde) or isinstance(_inst, Inky) or isinstance(_inst, Pinky)\
                                #         or isinstance(_inst, Blinky):
                                if _inst.state != STATE_REVIVE:
                                    _inst.state = STATE_FLEE
                                    _inst.vulnerable = True
                                    _inst.state_timer = 1000
                                    _inst.path_update_timer = 0
                    elif isinstance(inst, Fruit):
                        if inst.x - CWIDTH/2 <= self.x <= inst.x + CWIDTH/2 and inst.y == self.y:
                            game.add_score(2000)
                            game.instance_list.remove(inst)
                            del inst

            # ghost interactions
            for inst in game.get_ghosts():
                if dist([self.x, self.y], [inst.x, inst.y]) < CWIDTH/2:
                    if inst.vulnerable is True:
                        inst.state = STATE_REVIVE
                        inst.make_path(game.get_grid(), inst.spawnpoint[0], inst.spawnpoint[1])
                        inst.vulnerable = False
                        game.add_score(500)
                    elif inst.state != STATE_REVIVE:
                        self.dying = True
                        game.end_timer = 700
                        game.ending = True
                        self.snd_death.play()
            # fire portal
            keys = pygame.key.get_pressed()
            if keys[K_SPACE] == 1 and not self.portal_ball_active:
                instance_create(PortalBall(self.x, self.y, self, self.dir, self.next_portal_color), game.instance_list)
                self.portal_ball_active = True
                self.snd_shootportal.play()

    def draw(self, game):
        if self.arc_offset is 0:
            pygame.draw.circle(game.window, c_yellow, (int(self.x), int(self.y)), 8)
        else:
            pygame.draw.arc(game.window, c_yellow, (int(self.x) - 8, int(self.y)-8, 16, 16),
                            self.arc_offset + self.dir*math.pi/2, -self.arc_offset + self.dir*math.pi/2, 8)


class Ghost(Actor):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.path = Path()
        self.next_node = None
        self.sprite = []
        self.s_up = []
        self.s_down = []
        self.s_right = []
        self.s_left = []
        self.s_vulnerable = ['s_ghost_vuln1.png', 's_ghost_vuln2.png']
        self.s_eyes = ['s_ghost_eyes.png']
        self.state = STATE_SHOP
        self.state_timer = 0
        self.path_update_timer = 0
        self.rechase_chance = 0.0  # chance to continue to chase while in chase state
        self.shop_corner = 'tl'  # corner that the ghost will "shop" in during shop state
        self.vulnerable = False
        self.image_index = 0

    def make_path(self, grid, targetx, targety):
        gridx = math.floor(targetx / CWIDTH)
        gridy = math.floor(targety / CHEIGHT)
        return self.path.path_create(grid, math.floor(self.x / CWIDTH), math.floor(self.y / CHEIGHT), gridx, gridy)
        # print("PATH CREATED: ", self.path._nodes)

    def path_continue(self):
        self.movement_progress += 0.49
        if self.movement_progress >= 1:  # move a pixel
            self.movement_progress -= 1
            if self.next_node is not None and self.next_node[0] == self.x and self.next_node[1] == self.y:
                # we are already on a breakpoint
                self.next_node = self.path.get_next()
                self.path.pop_front()
            elif self.next_node is None and self.path.length() > 0:
                self.next_node = self.path.get_next()
                self.path.pop_front()
            if self.next_node is not None:
                self.xprevious = self.x
                self.yprevious = self.y
                nextx = self.next_node[0]
                nexty = self.next_node[1]
                if nextx == self.x:  # move on y axis
                    if nexty > self.y:
                        self.y += 1
                    elif nexty < self.y:
                        self.y -= 1
                else:
                    if nextx > self.x:
                        self.x += 1
                    elif nextx < self.x:
                        self.x -= 1

    def find_path_in_corner(self, game, corner):
        # path to a random spot in a given corner of the map
        lbound = 0
        rbound = game.get_grid().width()-1
        tbound = 3
        bbound = game.get_grid().height()-3
        if corner is 'tl':
            rbound = math.floor(game.get_grid().width() / 2)
            bbound = math.floor(game.get_grid().height() / 2)
        elif corner is 'tr':
            lbound = math.ceil(game.get_grid().width() / 2)
            bbound = math.floor(game.get_grid().height() / 2)
        elif corner is 'bl':
            rbound = math.floor(game.get_grid().width() / 2)
            tbound = math.ceil(game.get_grid().height() / 2)
        else:  # br and just in case catching
            lbound = math.ceil(game.get_grid().width() / 2)
            tbound = math.ceil(game.get_grid().height() / 2)

        # now pick random tiles in the corner until the path is found
        path_success = False
        while not path_success:
            rx = random.randint(lbound, rbound)
            ry = random.randint(tbound, bbound)
            path_success = self.make_path(game.get_grid(), rx * CWIDTH, ry * CHEIGHT)

    def update(self, game):

        if self.state == STATE_CHASE:
            if self.path_update_timer <= 0:
                pac = game.get_pacman()
                # scramble path timer so it's not all on the same tick
                self.path_update_timer = random.randint(100, 130)
                self.make_path(game.get_grid(), pac.x, pac.y)
                if self.path.length() > 0 and self.next_node is not None\
                        and dist([self.x, self.y], [self.next_node[0], self.next_node[1]]) < CWIDTH/2:
                    self.next_node = self.path.get_next()
                    self.path.pop_front()

        elif self.state == STATE_FLEE:
            pac = game.get_pacman()
            if self.path.length() < 0 or (dist([pac.x, pac.y], [self.x, self.y]) and self.path_update_timer <= 0):
                self.path_update_timer = random.randint(100, 120)
                # find a random place nearby to flee to that's away from pacman
                # first find the corner pacman is in
                map_width = game.get_grid().width() * CWIDTH
                map_height = game.get_grid().height() * CHEIGHT
                if pac.x > map_width / 2:
                    if pac.y > map_height / 2:
                        pac_corner = 'br'  # bottom right
                    else:
                        pac_corner = 'tr'  # top right
                else:
                    if pac.y > map_height / 2:
                        pac_corner = 'bl'  # bottom left
                    else:
                        pac_corner = 'tl'  # top left
                if pac_corner is 'br':
                    pathing_corner = 'tl'
                elif pac_corner is 'bl':
                    pathing_corner = 'tr'
                elif pac_corner is 'tr':
                    pathing_corner = 'bl'
                else:
                    pathing_corner = 'br'
                self.find_path_in_corner(game, pathing_corner)

        elif self.state == STATE_SHOP:
            if self.path.length() == 0:
                # find a random place in a corner to go to
                self.find_path_in_corner(game, self.shop_corner)
                self.path_update_timer = random.randint(30, 35)

        elif self.state == STATE_REVIVE:
            # keep on path to rez point, then rez
            if self.path.length() == 0:
                self.state_timer = 0
                if random.random() < self.rechase_chance:
                    self.state = STATE_CHASE
                else:
                    self.state = STATE_SHOP

        self.path_continue()

        if self.state_timer <= 0:
            self.state_timer = random.randint(2000, 3000)
            if self.state == STATE_CHASE:
                if random.random() < self.rechase_chance:
                    pass
                else:
                    self.state = STATE_SHOP
            elif self.state == STATE_SHOP:
                if random.random() < 0.5:
                    self.state = STATE_CHASE
                else:
                    r = random.random()
                    if r < 0.25:
                        self.shop_corner = 'tl'
                    elif r < 0.5:
                        self.shop_corner = 'tr'
                    elif r < 0.75:
                        self.shop_corner = 'bl'
                    else:
                        self.shop_corner = 'br'
            elif self.state == STATE_FLEE:
                self.vulnerable = False
                if random.random() < self.rechase_chance:
                    self.state = STATE_CHASE
                else:
                    self.state = STATE_SHOP
            elif self.state == STATE_REVIVE:
                pass

        # decrement timers
        self.state_timer -= 1
        self.path_update_timer -= 1

    def draw(self, game):
        if self.vulnerable is True:
            self.sprite = self.s_vulnerable
        elif self.state == STATE_REVIVE:
            self.sprite = self.s_eyes
        elif self.yprevious < self.y:
            self.sprite = self.s_down
        elif self.yprevious > self.y:
            self.sprite = self.s_up
        elif self.xprevious > self.x:
            self.sprite = self.s_left
        else:
            self.sprite = self.s_right
        self.image_index += 0.01
        if self.image_index >= len(self.sprite):
            self.image_index = 0
        image = pygame.image.load(self.sprite[math.floor(self.image_index)])
        game.window.blit(image, (self.x - CWIDTH/2, self.y - CHEIGHT/2))
        """
        col = c_red
        if self.vulnerable:
            col = c_dkblue
        pygame.draw.rect(game.window, col, (self.x-6, self.y-6, 13, 13))
        """


class Blinky(Ghost):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.s_up = ['s_blinky_u1.png', 's_blinky_u2.png']
        self.s_down = ['s_blinky_d1.png', 's_blinky_d2.png']
        self.s_left = ['s_blinky_l1.png', 's_blinky_l2.png']
        self.s_right = ['s_blinky_r1.png', 's_blinky_r2.png']
        self.rechase_chance = 1.0


class Inky(Ghost):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.s_up = ['s_inky_u1.png', 's_inky_u2.png']
        self.s_down = ['s_inky_d1.png', 's_inky_d2.png']
        self.s_left = ['s_inky_l1.png', 's_inky_l2.png']
        self.s_right = ['s_inky_r1.png', 's_inky_r2.png']
        self.rechase_chance = 0.5


class Pinky(Ghost):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.s_up = ['s_pinky_u1.png', 's_pinky_u2.png']
        self.s_down = ['s_pinky_d1.png', 's_pinky_d2.png']
        self.s_left = ['s_pinky_l1.png', 's_pinky_l2.png']
        self.s_right = ['s_pinky_r1.png', 's_pinky_r2.png']
        self.rechase_chance = 0.5


class Clyde(Ghost):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.s_up = ['s_clyde_u1.png', 's_clyde_u2.png']
        self.s_down = ['s_clyde_d1.png', 's_clyde_d2.png']
        self.s_left = ['s_clyde_l1.png', 's_clyde_l2.png']
        self.s_right = ['s_clyde_r1.png', 's_clyde_r2.png']
        self.rechase_chance = 0.0


class StaticObject:

    def __init__(self, x, y):
        self.x = round(x)
        self.y = round(y)

    def update(self, game):
        pass

    def draw(self, game):
        pass


class Wall(StaticObject):

    def draw(self, game):
        pygame.draw.rect(game.window, c_blue, (self.x, self.y, CWIDTH, CHEIGHT))


class SpawnBarrier(StaticObject):

    def draw(self, game):
        pygame.draw.rect(game.window, c_white, (self.x, self.y, CWIDTH, CHEIGHT/4))


class Pellet(StaticObject):

    def draw(self, game):
        pygame.draw.circle(game.window, c_white, (int(self.x), int(self.y)), 2)


class PowerPellet(StaticObject):

    def draw(self, game):
        pygame.draw.circle(game.window, c_white, (int(self.x), int(self.y)), 6)


class Fruit(StaticObject):

    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('s_fruit.png')

    def draw(self, game):
        game.window.blit(self.image, (self.x - CWIDTH / 2, self.y - CHEIGHT / 2))


class PortalBall:

    def __init__(self, x, y, pacman, direc, pcol):
        self.pacman = pacman
        self.dir = direc
        self.movement_progress = 0
        self.x = x
        self.y = y
        self.col = pcol
        self.snd_open = pygame.mixer.Sound('portal_open.wav')

    def update(self, game):
        self.movement_progress += .75
        if self.movement_progress >= 1:
            self.movement_progress -= 1
            if self.dir == 0:
                self.x += 1
            elif self.dir == 1:
                self.y -= 1
            elif self.dir == 2:
                self.x -= 1
            else:
                self.y += 1

            # check collision with walls
            gridx = math.floor(self.x / CWIDTH)
            gridy = math.floor(self.y / CHEIGHT)
            if game.get_grid().width() > gridx >= 0 and game.get_grid().height() > gridy >= 0 and\
                    game.get_grid().getval(gridx, gridy) < 0:
                self.pacman.portal_ball_active = False
                self.snd_open.play()
                new_port = instance_create(Portal(self.x, self.y, self.dir, self.col, self.pacman), game.instance_list)
                self.pacman.num_portals = min(self.pacman.num_portals+1, 2)
                if self.pacman.next_portal_color == c_blue:
                    self.pacman.next_portal_color = c_orange
                    if self.pacman.portal1 is not None:
                        self.pacman.portal1.snd_close.play()
                        for i in range(len(game.instance_list)):
                            if game.instance_list[i] == self.pacman.portal1:
                                del game.instance_list[i]
                                break
                    self.pacman.portal1 = new_port
                else:
                    self.pacman.next_portal_color = c_blue
                    if self.pacman.portal2 is not None:
                        self.pacman.portal2.snd_close.play()
                        for i in range(len(game.instance_list)):
                            if game.instance_list[i] == self.pacman.portal2:
                                del game.instance_list[i]
                                break
                    self.pacman.portal2 = new_port
                for i in range(len(game.instance_list)):
                    if game.instance_list[i] is self:
                        del game.instance_list[i]
                        break
            # screen wrap
            if self.x <= -CWIDTH / 2:
                self.x = game.get_grid().width() * CWIDTH + CWIDTH / 2 - 1
            elif self.x >= game.get_grid().width() * CWIDTH + CWIDTH / 2:
                self.x = -CWIDTH / 2 + 1

    def draw(self, game):
        pygame.draw.circle(game.window, self.col, (int(self.x), int(self.y)), 4)


class Portal:

    def __init__(self, x, y, direc, col, pacman):
        self.x = x
        self.y = y
        self.dir = direc
        self.pacman = pacman
        if col == c_blue:
            self.col1 = c_ltblue
            self.col2 = c_dkblue
        else:
            self.col1 = c_orange
            self.col2 = c_dkorange
        self.snd_close = pygame.mixer.Sound('portal_close.wav')

    def update(self, game):
        pass

    def draw(self, game):
        if self.dir == 0 or self.dir == 2:
            pygame.draw.ellipse(game.window, self.col2,
                                (self.x - CWIDTH/4 - 1, self.y - CHEIGHT/2 - 1, CWIDTH/2 + 2, CHEIGHT + 2))
            if self.pacman.num_portals > 1:
                pygame.draw.ellipse(game.window, self.col1,
                                    (self.x - CWIDTH/4, self.y - CHEIGHT/2, CWIDTH/2, CHEIGHT))
        else:
            pygame.draw.ellipse(game.window, self.col2,
                                (self.x - CWIDTH / 2 - 1, self.y - CHEIGHT / 4 - 1, CWIDTH + 2, CHEIGHT / 2 + 2))
            if self.pacman.num_portals > 1:
                pygame.draw.ellipse(game.window, self.col1,
                                    (self.x - CWIDTH / 2, self.y - CHEIGHT / 4, CWIDTH, CHEIGHT / 2))


def instance_create(inst, instance_list):
    instance_list.append(inst)
    return instance_list[len(instance_list)-1]


def get_grid_adjacent(grid, xcoord, ycoord, direction):
    gridx = math.floor(xcoord / CWIDTH)
    gridy = math.floor(ycoord / CHEIGHT)
    if direction is RIGHT:
        gridx += 1
    elif direction is LEFT:
        gridx -= 1
    elif direction is UP:
        gridy -= 1
    elif direction is DOWN:
        gridy += 1
    gridx = min(gridx, grid.width()-1)
    gridy = min(gridy, grid.height()-1)
    return grid.getval(gridx, gridy)


def dist(p, q):
    return math.sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))


def write_to_highscores(score):
    f = open('highscores.txt', 'r+')
    lines = f.readlines()
    final_text = ""
    for i in range(1, len(lines), 2):
        s = lines[i]
        if int(s) < score:
            # write new score here
            lines[i-1] = 'PLAYER\n'
            lines[i] = str(score)
        final_text += lines[i-1]
        final_text += lines[i]
    f.seek(0)
    f.write(final_text)
    f.close()


def main():

    pygame.init()
    pygame.mixer.init()
    game = Game("pacman_grid.txt")
    mapw = game.get_grid().width()
    maph = game.get_grid().height()
    if not game.window_created:
        game.window = pygame.display.set_mode((mapw * CWIDTH, maph * CHEIGHT))
        game.window_created = True
    game.show_main_menu()
    # game.start("pacman_grid.txt")

    pygame.display.update()

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type is QUIT:
                pygame.mixer.quit()
                pygame.quit()
                return
        game.window.fill(c_black)
        game.update()
        game.draw()
        pygame.display.update()


main()
