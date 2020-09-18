import sys
import numpy as np
import copy
import time 

from itertools import combinations 

try:
    from GAME_SOCKET_DUMMY_RANDOM import GameSocket #in testing version, please use GameSocket instead of GAME_SOCKET_DUMMY
except:
    from GAME_SOCKET import GameSocket 
    
from MINER_STATE import State

from .dijkstra import Dijkstra

TreeID = 1
TrapID = 2
SwampID = 3

print('use heuristic: {}'.format('submit_17_9'))



class Player():
    # def __init__(self):
    def __init__(self, state):
        self.state = state
        self.des = [state.x, state.y] 
        self.dijkstra = Dijkstra()
    
    def get_des(self):

        if len(self.state.mapInfo.golds) == 0: return self.des

        if self.des is None:
            des = self.find_des()

        if self.state.gold_info[self.des[0]][self.des[1]] == 0:
            des = self.find_des()
        else:
            return self.des
        # print('check des none list gold {}'.format(self.dijkstra.list_gold))
        # print('check des none des {}'.format(self.des))
        if des is None:
            return self.des # hết vàng rồi thì k làm gì nữa

        return des

    # def find_des(self):
    #     self.dijkstra.find_n_gold(self.state, n_gold=1)  
    #     self.des = self.dijkstra.list_gold.pop()
    #     self.des = [self.des['posx'], self.des['posy']]


class Heuristic_1:
    def __init__(self):

        self.state = None
        self.des = None
        self.list_gold = None
        self.dijkstra = Dijkstra()
        # self.state = None

    def act(self, state):
        # self.state = self.init_state(state)

        state.mapInfo.golds = self.delete_gold(state)

        self.state = self.dijkstra.init_state(state)

        if self.state.lastAction == 4 and self.state.energy < 40:
            return 4

        if self.check_des_none(): # tìm des
            return 4

        action = self.check_at_des()
        if action is not None:
            return action

        #tìm điểm tiếp theo
        next_cell = self.get_next_cell()
        if next_cell[1] == -477:
            return self.craft()
        # nước đi tiếp theo mà die thì phải nghỉ
        # print(self.des, state.x, state.y, next_cell, self.state.gold_info[state.x][state.y])
        if -self.lost_energy_next_step(next_cell, self.state)  >= self.state.energy:
            return 4

        action = self.convert_point_to_action(next_cell)
    
        return action 


    def delete_gold(self,state):

        gold_temp = []
        for cell in state.mapInfo.golds:
            if cell['amount'] >= 200:
                gold_temp.append(cell)
            if cell['posx'] == state.x and cell['posy'] == state.y and cell['amount'] > 50:
                gold_temp.append(cell)

        if len(gold_temp) <3:
            return state.mapInfo.golds
        return gold_temp

    def get_next_cell(self):

        next_cell_f = self.state.path[self.des[0] + self.des[1] * 21][self.state.x + self.state.y*21]
        if next_cell_f%21 == self.state.x and next_cell_f//21 == self.state.y:
            next_cell = self.des  
        else:
            next_cell = [next_cell_f%21, next_cell_f//21]

        return next_cell

    def craft(self):
        if self.state.energy > 5:
            return 5
        else:
            return 4

    def check_des_none(self):
        if len(self.state.mapInfo.golds) == 0: return True

        if self.des is None:
            self.des = self.find_des()
            if self.des is None:
                return True # hết vàng rồi thì k làm gì nữa

        if self.state.gold_info[self.des[0]][self.des[1]] == 0:

            self.des = self.find_des()

        # print('check des none list gold {}'.format(self.dijkstra.list_gold))
        # print('check des none des {}'.format(self.des))
        if self.des is None:
            return True # hết vàng rồi thì k làm gì nữa

    def find_des(self):

        if len(self.state.mapInfo.golds) > 3:
            for player in self.state.players :
                if self.check_status(player) and player["playerId"] != self.state.id:
                    state = copy.deepcopy(self.state)
                    state.x = player['posx']
                    state.y = player['posy']
                    state.energy = player['energy']
                    
                    des_temp = self.dijkstra.find_cluster_gold(state)
                    # if player["posx"] == self.state.x and player["posy"] == self.state.y:
                    golds_temp = []
                    for cell in self.state.mapInfo.golds:
                        if cell['posx'] == des_temp[0] and cell['posy'] == des_temp[1]:
                            pass
                        else:
                            golds_temp.append(cell)

                        self.state.mapInfo.golds = golds_temp

                    self.state.gold_info[des_temp[0]][des_temp[1]] = 0
        
        if not self.dijkstra.list_gold:
            self.dijkstra.find_n_gold_filter(self.state)  

        if not self.dijkstra.list_gold:
            return 
        cell = self.dijkstra.list_gold.pop()
        self.des = [cell['posx'], cell['posy']]

        return self.des

    def leave_early(self, gold_amount):
        # print('leave_early')
        # nếu quyết định đào vàng mà vàng đem về <50 -> đi luôn k đào nữa
        count = 0
        for player in self.state.players:
            if self.check_status(player):
                if player["posx"] == self.state.x and player["posy"] == self.state.y:
                    count +=1

        if count == 0:
            return False

        # print('gold {} count {}'.format(gold_amount, count))
        return gold_amount/count < 50
    
    def check_status(self, player):
        # neu nguoi choi khong co status hoac status != 0 ->  không cần quan tâm
        if 'status' not in player.keys():
            return False
        if player['status'] != 0:
            return False
        return True

    def check_at_des(self):
        if self.state.x == self.des[0] and self.state.y == self.des[1]:
            gold_amount = self.state.gold_info[self.des[0]][self.des[1]]
            if gold_amount > 50:
                if not self.leave_early(gold_amount):
                    # print('check_at_des craft')
                    return self.craft()
                else: 
                    golds_temp = []
                    for cell in self.state.mapInfo.golds:
                        if cell['posx'] == self.state.x and cell['posy'] == self.state.y:
                            # print('check_at_des  delete gold')
                            # cell['amount'] = 0
                            pass
                        else:
                            golds_temp.append(cell)

                    self.state.mapInfo.golds = golds_temp
                    self.state.gold_info[self.des[0]][self.des[1]] = 0

                    # print('check_at_des  leave early')

                    if self.check_des_none(): # tìm des
                        # print('check_at_des het vang')
                        
                        return 4        
        return 
        
    def convert_point_to_action(self, next_cell):
        if next_cell[0] - self.state.x == 1: return 1
        if next_cell[0] - self.state.x == -1: return 0

        if next_cell[1] - self.state.y == 1: return 3
        if next_cell[1] - self.state.y == -1: return 2

    def lost_energy_next_step(self, next_cell, state):
        if state.obstacle_info[next_cell[0]][next_cell[1]] == -13:
            return -20
        return state.obstacle_info[next_cell[0]][next_cell[1]]
