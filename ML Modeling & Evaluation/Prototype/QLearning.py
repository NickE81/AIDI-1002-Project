import numpy as np
import my_env

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam

from rl.agents import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

def train():
    env = my_env.DinoEnv()
    states = 6
    actions = env.action_space.n

    model = build_model(states, actions, dense_layers = 4)
    dqn = build_agent(model, actions)
    dqn.compile(Adam(lr=0.01), metrics = ['mae'])
    dqn.fit(env, nb_steps = 1000000, visualize = True, verbose = 1)
    dqn.save_weights('dqn_weights2.h5f', overwrite = True)

def load():
    env = my_env.DinoEnv()
    states = 6
    actions = env.action_space.n
    
    model = build_model(states, actions, dense_layers = 4)
    dqn = build_agent(model, actions)
    dqn.compile(Adam(lr=0.01), metrics = ['mae'])
    dqn.load_weights('dqn_weights.h5f')
    dqn.test(env, nb_episodes = 10, visualize = True)

def build_model(states, actions, dense_layers = 24, acti = 'relu'):
    model = Sequential()
    model.add(Flatten(input_shape = (1, states)))
    model.add(Dense(dense_layers, activation = acti))
    model.add(Dense(dense_layers, activation = acti))
    model.add(Dense(dense_layers, activation = acti))
    model.add(Dense(actions, activation = 'linear'))
    return model

def build_agent(model, actions):
    policy = EpsGreedyQPolicy(0.1)
    memory = SequentialMemory(limit = 1000000, window_length = 1)
    dqn = DQNAgent(model = model, memory = memory, policy = policy,
        nb_actions = actions, nb_steps_warmup = 25, target_model_update = 0.5)
    return dqn



if __name__ == "__main__":
    load()