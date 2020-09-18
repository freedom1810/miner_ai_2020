import sys
import numpy as np
import copy
import time

from itertools import combinations , permutations # tổ hợp, chỉnh hợp

try:
    from GAME_SOCKET_DUMMY_RANDOM import GameSocket #in testing version, please use GameSocket instead of GAME_SOCKET_DUMMY
except:
    from GAME_SOCKET import GameSocket 
    
from MINER_STATE import State

TreeID = 1
TrapID = 2
SwampID = 3

class Dijkstra:
    def __init__(self):
        self.list_gold = []

    def init_state(self, state):
        state.obstacle_info = self.create_obstacle_info(state) # khởi tạo mảng 2 chiều về thông tin chướng ngoại vật
        state.gold_info = self.create_gold_info(state) # khởi tạo mảng 2 chiều về thông tin vàng

        state.graph = self.create_graph(state.obstacle_info) # khởi tạo graph tình chi phí đường đi giữa các điểm theo năng lượng
        # tic = time.time()
        state.path = self.dijkstra([state.x, state.y], state.graph, state.mapInfo.golds) # tính đường đi ngắn nhất từ vị trí hiện tại tới tất cả vị trí khác
        # print('dijkstra time: {}'.format(time.time() - tic))

        return state

    def create_obstacle_info(self, state):
        view = np.zeros([state.mapInfo.max_x + 1, state.mapInfo.max_y + 1], dtype=int) - 1
        for cell in state.mapInfo.obstacles:
            if cell['value'] == 0:
                view[cell["posx"]][cell["posy"]] = -13
            elif cell['value'] == -100:
                view[cell["posx"]][cell["posy"]] = -1000
            else:
                view[cell["posx"]][cell["posy"]] = cell['value']

        for cell in state.mapInfo.golds:
            view[cell["posx"]][cell["posy"]] = -4
        
        return view

    def create_gold_info(self, state):
        view = np.zeros([state.mapInfo.max_x + 1, state.mapInfo.max_y + 1], dtype=int)
        for cell in state.mapInfo.golds:
            view[cell["posx"]][cell["posy"]] = cell['amount']
        return view

    def create_graph(self, obstacle_info):
        graph = np.zeros([189, 189])

        for i in range(21):
            for j in range(9):
                if i - 1 >= 0:
                    x = i - 1
                    y = j
                    graph[i + j*21][x + y*21] =  17 - obstacle_info[x][y]

                if i + 1 < 21:
                    x = i + 1
                    y = j
                    graph[i + j*21][x + y*21] =  17 - obstacle_info[x][y]
                
                if j - 1 >= 0:
                    x = i
                    y = j - 1
                    graph[i + j*21][x + y*21] =  17 - obstacle_info[x][y]
                
                if j + 1 < 9:
                    x = i
                    y = j + 1
                    graph[i + j*21][x + y*21] =  17 - obstacle_info[x][y]
        # print(graph)
        return graph    

    def dijkstra(self, src, graph, list_des):
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import shortest_path
        graph = csr_matrix(graph)

        dist_matrix, predecessors = shortest_path(csgraph=graph, 
                                        directed=True, 
                                        return_predecessors=True,
                                        method = 'D')
        # 
        # dist_matrix

        path = predecessors
        # print(path)
        return path 

    def lost_energy_next_step(self, next_cell, state):
        if state.obstacle_info[next_cell[0]][next_cell[1]] == -13:
            return -20
        return state.obstacle_info[next_cell[0]][next_cell[1]]

    def find_n_gold(self, state, n_gold = 3):
        permutations_position = list(permutations(state.mapInfo.golds, n_gold))
        # print(permutations_position)
        
        max_gold = -sys.maxsize
        optimize_idx = -1

        for i, p in enumerate(permutations_position):
            # print(i)
            state_temp = copy.deepcopy(state)
            gold = 0 
            num_step = 0
            for cell in p:

                num_step_to_gold, energy_temp = self.count_step(state_temp, cell['posx'] + cell['posy']*21)

                state_temp.energy = energy_temp
                state_temp.x = cell['posx']
                state_temp.y = cell['posy']

                gold += cell['amount']
                num_step += num_step_to_gold


            if max_gold < gold/num_step:
                optimize_idx = i
                max_gold = gold/num_step

        # print(optimize_idx)
        # print(len(permutations_position))
        self.list_gold = list(permutations_position[optimize_idx])[::-1]
        # print(self.list_gold)
        # print(self.list_gold)

    def find_cluster_gold(self, state):
        
        optimize_idx, _, _ = self.find_gold(state)
        optimize_cell = state.mapInfo.golds[optimize_idx]
        optimize_cell = [optimize_cell['posx'], optimize_cell['posy']]

        return optimize_cell

    def find_gold(self, state):

        '''find biggest gold/num_step_to_gold'''
        max_gold = -sys.maxsize
        optimize_idx = -1
        num_step = -1
        energy = state.energy
        
        for i, cell in enumerate(state.mapInfo.golds):
            num_step_to_gold, energy_temp = self.count_step(state, cell['posx'] + cell['posy']*21)

            if max_gold < cell['amount']/num_step_to_gold:
                optimize_idx = i
                energy = energy_temp
                max_gold = cell['amount']/num_step_to_gold
                num_step = num_step_to_gold
        # print('model: x: {}, y: {}, num_step: {}'.format(max_gold_x, max_gold_y, n))        

        return optimize_idx, energy , num_step 
        
    def count_step(self, state, gold_position_f):
        energy = state.energy
        # print('count_step energy: {}'.format(energy))

        cur_position_f = state.x + state.y*21
        num_step = 0

        while cur_position_f != state.path[cur_position_f][gold_position_f]:
            
            if state.path[cur_position_f][gold_position_f] == -9999:  # cur_position_f trùng gold_position
                break

            
            # next_position_f = state.path[cur_position_f][gold_position]
            next_position_f = state.path[gold_position_f][cur_position_f]
            next_position = [next_position_f%21, next_position_f//21]

            if -self.lost_energy_next_step(next_position, state)  > energy:
                for nang_luong_hoi in (4,3,2):
                    if energy < 40:
                        num_step += 1
                        energy += 50//nang_luong_hoi
                        energy = min(50, energy)

            energy += self.lost_energy_next_step(next_position, state)
            num_step += 1

            cur_position_f = next_position_f

        next_position = [gold_position_f%21, gold_position_f//21]

        if -self.lost_energy_next_step(next_position, state)  > energy:
            for nang_luong_hoi in (4,3,2):
                if energy < 40:
                    num_step += 1
                    energy += 50//nang_luong_hoi
                    energy = min(50, energy)

        energy += self.lost_energy_next_step(next_position, state)
        num_step += 1

        gold_amount = state.gold_info[gold_position_f%21, gold_position_f//21]

        while gold_amount > 0:
            if 5 >= energy:
                for nang_luong_hoi in (4,3,2):
                    if energy < 40:
                        num_step += 1
                        energy += 50//nang_luong_hoi
                        energy = min(50, energy)
            energy += -5
            num_step += 1
            gold_amount -= 50

        if num_step == 0: return 1, energy
        return num_step, energy


