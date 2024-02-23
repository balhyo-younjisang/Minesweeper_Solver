import random

import numpy as np

from minesweeper_basic import Minesweeper
from DQN import create_dqn
from collections import deque

# Initialize Network Hyperparameters
LEARNING_RATE = 0.01
LEARNING_DECAY = 0.99
LEARNING_MIN = 0.1
GAMMA = 0.1

# Initialize exploration settings
EPSILON = 0.9
EPSILON_DECAY = 0.99
EPSILON_MIN = 0.01

MEMORY_SIZE = 50_000

MODEL_NAME = f'gamma{GAMMA}_lr{LEARNING_RATE}'

class DQNAgent(object):
    def __init__(self, environment):
        self.env = environment

        self.learning_rate = LEARNING_RATE
        self.learning_decay = LEARNING_DECAY
        self.learning_min = LEARNING_MIN

        self.gamma = GAMMA

        self.epsilon = EPSILON
        self.epsilon_decay = EPSILON_DECAY
        self.epsilon_min = EPSILON_MIN

        self.model = create_dqn(self.learning_rate, self.env.ROWS, self.env.COLUMNS)

        self.replay_memory = deque(maxlen=MEMORY_SIZE)

    def act(self, state):
        flattened_state = state.flatten()

        if self.epsilon > np.random.rand():
            valid_actions = np.where(flattened_state == 9)[0]
            return np.random.choice(valid_actions)
        else:
            valid_actions = [0 if x == "B" else 1 for x in flattened_state]
            q_values = self.model.predict(np.reshape(state, (1, self.env.ROWS, self.env.COLUMNS, 1)))
            valid_qvalues = np.ma.masked_array(q_values, valid_actions)
            return np.argmax(valid_qvalues)

    def remember(self, state, action, reward, next_state, done):
        self.replay_memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        minibatch = random.sample(self.replay_memory, batch_size)
        states, targets_f = [], []

        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            targets_f[0][action] = target
            states.append(state[0])
            targets_f.append(target_f[0])
        history = self.model.fit(np.array(states), np.array(targets_f), epochs=1, verbose=0)
        loss = history.history['loss'][0]
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        return loss

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
