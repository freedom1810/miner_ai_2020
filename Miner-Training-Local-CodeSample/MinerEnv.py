import sys
import numpy as np
from GAME_SOCKET_DUMMY import GameSocket #in testing version, please use GameSocket instead of GAME_SOCKET_DUMMY
from MINER_STATE import State
import copy
import sys

TreeID = 1
TrapID = 2
SwampID = 3

class MinerEnv:
    def __init__(self, host, port):
        self.socket = GameSocket(host, port)
        self.state = State()
        
        self.score_pre = self.state.score#Storing the last score for designing the reward function


    def start(self): #connect to server
        self.socket.connect()

    def end(self): #disconnect server
        self.socket.close()

    def send_map_info(self, request):#tell server which map to run
        self.socket.send(request)

    def reset(self): #start new game
        try:
            message = self.socket.receive() #receive game info from server
            self.state.init_state(message) #init state
        except Exception as e:
            import traceback
            traceback.print_exc()

    def step(self, action): #step process
        self.socket.send(action) #send action to server
        try:
            message = self.socket.receive() #receive new state from server
            self.state.update_state(message) #update to local state
        except Exception as e:
            import traceback
            traceback.print_exc()

    # Functions are customized by client
    def get_state(self):
        return self.state
        # Building the map
        view = np.zeros([self.state.mapInfo.max_x + 1, self.state.mapInfo.max_y + 1], dtype=int)
        for i in range(self.state.mapInfo.max_x + 1):
            for j in range(self.state.mapInfo.max_y + 1):
                if self.state.mapInfo.get_obstacle(i, j) == TreeID:  # Tree
                    view[i, j] = -TreeID
                if self.state.mapInfo.get_obstacle(i, j) == TrapID:  # Trap
                    view[i, j] = -TrapID
                if self.state.mapInfo.get_obstacle(i, j) == SwampID: # Swamp
                    view[i, j] = -SwampID
                if self.state.mapInfo.gold_amount(i, j) > 0:
                    view[i, j] = self.state.mapInfo.gold_amount(i, j)

        DQNState = view.flatten().tolist() #Flattening the map matrix to a vector
        
        # Add position and energy of agent to the DQNState
        DQNState.append(self.state.x)
        DQNState.append(self.state.y)
        DQNState.append(self.state.energy)
        #Add position of bots 
        for player in self.state.players:
            if player["playerId"] != self.state.id:

                DQNState.append(player["posx"])
                DQNState.append(player["posy"])

                # if "energy" in player:
                #     DQNState.append(player["energy"])
                # else:
                #     DQNState.append(50)

                # if 'status' in player: 
                #     DQNState.append(player["status"])
                # else:
                #     DQNState.append(0)

                # if 'free_count' in player:
                #     DQNState.append(player["free_count"])
                # else:
                #     DQNState.append(0)
                
        #Convert the DQNState from list to array for training
        DQNState = np.array(DQNState)

        return DQNState
        
    
    def check_info_map(self):

        # check info map, tổng gold, trung bình gold, min, max, số lượng mỏ
        x = []
        count_gold = len(self.state.mapInfo.golds)
        for cell in self.state.mapInfo.golds:
            x.append(cell["amount"])

        print('all gold: ', sum(x))
        print('gold per bai: ', sum(x)/count_gold)
        print('min: ', min(x))
        print('max: ', max(x))
        print('so luong: ', len(x))


    def check_terminate(self):
        #Checking the status of the game
        #it indicates the game ends or is playing
        return self.state.status != State.STATUS_PLAYING
