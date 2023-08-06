import pygame
from gym import Env
import numpy as np
from members import Circle, FreeSpaceRect, CellRect

class FreeSpaceEnv(Env):
    def __init__(self, action_space, observation_space, length, _handler, color = (0, 0, 0), scr=False, **kwargs):
        self.members = []
        self.action_space = action_space
        self.observation_space = observation_space
        self.length = [length]
        self._handler = _handler
        if scr!=False:
            pygame.init()
            self.screen_h, self.screen_w = scr
            self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.FULLSCREEN)
            self.clock = pygame.time.Clock()
        self.scr = scr
        self.screen_color = color
        self.optional_args = {key: [value] for (key, value) in kwargs.items()}
        self._initial_length = [length]
        self._optional_args_original = {key: [value] for (key, value) in kwargs.items()}
    def step(self, action):
        self.length[0]-=1
        observation, reward, done, info = self._handler(action)
        if self.length[0] == 0:
            done = True
        observation = np.array(observation)
        return observation, reward, done, info
    def reset(self):
        self.length[0] = self._initial_length[0]
        self.members.clear()
        for key in self.optional_args.keys():
            self.optional_args[key][0] = self._optional_args_original[key][0]
    def render(self):
        if self.scr != False:
            for e in pygame.event.get():   
                if e.type == pygame.QUIT:
                    break
            self.screen.fill(self.screen_color)
            for member in self.members:
                if isinstance(member, Circle):
                    pygame.draw.circle(self.screen, member.color, (member.x, member.y), member.r)
                else:
                    pygame.draw.rect(self.screen, member.color, (member.x, -member.y+self.screen_h, member.w, member.h))
            self.clock.tick(100);
            pygame.display.update()
        else:
            raise ValueError("Environment has not been instantiated with screen, and therefore cannot be rendered.")
    def add_member(self, member):
        if not isinstance(member, Circle) and not isinstance(member, FreeSpaceRect):
            raise ValueError("Member is not identifiable")
        else:
            self.members.append(member)
    def _get_args(self):
        return self.members, self.optional_args

class GridworldEnv(Env):
    def __init__(self, action_space, observation_space, length, _handler, table_dim, color = (0, 0, 0), **kwargs):
        self.action_space = action_space
        self.observation_space = observation_space
        self.length = [length]
        self._handler = _handler
        if table_dim[0][0] == 0 or table_dim[1][0] == 0:
            raise ValueError("Environment must be configured with at least 1 row and 1 column.")
        else:
            self.table = [[[] for _ in range(table_dim[1][0])] for _ in range(table_dim[0][0])]
        if table_dim[0][1] != 0 and table_dim[1][1] != 0:
            self.scr = True
            pygame.init()
            self.cell_w, self.cell_h = table_dim[1][1], table_dim[0][1]
            self.screen_w, self.screen_h = table_dim[1][0]*table_dim[1][1], table_dim[0][0]*table_dim[0][1]
            self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.FULLSCREEN)
            self.clock = pygame.time.Clock()
            self.screen_color = color
        else: self.scr = False
        self.outside = []
        self.optional_args = {key: [value] for (key, value) in kwargs.items()}
        self._initial_length = [length]
        self._optional_args_original = {key: [value] for (key, value) in kwargs.items()}
    def step(self, action):
        self.length[0] -= 1
        observation, reward, done, info = self._handler(action)
        if self.length[0] == 0:
            done = True
        observation = np.array(observation)
        self._update()
        return observation, reward, done, info
    def reset(self):
        self.length[0] = self._initial_length[0]
        self.table = [[[] for _ in range(len(self.table[0]))] for _ in range(len(self.table))]
        self.outside.clear()
        for key in self.optional_args.keys():
            self.optional_args[key][0] = self._optional_args_original[key][0]
    def render(self, grid_lines = True):
        self._update()
        if self.scr!=False:
            for e in pygame.event.get():   
                if e.type == pygame.QUIT:
                    break
            self.screen.fill(self.screen_color)
            if grid_lines:
                grid_color = (255-self.screen_color[0], 255-self.screen_color[1], 255-self.screen_color[2])
                for row in range(1, len(self.table)):
                    pygame.draw.line(self.screen, grid_color, (0, self.cell_h*row), (self.screen_w, self.cell_h*row))
                for col in range(1, len(self.table[0])):
                    pygame.draw.line(self.screen, grid_color, (col*self.cell_w, 0), (col*self.cell_w, self.screen_h))
            for row in range(len(self.table)):
                for col in range(len(self.table[row])):
                    for member in self.table[row][col]:
                        pygame.draw.rect(self.screen, member.color, (col*self.cell_w, -(row*self.cell_h)+self.screen_h, self.cell_w, self.cell_h))
            self.clock.tick(100);
            pygame.display.update()    
        else:
            raise ValueError("Environment has not been instantiated with screen, and therefore cannot be rendered.")
    def add_member(self, member):
        if not isinstance(member, CellRect):
            raise ValueError("Member is not identifiable")
        else:
            if (member.row>=len(self.table) or member.row<0 or member.col>=len(self.table[0]) or member.col<0):
                self.outside.append(member)
            else:
                self.table[member.row][member.col].append(member)
    def _update(self):
        for row in range(len(self.table)):
            for col in range(len(self.table[row])):
                for member in self.table[row][col]:
                    self.table[row][col].remove(member)
                    if (member.row>=len(self.table) or member.row<0 or member.col>=len(self.table[0]) or member.col<0):
                        self.outside.append(member)
                    else:
                        self.table[member.row][member.col].append(member)
        for member in self.outside:
            if member.row>= 0 and member.row<len(self.table) and member.col>=0 and member.col<len(self.table[0]):
                self.table[member.row][member.col].append(member)
    def _get_args(self):
        return self.members, self.optional_args