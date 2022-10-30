from functools import partial
from imp import acquire_lock
from symbol import global_stmt
from time import sleep
from tkinter import font
import pygame
import random 
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    R = 1
    L = 2
    U = 3
    D = 4

Point = namedtuple('Point', 'x, y')

#rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN1 = (170, 255, 0)
GREEN2 = (80, 200, 120)
BLACK = (0, 0, 0)

SQUARE_SIZE = 20
SPEED = 15

class AISnake:

    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        # Setting up the pygame display parameters
        self.display = pygame.display.set_mode((self.width, self.height))
        # Setting display caption
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()
        
    def reset(self):
        # initializing game state -> setting up the initial direction which is Right
        self.direction = Direction.R

        # snake head point
        self.head = Point(self.height/2, self.width/2)
        # snake full body with head
        self.snake = [self.head,
                     Point(self.head.x - SQUARE_SIZE, self.head.y),
                     Point(self.head.x - (2 * SQUARE_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        # implement todo tree -> https://thomasventurini.com/articles/the-best-way-to-work-with-todos-in-vscode/
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        _food_x = random.randint(0, (self.width - SQUARE_SIZE)//SQUARE_SIZE) * SQUARE_SIZE
        _food_y = random.randint(0, (self.height - SQUARE_SIZE)//SQUARE_SIZE) * SQUARE_SIZE
        self.food = Point(_food_x, _food_y)
        if self.food in self.snake:
            self._place_food()
    
    def play_session(self, action):
        # Updating frame 

        self.frame_iteration += 1

        # Collecting input from user
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         self.direction = Direction.L
            #     elif event.key == pygame.K_RIGHT:
            #         self.direction = Direction.R
            #     elif event.key == pygame.K_UP:
            #         self.direction = Direction.U
            #     elif event.key == pygame.K_DOWN:
            #         self.direction = Direction.D

        # moving the snake at user defined direction
        self._move(action)
        # replacing previous head position by new one
        self.snake.insert(0, self.head)

        # Game over check
        reward = 0
        game_over = False
        if self._is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # place food or just move one frame
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        self._update_ui()
        self.clock.tick(SPEED)

        return reward, game_over, self.score

    def _update_ui(self):
        self.display.fill(BLACK)

        for part in self.snake:
            pygame.draw.circle(self.display, GREEN1, (part.x + SQUARE_SIZE / 2, part.y + SQUARE_SIZE / 2), SQUARE_SIZE / 2)
            pygame.draw.circle(self.display, GREEN2, (part.x + SQUARE_SIZE / 2, part.y + SQUARE_SIZE / 2), SQUARE_SIZE / 3)
            

        pygame.draw.circle(self.display, RED, (self.food.x + SQUARE_SIZE / 2, self.food.y + SQUARE_SIZE / 2), SQUARE_SIZE / 2)
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
            
    # detect all kinds of collision 
    def _is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.width - SQUARE_SIZE or pt.x < 0 or pt.y > self.height - SQUARE_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False
    
    # updating snake's head position
    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.R, Direction.D, Direction.L, Direction.U]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            # Direction haven't changed
            new_dir = clock_wise[idx] 
        elif np.array_equal(action, [0, 1, 0]):
            new_idx = (idx + 1) % 4
            # Right Turn r -> d -> l -> u
            new_dir = clock_wise[new_idx]
        else: 
            # [0, 0, 1]
            new_idx = (idx - 1) % 4
            # Left Turn r -> u -> l -> d
            new_dir = clock_wise[new_idx]
        
        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.R:
            x += SQUARE_SIZE
        elif self.direction == Direction.L:
            x -= SQUARE_SIZE
        elif self.direction == Direction.U:
            y -= SQUARE_SIZE
        elif self.direction == Direction.D:
            y += SQUARE_SIZE
        
        self.head = Point(x, y)


# if __name__ == '__main__':
#     game = SnakeGameMain()

#     # game loop
#     while True:
#         game_over, score = game.play_session()

#         if game_over == True:
#             break
        
    
#     print('Final Score', score)



#     pygame.quit()

