import sys
# from DQNModel import DQN # A class of creating a deep q-learning model
from MinerEnv import MinerEnv # A class of creating a communication environment between the DQN model and the GameMiner environment (GAME_SOCKET_DUMMY.py)
from heuristic_model1_submit4 import Heuristic_1

import pandas as pd
import datetime 
import numpy as np

import json
import codecs

game = json.load(codecs.open('submit_4/game_2.json', 'r', 'utf-8-sig'))
# for step in game:
#     print(step.keys())
#     for player in step['players']:
#         if player['status'] != 0:
#             print(player)

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
                    m_ = 2
                    x_ = 13
                    y_ = 5
                    request = 'map{},{},{},50,100'.format(m_, x_, y_)
                    print(request)
                    # request = 'map1,1,1,50, 100'
                    #Send the request to the game environment (GAME_SOCKET_DUMMY.py)
                    minerEnv.send_map_info(request)

                    # Getting the initial state
                    minerEnv.reset() #Initialize the game environment
                    #Get the state after reseting. 
                    maxStep = minerEnv.state.mapInfo.maxStep #Get the maximum number of steps for each episode in training

                    #Start an episde 
                    for step in range(0, maxStep):
                        if step == 0:
                            s = minerEnv.get_state()
                        else:
                            another_player = 2
                            # print(type(game[step]['golds']))
                            s.mapInfo.golds = game[step -1]['golds']
                            for cell in s.mapInfo.obstacles:
                                for cell_ in game[step - 1]['changedObstacles']:
                                    if cell['posx'] == cell_['posx'] and cell['posy'] == cell_['posy']:
                                        cell['type'] = cell_['type']
                                        cell['value'] = cell_['value']
                            for player in game[step - 1]['players']:
                                if player['playerId'] == 2344466:
                                    s.lastAction = player['lastAction']
                                    s.x = player['posx']
                                    s.y = player['posy']
                                    s.energy = player['energy']
                                    s.status = player['status']
                                else:
                                    s.players.append({"playerId": another_player, 
                                                        "posx": player['posx'], 
                                                        "posy": player['posy'],
                                                        "energy": player["energy"],
                                                        "status": player["status"],
                                                        "lastAction": player["lastAction"]})
                                    another_player += 1
                        
                        for player in game[step]['players']:
                            if player['playerId'] == 2344466:
                                print('action must do next step: {}'.format(player['lastAction']))
                                

                        # print(s.x, s.y, s.energy)
                        # tic = time.time()
                        action = heuristic_1.act(s)  
                        print('step: {}, action: {}'.format(step, action))
                        # print('time: {}'.format(time.time() - tic))
                        # minerEnv.step(str(action))  # Performing the action in order to obtain the new state
                        # if minerEnv.check_terminate():break

                    print('bot1_score: {}, step count: {}\n'.format(minerEnv.socket.bots[0].info.score, minerEnv.socket.bots[0].step_count),
                        'bot2_score: {}, step count: {}\n'.format(minerEnv.socket.bots[1].info.score, minerEnv.socket.bots[1].step_count),
                        'bot3_score: {}, step count: {}\n'.format(minerEnv.socket.bots[2].info.score, minerEnv.socket.bots[2].step_count),
                        'user_score: {}, step count: {}\n'.format(minerEnv.socket.user.score, minerEnv.state.stepCount))



                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    break