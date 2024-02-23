import random
from collections import deque
import numpy as np
from DQN import create_dqn
from minesweeper_basic import Minesweeper

# Environment settings
MEMORY_SIZE = 50_000

# Learning settings
BATCH_SIZE = 64
LEARNING_RATE = 0.01
LEARNING_DECAY = 0.99
LEARNING_MIN = 0.1
GAMMA = 0.1

# Exploration settings
EPSILON = 0.9
EPSILON_DECAY = 0.99
EPSILON_MIN = 0.01

ROWDIM = 9
COLDIM = 9
MINES = 10
EPISODE = 5_000


class DQNAgent:
    def __init__(self):
        self.EPSILON = EPSILON
        self.EPSILON_MIN = EPSILON_MIN
        self.EPSILON_DECAY = EPSILON_DECAY

        self.model = create_dqn(learn_rate=LEARNING_RATE, ROWDIM=ROWDIM, COLDIM=COLDIM)
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.moves = 0

    def memorize(self, transition):
        self.memory.append(transition)

    def act(self, act_state):
        flattened_state = act_state.flatten()
        if np.random.rand() < EPSILON:
            valid_actions = np.where(flattened_state == 9)[0]
            return np.random.choice(valid_actions)
        act_values = self.model.predict(act_state)
        return np.argmax(act_values[0])

    def replay(self):
        minibatch = random.sample(self.memory, BATCH_SIZE)
        states, targets_f = [], []

        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + GAMMA * np.amax(self.model.predict(next_state)[0]))

            target_f = self.model.predict(state)
            target_f[0][action] = target
            states.append(state[0])
            targets_f.append(target_f[0])
        memory = self.model.fit(np.array(states), np.array(targets_f), epochs=1, verbose=0)
        loss = memory.memory['loss'][0]

        if self.EPSILON > self.EPSILON_MIN:
            self.EPSILON *= self.EPSILON_DECAY
        return loss

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


if __name__ == "__main__":
    env = Minesweeper(ROWDIM, COLDIM, MINES)
    agent = DQNAgent()
    trial_episode_moves = []

    for episode in range(1, EPISODE + 1):
        episode_state = env.reset()
        for step_num in range(500):
            episode_action = agent.act(episode_state)
            episode_next_state, episode_reward, episode_done = env.step(episode_action)
            agent.memorize((episode_state, episode_action, episode_reward, episode_next_state, episode_done))
            state = episode_next_state

            agent.moves += 1

            if episode_done:
                print("episode {}/{}, moves : {}, reward: {}, won : {}, lost: {}".format(episode, EPISODE, agent.moves, episode_reward, env.won, env.lost))
                break
            if len(agent.memory) > BATCH_SIZE:
                loss = agent.replay()
