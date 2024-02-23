from DQNAgent import DQNAgent, MODEL_NAME
from minesweeper_basic import Minesweeper
import tensorflow as tf

# Initialize game environment
ROWDIM = 9
COLDIM = 9
MINE_COUNT = 10
env = Minesweeper(ROWDIM, COLDIM, MINE_COUNT)

# Initialize training parameters
EPISODES = 10_000
MEMORY_SIZE = 50_000
SAVE_MODEL_EVERY = 1000

if __name__ == "__main__":
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    agent = DQNAgent(env)
    wins_list, episode_per_rewards = [], []

    for episode in range(0, EPISODES):
        env.reset()
        current_state, reward, done = env.step((0, 0))

        episode_reward = reward
        episode_wins = env.won

        while not done:
            action = agent.act(current_state)
            new_state, new_reward, new_done = env.step(action)

            episode_reward += new_reward

            agent.remember(current_state, action, reward, new_state, done)
            current_state = new_state

        if env.won > episode_wins:
            wins_list.append(1)
        else:
            wins_list.append(0)

        if len(agent.replay_memory) < MEMORY_SIZE:
            continue

        if not episode % SAVE_MODEL_EVERY:
            agent.save(f"./models/{MODEL_NAME}.h5")
