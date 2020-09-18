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

print('use heuristic: {}'.format('submit_8_9'))

class Heuristic_1:
    def __init__(self):

        self.state = None
        self.des = None
        self.list_gold = None
        self.dijkstra = Dijkstra()

    def act(self, state):
        # self.state = self.init_state(state)
        self.state = self.dijkstra.init_state(state)

        if self.state.lastAction == 4 and self.state.energy < 40:
            return 4

        if self.check_des_none() is not None: 
            return 4

        if self.check_at_des(): # check xem có đang ở vị trí gold
            gold_amount = self.state.gold_info[self.des[0]][self.des[1]]
            if gold_amount > 0:
                if not self.check_di_truoc(gold_amount):
                    return self.dao_vang()
                else:
                    #check di truoc nhung neu đi trước mà new des trùng self.des chứng tỏ map không còn vàng -> đào tiếp 
                    new_des = self.dijkstra.find_cluster_gold(self.state)
                    # print(new_des, self.des)
                    if self.des[0] == new_des[0] and self.des[1] == new_des[1]:
                        return self.dao_vang()
                    else:
                        self.des = new_des

        if self.state.gold_info[self.state.x][self.state.y] > 0:  # trên đường đi lại đi qua 1 mỏ vàng khác -> đào luôn
            if not self.check_di_truoc(self.state.gold_info[self.state.x][self.state.y]):
                return self.dao_vang()

        self.path_to_des = self.state.path[self.des[0]][self.des[1]]
        self.path_to_des.append(self.des)  # không được phép xóa , khi nó gần sát des thì path_to_des chỉ có mình (state.x, state.y)
        next_cell = self.path_to_des[1]

        if -self.lost_energy_next_step(next_cell, self.state)  >= self.state.energy:
            return 4
        
        action = self.convert_point_to_action(next_cell)
    
        return action 

    def dao_vang(self):
        if self.state.energy > 5:
            return 5
        else:
            return 4

    def check_des_none(self):
        if len(self.state.mapInfo.golds) == 0: return 4

        if self.des is None:    
            self.des = self.dijkstra.find_cluster_gold(self.state) # ban đầu khởi tạo sẽ chưa có des
                
        elif self.state.gold_info[self.des[0]][self.des[1]] == 0: # mỏ vàng đang định đi đến nhưng đã bị đào hết
                self.des = self.dijkstra.find_cluster_gold(self.state)

        if self.des is None:
            return 4 # hết vàng rồi thì k làm gì nữa

    def check_di_truoc(self, gold_amount):
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

    # def find_cluster_gold(self):

    #     # if self.list_gold:
    #     #     return self.list_gold.pop()

    #     # list_gold_sorted = []
    #     # max_cluster_gold = -sys.maxsize
    #     # optimize_cluster_idx = -1

    #     # if len(self.state.mapInfo.golds) > 5:
    #     #     all_list_gold = list(combinations(self.state.mapInfo.golds, 1))
    #     #     print(len(all_list_gold))
            
    #     #     for cluster_idx, list_gold in enumerate(all_list_gold):
    #     #         # print(cluster_idx)
                

    #     #         state = copy.deepcopy(self.state)
    #     #         state = self.init_state(state)
    #     #         state.mapInfo.golds = list(list_gold)

    #     #         list_gold_sorted_temp = []
    #     #         gold = 0
    #     #         num_step = 0

    #     #         while state.mapInfo.golds:
    #     #             # print(len(state.mapInfo.golds))
    #     #             optimize_idx, energy, num_step_ = self.find_gold(state)

    #     #             cell = state.mapInfo.golds.pop(optimize_idx)
    #     #             gold += cell['amount']
    #     #             num_step += num_step_
    #     #             list_gold_sorted_temp += [[cell['posx'], cell['posy']]] + list_gold_sorted_temp
                    
    #     #             #update state
    #     #             state.x = cell['posx']
    #     #             state.y = cell['posy']
    #     #             state.energy = energy

    #     #             #update obstacle_info
    #     #             for point in state.path[cell['posx']][cell['posy']]:
    #     #                 #bẫy đi qua rồi mất lun
    #     #                 if state.obstacle_info[point[0]][point[1]] == -10:
    #     #                     state.obstacle_info[point[0]][point[1]] = -1

    #     #                 #update đầm lầy
    #     #                 if state.obstacle_info[point[0]][point[1]] in [-5, -20, -40, -100]:
    #     #                     if state.obstacle_info[point[0]][point[1]] == -5:
    #     #                         state.obstacle_info[point[0]][point[1]] = -20

    #     #                     elif state.obstacle_info[point[0]][point[1]] == -20:
    #     #                         state.obstacle_info[point[0]][point[1]] = -40

    #     #                     elif state.obstacle_info[point[0]][point[1]] == -40:
    #     #                         state.obstacle_info[point[0]][point[1]] = -1000
                    
    #     #             state.obstacle_info[cell['posx']][cell['posy']] = -1 # vang dao het roi nen thanh dat -4 -> -1
                    
    #     #             #update gold_info
    #     #             state.gold_info[cell['posx']][cell['posy']] = 0


    #     #         if max_cluster_gold < gold/num_step:
    #     #             list_gold_sorted = list_gold_sorted_temp

    #         # if list_gold_sorted:
    #         #     self.list_gold = list_gold_sorted
    #         #     return self.list_gold.pop()

    #     tic = time.time()
    #     optimize_idx, _, _ = self.find_gold(self.state)
    #     print('find gold time: {}'.format(time.time() - tic))
    #     # print(optimize_idx)
    #     # print(self.state.mapInfo.golds)
    #     optimize_cell = self.state.mapInfo.golds[optimize_idx]
    #     optimize_cell = [optimize_cell['posx'], optimize_cell['posy']]

    #     return optimize_cell

    # def find_gold(self, state):

    #     '''find biggest gold/num_step_to_gold'''
    #     max_gold = -sys.maxsize
    #     optimize_idx = -1
    #     num_step = -1
    #     energy = state.energy
    #     for i, cell in enumerate(state.mapInfo.golds):
    #         num_step_to_gold, energy_temp = self.count_step(state, [cell['posx'],cell['posy']])
    #         # print('model: ', num_step_to_gold, cell['amount'])

    #         if max_gold < cell['amount']/num_step_to_gold:
    #             optimize_idx = i
    #             energy = energy_temp
    #             max_gold = cell['amount']/num_step_to_gold
    #             num_step = num_step_to_gold
    #     # print('model: x: {}, y: {}, num_step: {}'.format(max_gold_x, max_gold_y, n))        

    #     return optimize_idx, energy , num_step 
        
    # def count_step(self, state, gold_potision):
    #     energy = state.energy

    #     path_to_des = state.path[gold_potision[0]][gold_potision[1]]
    #     path_to_des.append(gold_potision)
    #     path_to_des = path_to_des[1:]

    #     num_step = 0

    #     for next_cell in path_to_des:
    #         if -self.lost_energy_next_step(next_cell, state)  > energy:
    #             for nang_luong_hoi in (4,3,2):
    #                 if energy < 40:
    #                     num_step += 1
    #                     energy += 50//nang_luong_hoi
    #                     energy = min(50, energy)

    #         energy += self.lost_energy_next_step(next_cell, state)
    #         num_step += 1

    #     gold_amount = state.gold_info[gold_potision[0], gold_potision[1]]
    #     while gold_amount > 0:
    #         if 5 >= energy:
    #             for nang_luong_hoi in (4,3,2):
    #                 if energy < 40:
    #                     num_step += 1
    #                     energy += 50//nang_luong_hoi
    #                     energy = min(50, energy)
    #         energy += -5
    #         num_step += 1
    #         gold_amount -= 50

    #     if num_step == 0: return 1, energy
    #     return num_step, energy


