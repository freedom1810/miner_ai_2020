import numpy as np
import gym
import sys

from keras import Input, Model
from rl.agents import DDPGAgent
from rl.random import OrnsteinUhlenbeckProcess

sys.path.append('src')

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Concatenate
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="0"

# from Config import *
N_EPISODE = 10000 #The number of episodes for training
MAX_STEP = 1000   #The number of steps for each episode
BATCH_SIZE = 32   #The number of experiences for each replay
MEMORY_SIZE = 100000 #The size of the batch for storing experiences
SAVE_NETWORK = 100  # After this number of episodes, the DQN model is saved for testing later.
INITIAL_REPLAY_SIZE = 1000 #The number of experiences are stored in the memory batch before starting replaying
INPUTNUM = 198 #The number of input values for the DQN model
ACTIONNUM = 6  #The number of actions output from the DQN model
MAP_MAX_X = 21 #Width of the Map
MAP_MAX_Y = 9  #Height of the Map
DEBUG = False
from MinerGymEnv import MinerGymEnv


env = MinerGymEnv(HOST=None, PORT=None)
env.start()
env.reset()
nb_actions = env.action_space.n


actor = Sequential()
actor.add(Flatten(input_shape=(1,207) ))
actor.add(Dense(400))
actor.add(Activation('relu'))
actor.add(Dense(300))
actor.add(Activation('relu'))
actor.add(Dense(nb_actions))
actor.add(Activation('tanh'))
print(actor.summary())


action_input = Input(shape=(nb_actions,), name='action_input')
observation_input = Input(shape=(1,207) , name='observation_input')
flattened_observation = Flatten()(observation_input)
x = Dense(400)(flattened_observation)
x = Activation('relu')(x)
x = Concatenate()([x, action_input])
x = Dense(300)(x)
x = Activation('relu')(x)
x = Dense(1)(x)
x = Activation('linear')(x)
critic = Model(inputs=[action_input, observation_input], outputs=x)
print(critic.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=100000, window_length=1)
random_process = OrnsteinUhlenbeckProcess(size=nb_actions, theta=.15, mu=0., sigma=.1)
agent = DDPGAgent(nb_actions=nb_actions, actor=actor, critic=critic, critic_action_input=action_input,
                  memory=memory, nb_steps_warmup_critic=1000, nb_steps_warmup_actor=1000,
                  random_process=random_process, gamma=.99, target_model_update=1e-3)
agent.compile([Adam(lr=1e-4), Adam(lr=1e-3)], metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
agent.fit(env, nb_steps=1000000, visualize=True, verbose=1)

# After training is done, we save the final weights.
agent.save_weights('TrainedModels/ddpg_weights.h5f', overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
agent.test(env, nb_episodes=5, visualize=True, nb_max_episode_steps=200)