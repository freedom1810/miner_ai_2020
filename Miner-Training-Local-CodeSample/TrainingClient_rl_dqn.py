import numpy as np
import gym
import sys

import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="1"

from rl.callbacks import ModelIntervalCheckpoint, FileLogger

sys.path.append('src')

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, BatchNormalization
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy, EpsGreedyQPolicy, LinearAnnealedPolicy, GreedyQPolicy
from rl.memory import SequentialMemory

from Config import *

from MinerGymEnv import MinerGymEnv

env = MinerGymEnv(HOST=None, PORT=None)
env.start()
env.reset()

nb_actions = env.action_space.n

# Next, we build a very simple model.
model = Sequential()
# model.add(Flatten(input_shape=(1, 207)))
model.add(Flatten(input_shape=(32,) + (207,)))
model.add(Dense(512))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Dense(512))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Dense(256))
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Dense(nb_actions))
model.add(Activation('linear'))
print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=32)
# policy = BoltzmannQPolicy()
policy = EpsGreedyQPolicy()
dqn = DQNAgent(model=model, 
                nb_actions=nb_actions, 
                memory=memory, 
                nb_steps_warmup=32,
                target_model_update=1e-2, 
                policy=policy)

dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# dqn.load_weights('TrainedModels/dqn.h5f')

callbacks = [ModelIntervalCheckpoint('TrainedModels_rl_dqn/dqn.h5f', interval=10000)]
# log_filename = 'log/'
# callbacks += [FileLogger(log_filename, interval=100)]

dqn.fit(env,
        callbacks=callbacks, 
        nb_steps=1000000, 
        visualize=False, 
        verbose=2)


dqn.save_weights('TrainedModels_rl_dqn/dqn._finalh5f', overwrite=True)
# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=500, visualize=True,verbose=2)