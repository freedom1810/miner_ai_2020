import sys
# from DQNModel import DQN # A class of creating a deep q-learning model
from MinerEnv import MinerEnv # A class of creating a communication environment between the DQN model and the GameMiner environment (GAME_SOCKET_DUMMY.py)
# from submit_8_9.heuristic_model import Heuristic_1
# from submit.heuristic_model_submit_10 import Heuristic_1
# from submit.heuristic_model_submit_6 import Heuristic_1
# print('use heuristic: {}'.format('6'))

# from submit_14_9.heuristic_model import Heuristic_1
from submit_17_9.heuristic_model import Heuristic_1

from eda import *

import pandas as pd
import datetime 
import numpy as np

import os
import time
HOST = "localhost"
PORT = 1111
if len(sys.argv) == 3:
    HOST = str(sys.argv[1])
    PORT = int(sys.argv[2])

# Initialize environment
minerEnv = MinerEnv(HOST, PORT) #Creating a communication environment between the DQN model and the game environment (GAME_SOCKET_DUMMY.py)
minerEnv.start()  # Connect to the game

#Training Process
#the main part of the deep-q learning agorithm 
m = [1,2,3,4,5]
# for episode_i in range(0, 4):
for m_ in range(6)[1:]:
    for x_ in range(1):
        for y_ in range(1):
            for _ in range(1):
                try:
                    heuristic_1 = Heuristic_1()
                    x_ = 20
                    y_ = 0
                    # m_ = 3
                    request = 'map{},{},{},50,100'.format(m_, x_, y_)
                    print(request)
                    #Send the request to the game environment (GAME_SOCKET_DUMMY.py)
                    minerEnv.send_map_info(request)

                    # Getting the initial state
                    minerEnv.reset() #Initialize the game environment
                    #Get the state after reseting. 
                    maxStep = minerEnv.state.mapInfo.maxStep #Get the maximum number of steps for each episode in training
                    s = minerEnv.get_state()
                    # minerEnv.check_info_map()
     
                    #Start an episde 

                    for step in range(0, maxStep):
                        # print(s.x, s.y, s.energy)
                        # tic = time.time()
                        # print('step: {}'.format(minerEnv.state.stepCount))

                        action = heuristic_1.act(s)  
                        # print(action)s
                        # print(heuristic_1.des)
                        # print(action)

                        # print('step: {}, action: {}'.format(minerEnv.state.stepCount, action))
                        # print(time.time() - tic)

                        minerEnv.step(str(action))  # Performing the action in order to obtain the new state
                        s = minerEnv.get_state()
                        # if minerEnv.check_terminate():
                        #     print(s.status)
                        #     break

                    print('bot1_score: {}, step count: {}\n'.format(minerEnv.socket.bots[0].info.score, minerEnv.socket.bots[0].step_count),
                        'bot2_score: {}, step count: {}\n'.format(minerEnv.socket.bots[1].info.score, minerEnv.socket.bots[1].step_count),
                        'bot3_score: {}, step count: {}\n'.format(minerEnv.socket.bots[2].info.score, minerEnv.socket.bots[2].step_count),
                        'user_score: {}, step count: {}\n'.format(minerEnv.socket.user.score, minerEnv.state.stepCount))



                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    break