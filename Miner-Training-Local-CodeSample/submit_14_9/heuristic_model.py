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

print('use heuristic: {}'.format('submit_14_9'))

class Heuristic_1:
    def __init__(self):

        self.state = None
        self.des = None
        self.list_gold = None
        self.dijkstra = Dijkstra()
        # self.state = None

    def act(self, state):
        # self.state = self.init_state(state)
        self.state = self.dijkstra.init_state(state)

        if self.state.lastAction == 4 and self.state.energy < 40:
            return 4

        if self.check_des_none(): # tìm des
            return 4

        if self.check_at_des(): # check xem có đang ở vị trí gold
            gold_amount = self.state.gold_info[self.des[0]][self.des[1]]
            if gold_amount > 0:
                if not self.leave_early(gold_amount):
                    print('check_at_des craft')
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

                    print('check_at_des  leave early')

                    if self.check_des_none(): # tìm des
                        print('check_at_des het vang')
                        
                        return 4         

        # if self.state.gold_info[self.state.x][self.state.y] > 0:  # trên đường đi lại đi qua 1 mỏ vàng khác -> đào luôn
        #     if not self.leave_early(self.state.gold_info[self.state.x][self.state.y]):
        #         return self.craft()

        #tìm điểm tiếp theo
        next_cell = self.get_next_cell()
        # nước đi tiếp theo mà die thì phải nghỉ
        if -self.lost_energy_next_step(next_cell, self.state)  >= self.state.energy:
            return 4

        action = self.convert_point_to_action(next_cell)
    
        return action 

    def get_next_cell(self):
        # print(self.state.path[self.state.x + self.state.y*21])

        next_cell_f = self.state.path[self.des[0] + self.des[1] * 21][self.state.x + self.state.y*21]
        if next_cell_f%21 == self.state.x and next_cell_f//21 == self.state.y:
            next_cell = self.des  
        else:
            next_cell = [next_cell_f%21, next_cell_f//21]

        print('next cell f {}'.format(next_cell_f))
        print('next cell {}'.format(next_cell))
        print('des f {}'.format(self.des[0] + self.des[1] * 21))
        print('des {}'.format(self.des))
        return next_cell

    def craft(self):
        if self.state.energy > 5:
            return 5
        else:
            return 4

    def check_des_none(self):
        if len(self.state.mapInfo.golds) == 0: return True

        if self.des is None:
            if not self.dijkstra.list_gold:
                self.dijkstra.find_n_gold(self.state)  
            self.des = self.dijkstra.list_gold.pop()
            self.des = [self.des['posx'], self.des['posy']]

        if self.state.gold_info[self.des[0]][self.des[1]] == 0:
            if not self.dijkstra.list_gold:
                self.dijkstra.find_n_gold(self.state)  
            self.des = self.dijkstra.list_gold.pop()
            self.des = [self.des['posx'], self.des['posy']]

        print('check des none list gold {}'.format(self.dijkstra.list_gold))
        print('check des none des {}'.format(self.des))
        if self.des is None:
            return True # hết vàng rồi thì k làm gì nữa

    def leave_early(self, gold_amount):
        # nếu quyết định đào vàng mà vàng đem về <50 -> đi luôn k đào nữa
        count = 0
        for player in self.state.players:
            if player['playerId'] != 1 and self.check_status(player):
                if player["posx"] == self.state.x and player["posy"] == self.state.y:
                    count +=1

        if count == 0:
            return False
        return gold_amount/count < 50
    
    def check_status(self, player):
        # neu nguoi choi khong co status hoac status != 0 ->  không cần quan tâm
        if 'status' not in player.keys():
            return False
        if player['status'] != 0:
            return False
        return True

    def check_at_des(self):
        return self.state.x == self.des[0] and self.state.y == self.des[1]

    def convert_point_to_action(self, next_cell):
        if next_cell[0] - self.state.x == 1: return 1
        if next_cell[0] - self.state.x == -1: return 0

        if next_cell[1] - self.state.y == 1: return 3
        if next_cell[1] - self.state.y == -1: return 2

    def lost_energy_next_step(self, next_cell, state):
        if state.obstacle_info[next_cell[0]][next_cell[1]] == -13:
            return -20
        return state.obstacle_info[next_cell[0]][next_cell[1]]
