import sys
# from DQNModel import DQN # A class of creating a deep q-learning model
from MinerEnv import MinerEnv # A class of creating a communication environment between the DQN model and the GameMiner environment (GAME_SOCKET_DUMMY.py)
from submit_17_9.heuristic_model import Heuristic_1

import pandas as pd
import datetime 
import numpy as np

import json
import codecs
game = json.load(codecs.open('submit_17_9/2344466_Log_Match_21687.json.json', 'r', 'utf-8-sig'))
# game = json.load(codecs.open('submit_17_9/2344466_Log_Match_21685.json.json', 'r', 'utf-8-sig'))
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


# Initialize environment
minerEnv = MinerEnv(HOST, PORT) #Creating a communication environment between the DQN model and the game environment (GAME_SOCKET_DUMMY.py)
minerEnv.start()  # Connect to the game


check = False
try:
    heuristic_1 = Heuristic_1()
    m_ = 17_09
    # x_ = 2
    # y_ = 8
    x_ = 2
    y_ = 8

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
            # print(type(game[step]['golds']))
            s.mapInfo.golds = game[step -1]['golds']
            for cell in s.mapInfo.obstacles:
                for cell_ in game[step - 1]['changedObstacles']:
                    if cell['posx'] == cell_['posx'] and cell['posy'] == cell_['posy']:
                        cell['type'] = cell_['type']
                        cell['value'] = cell_['value']

            s.players = []
            for player in game[step - 1]['players']:
                if player['playerId'] == 2344466:
                    s.id = 2344466
                    s.lastAction = player['lastAction']
                    s.x = player['posx']
                    s.y = player['posy']
                    s.energy = player['energy']
                    s.status = player['status']
                # else:
                s.players.append({"playerId": player['playerId'], 
                                    "posx": player['posx'], 
                                    "posy": player['posy'],
                                    "energy": player["energy"],
                                    "status": player["status"],
                                    "lastAction": player["lastAction"],
                                    "score" : player['score'],
                                    })
        
        # for player in game[step]['players']:
        #     if player['playerId'] == 2344466:
        #         print('action must do next step: {}'.format(player['lastAction']))
                

        # print(s.x, s.y, s.energy)
        tic = time.time()
        # print('vi tri {} {}'.format( s.x, s.y))
        action = heuristic_1.act(s)
        for player in game[step]['players']:
            if player['playerId'] == 2344466:
                print('action must do next step: {}'.format(player['lastAction']))
                # print(player['lastAction'])
                if player['lastAction'] != action:
                    
                    # print(action)
                    # break
                    check = True

        print('step: {}, vi tri: {}'.format(step - 1, (s.x, s.y)))
        print('step: {}, gold: {}'.format(step - 1, s.gold_info[s.x][s.y]))
        print('step: {}, action: {}'.format(step, action))

        print('time: {}'.format(time.time() - tic))
        # minerEnv.step(str(action))  # Performing the action in order to obtain the new state
        # if minerEnv.check_terminate():break
        if check :
            break
    print('bot1_score: {}, step count: {}\n'.format(minerEnv.socket.bots[0].info.score, minerEnv.socket.bots[0].step_count),
        'bot2_score: {}, step count: {}\n'.format(minerEnv.socket.bots[1].info.score, minerEnv.socket.bots[1].step_count),
        'bot3_score: {}, step count: {}\n'.format(minerEnv.socket.bots[2].info.score, minerEnv.socket.bots[2].step_count),
        'user_score: {}, step count: {}\n'.format(minerEnv.socket.user.score, minerEnv.state.stepCount))



except Exception as e:
    import traceback
    traceback.print_exc()