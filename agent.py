from shutil import move
from typing_extensions import Self
from xml.etree.ElementPath import prepare_predicate
import torch
import random
import numpy as np
from collections import deque
from game import AISnake, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.00125

class Agent:

    def __init__(self):
        self.n_games = 0
        # introduces randomness
        self.epsilon = 0 
        # discount rate
        self.gamma = 0.917 
        # pops from left
        self.memory = deque(maxlen=MAX_MEMORY) 
        self.model = Linear_QNet(11, 512, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger on straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger on right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger on left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food on left
            game.food.x > game.head.x,  # food on  right
            game.food.y < game.head.y,  # food above
            game.food.y > game.head.y  # food below
            ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        # pops old record (left) if MAX_MEMORY is reached
        self.memory.append((state, action, reward, next_state, done)) 

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            sample_memory_chunk = random.sample(self.memory, BATCH_SIZE)
        else:
            sample_memory_chunk = self.memory

        states, actions, rewards, next_states, dones = zip(*sample_memory_chunk)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def get_action(self, state):
        # exploration / exploitation tradeoff
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move_index = random.randint(0, 2)
            final_move[move_index] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move_index = torch.argmax(prediction).item()
            final_move[move_index] = 1

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = AISnake()
    while True:
        # fetch old state 
        old_state = agent.get_state(game)
        # get next move
        final_move = agent.get_action(old_state)
        # perform new move and get the new state
        reward, done, score = game.play_session(final_move)
        new_state = agent.get_state(game)

        # train short memory
        agent.train_short_memory(old_state, final_move, reward, new_state, done)

        # store parameters
        agent.remember(old_state, final_move, reward, new_state, done)

        if done:

            # train the long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # save the model agent.model.save()
            
            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            # plot code here

if __name__ == "__main__":
    train()