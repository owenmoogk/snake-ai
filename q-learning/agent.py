from typing import final
import torch
import random
import numpy as np
from game import SnakeGameAI, Point, Direction
from model import Linear_QNet, QTrainer
from collections import deque
from helper import plot

maxMemory = 100_000
batchSize = 1000
learningRate = 0.001


class Agent:

    def __init__(self):
        self.numberOfGames = 0
        self.epsilon = 0  # controlls randomness
        self.gamma = 0.9  # discount rate, <1
        
        # will popleft if there is too much in memory
        self.memory = deque(maxlen=maxMemory)
        
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr = learningRate, gamma=self.gamma)

    def getState(self, game):
        head = game.snake[0]

        # Clok-wise directions and angles
        cw_dirs = [
            Direction.RIGHT == game.direction,
            Direction.DOWN == game.direction,
            Direction.LEFT == game.direction,
            Direction.UP == game.direction
        ]
        cw_angs = np.array([0, np.pi/2, np.pi, -np.pi/2])

        # Position - in front: 0, on right: 1, on left: -1; BLOCK_SIZE = 20
        def getPoint(pos): return Point(
            head.x + 20*np.cos(cw_angs[(cw_dirs.index(True)+pos) % 4]),
            head.y + 20*np.sin(cw_angs[(cw_dirs.index(True)+pos) % 4]))

        state = [
            # Danger
            game.is_collision(getPoint(0)),
            game.is_collision(getPoint(1)),
            game.is_collision(getPoint(-1)),

            # Move direction
            cw_dirs[2],
            cw_dirs[0],
            cw_dirs[3],
            cw_dirs[1],

            # Food location
            game.food.x < head.x,
            game.food.x > head.x,
            game.food.y < head.y,
            game.food.y > head.y
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def trainLongMemory(self):
        if len(self.memory) > batchSize:
            # list of tuples from the memory
            miniSample = random.sample(self.memory, batchSize)
        else:
            miniSample = self.memory

        states, actions, rewards, next_states, game_over = zip(*miniSample)
        self.trainer.train_step(states, actions, rewards, next_states, game_over)

    def trainShortMemory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def getAction(self, state):
        # exploitation / exploration
        self.epsilon = 80 - self.numberOfGames
        final_move = [0,0,0]
        if random.randint(-2,200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return(final_move)


def train():
    # data to plot
    plotScores = []
    plotMeanScores = []
    totalScore = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:
        stateOld = agent.getState(game)

        move = agent.getAction(stateOld)

        reward, game_over, score = game.play_step()

        stateNew = agent.getState(game)

        agent.trainShortMemory(stateOld, move, reward, stateNew, game_over)

        agent.remember(stateOld, move, reward, stateNew, game_over)

        if game_over:
            # train long memory, plot results, reset the game
            game.reset()

            agent.numberOfGames += 1
            agent.trainLongMemory()

            if score > record:
                record = score
                agent.model.save()

            print("Game", agent.numberOfGames,
                  'Score', score, 'Record', record)

            plotScores.append(score)
            totalScore += score
            mean_score = totalScore / agent.numberOfGames
            plotMeanScores.append(mean_score)
            plot(plotScores, plotMeanScores)

if __name__ == '__main__':
    train()
