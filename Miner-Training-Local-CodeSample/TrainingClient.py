import sys
# from DQNModel import DQN # A class of creating a deep q-learning model
from MinerEnv import MinerEnv # A class of creating a communication environment between the DQN model and the GameMiner environment (GAME_SOCKET_DUMMY.py)
from heuristic_model1 import Heuristic_1

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


# Create header for saving DQN learning file
# now = datetime.datetime.now() #Getting the latest datetime
# header = ["Ep", "Step", "Reward", "Total_reward", "Action", "Epsilon", "Done", "Termination_Code", "Loss"] #Defining header for the save file
# filename = LOG_PATH + now.strftime("%Y%m%d-%H%M") + ".csv" 
# with open(filename, 'w') as f:
#     pd.DataFrame(columns=header).to_csv(f, encoding='utf-8', index=False, header=True)


# Initialize environment
minerEnv = MinerEnv(HOST, PORT) #Creating a communication environment between the DQN model and the game environment (GAME_SOCKET_DUMMY.py)
minerEnv.start()  # Connect to the game

#Training Process
#the main part of the deep-q learning agorithm 
m = [1,2,3,4,5]
# for episode_i in range(0, 4):
for m_ in (1,2,3,4,5):
    for x_ in range(21):
        for y_ in range(9):
            for _ in range(4):
                try:
                    heuristic_1 = Heuristic_1()
                    # # Choosing a map in the list
                    # # mapID = np.random.randint(1, 6) #Choosing a map ID from 5 maps in Maps folder randomly
                    # mapID = m[episode_i]
                    # posID_x = np.random.randint(MAP_MAX_X) #Choosing a initial position of the DQN agent on X-axes randomly
                    # posID_y = np.random.randint(MAP_MAX_Y) #Choosing a initial position of the DQN agent on Y-axes randomly
                    # #Creating a request for initializing a map, initial position, the initial energy, and the maximum number of steps of the DQN agent
                    # request = ("map" + str(mapID) + "," + str(posID_x) + "," + str(posID_y) + ",50,100") 
                    request = 'map{},{},{},50, 100'.format(m_, x_, y_)
                    # request = 'map1,1,1,50, 100'
                    #Send the request to the game environment (GAME_SOCKET_DUMMY.py)
                    minerEnv.send_map_info(request)

                    # Getting the initial state
                    minerEnv.reset() #Initialize the game environment
                    #Get the state after reseting. 
                    maxStep = minerEnv.state.mapInfo.maxStep #Get the maximum number of steps for each episode in training

                    #Start an episde 
                    for step in range(0, maxStep):
                        s = minerEnv.get_state()
                        # print(s.x, s.y, s.energy)
                        tic = time.time()
                        action = heuristic_1.act(s)  # Getting an action from the DQN model from the state (s)
                        # print(action)
                        # print('time: {}'.format(time.time() - tic))
                        minerEnv.step(str(action))  # Performing the action in order to obtain the new state
                        if minerEnv.check_terminate():break

                    print('bot1_score: {}, step count: {}\n'.format(minerEnv.socket.bots[0].info.score, minerEnv.socket.bots[0].step_count),
                        'bot2_score: {}, step count: {}\n'.format(minerEnv.socket.bots[1].info.score, minerEnv.socket.bots[1].step_count),
                        'bot3_score: {}, step count: {}\n'.format(minerEnv.socket.bots[2].info.score, minerEnv.socket.bots[2].step_count),
                        'user_score: {}, step count: {}\n'.format(minerEnv.socket.user.score, minerEnv.state.stepCount))



                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    break