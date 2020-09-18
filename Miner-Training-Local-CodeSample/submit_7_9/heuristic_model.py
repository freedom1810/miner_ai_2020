import sys
import numpy as np
import copy

from itertools import combinations 

try:
    from GAME_SOCKET_DUMMY import GameSocket #in testing version, please use GameSocket instead of GAME_SOCKET_DUMMY
except:
    from GAME_SOCKET import GameSocket 
    
from MINER_STATE import State

TreeID = 1
TrapID = 2
SwampID = 3

print('use heuristic: {}'.format('submit_7_9'))

class Heuristic_1:
    def __init__(self):

        self.state = None
        self.des = None
        self.list_gold = None

    def act(self, state):
        self.state = self.init_state(state)

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
                    new_des = self.find_cluster_gold()
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

    def init_state(self, state):
        # self.state = state
        state.obstacle_info = self.create_obstacle_info(state) # khởi tạo mảng 2 chiều về thông tin chướng ngoại vật
        state.gold_info = self.create_gold_info(state) # khởi tạo mảng 2 chiều về thông tin vàng

        state.graph = self.create_graph(state.obstacle_info) # khởi tạo graph tình chi phí đường đi giữa các điểm theo năng lượng
        state.path = self.dijkstra([state.x, state.y], state.graph, state.mapInfo.golds) # tính đường đi ngắn nhất từ vị trí hiện tại tới tất cả vị trí khác

        return state

    def dao_vang(self):
        if self.state.energy > 5:
            return 5
        else:
            return 4

    def check_des_none(self):
        if len(self.state.mapInfo.golds) == 0: return 4

        if self.des is None:
            self.des = self.find_cluster_gold() # ban đầu khởi tạo sẽ chưa có des
        
        elif self.state.gold_info[self.des[0]][self.des[1]] == 0: # mỏ vàng đang định đi đến nhưng đã bị đào hết
                self.des = self.find_cluster_gold()

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
        
        graph = []
        for i in range(21):
            graph.append([])
            for j in range(9):
                graph[i].append([])
                if i - 1 >= 0:
                    x = i - 1
                    y = j
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - obstacle_info[x][y]))

                if i + 1 < 21:
                    x = i + 1
                    y = j
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - obstacle_info[x][y]))
                
                if j - 1 >= 0:
                    x = i
                    y = j - 1
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - obstacle_info[x][y]))
                
                if j + 1 < 9:
                    x = i
                    y = j + 1
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - obstacle_info[x][y]))
        return graph    

    def dijkstra(self, src, graph, list_des):
        list_des = [[cell['posx'], cell['posy']] for cell in list_des]

        def minDistance(dist, sptSet): 
   
            # Initilaize minimum distance for next node 
            min = sys.maxsize
    
            # Search not nearest vertex not in the  
            # shortest path tree 
            for i in range(21):
                for j in range(9): 
                    # print(dist[i][j])
                    if dist[i][j] < min and sptSet[i][j] == False: 
                        min = dist[i][j] 
                        min_index_i = i
                        min_index_j = j 
            try:
                return min_index_i, min_index_j
            except:
                pass
            return None 
            
        def get_distance(u, v):
            if ((u[0] - v[0])**2 + (u[1] - v[1])**2) == 1:
                for v_ in graph[u[0]][u[1]]:
                    if v_[0] == v[0] and v_[1] == v[1] :
                        return v_[2]
            return -1

        path = []
        for i in range(21):
            path.append([])
            for j in range(9):
                path[i].append([])

        # path[src[0]][src[1]].append([])

        dist = []
        for i in range(21):
            dist.append([])
            for j in range(9):
                dist[i].append(sys.maxsize)
        dist[src[0]][src[1]] = 0


        sptSet = []
        for i in range(21):
            sptSet.append([])
            for j in range(9):
                sptSet[i].append(False)
                
        for _ in range(21*9):
            u = minDistance(dist, sptSet)
            sptSet[u[0]][u[1]] = True

            for i in (-1,0,1):
                for j in (-1,0,1):
                    v = [u[0] + i, u[1] + j]

                    distance = get_distance(u, v)
                    if distance != -1 and \
                        sptSet[v[0]][v[1]] == False and \
                        dist[v[0]][v[1]] > dist[u[0]][u[1]] + distance:

                        dist[v[0]][v[1]] = dist[u[0]][u[1]] + distance
                        path[v[0]][v[1]] = path[u[0]][u[1]] + [[u[0], u[1]]]

                        if v in list_des: 
                            list_des.remove(v)
                            if len(list_des) == 0:
                                return path

        return path 

    def lost_energy_next_step(self, next_cell, state):
        if state.obstacle_info[next_cell[0]][next_cell[1]] == -13:
            return -20
        return state.obstacle_info[next_cell[0]][next_cell[1]]

    def find_cluster_gold(self):

        # if self.list_gold:
        #     return self.list_gold.pop()

        # list_gold_sorted = []
        # max_cluster_gold = -sys.maxsize
        # optimize_cluster_idx = -1

        # if len(self.state.mapInfo.golds) > 5:
        #     all_list_gold = list(combinations(self.state.mapInfo.golds, 1))
        #     print(len(all_list_gold))
            
        #     for cluster_idx, list_gold in enumerate(all_list_gold):
        #         # print(cluster_idx)
                

        #         state = copy.deepcopy(self.state)
        #         state = self.init_state(state)
        #         state.mapInfo.golds = list(list_gold)

        #         list_gold_sorted_temp = []
        #         gold = 0
        #         num_step = 0

        #         while state.mapInfo.golds:
        #             # print(len(state.mapInfo.golds))
        #             optimize_idx, energy, num_step_ = self.find_gold(state)

        #             cell = state.mapInfo.golds.pop(optimize_idx)
        #             gold += cell['amount']
        #             num_step += num_step_
        #             list_gold_sorted_temp += [[cell['posx'], cell['posy']]] + list_gold_sorted_temp
                    
        #             #update state
        #             state.x = cell['posx']
        #             state.y = cell['posy']
        #             state.energy = energy

        #             #update obstacle_info
        #             for point in state.path[cell['posx']][cell['posy']]:
        #                 #bẫy đi qua rồi mất lun
        #                 if state.obstacle_info[point[0]][point[1]] == -10:
        #                     state.obstacle_info[point[0]][point[1]] = -1

        #                 #update đầm lầy
        #                 if state.obstacle_info[point[0]][point[1]] in [-5, -20, -40, -100]:
        #                     if state.obstacle_info[point[0]][point[1]] == -5:
        #                         state.obstacle_info[point[0]][point[1]] = -20

        #                     elif state.obstacle_info[point[0]][point[1]] == -20:
        #                         state.obstacle_info[point[0]][point[1]] = -40

        #                     elif state.obstacle_info[point[0]][point[1]] == -40:
        #                         state.obstacle_info[point[0]][point[1]] = -1000
                    
        #             state.obstacle_info[cell['posx']][cell['posy']] = -1 # vang dao het roi nen thanh dat -4 -> -1
                    
        #             #update gold_info
        #             state.gold_info[cell['posx']][cell['posy']] = 0


        #         if max_cluster_gold < gold/num_step:
        #             list_gold_sorted = list_gold_sorted_temp

            # if list_gold_sorted:
            #     self.list_gold = list_gold_sorted
            #     return self.list_gold.pop()

        optimize_idx, _, _ = self.find_gold(self.state)
        # print(optimize_idx)
        # print(self.state.mapInfo.golds)
        optimize_cell = self.state.mapInfo.golds[optimize_idx]
        optimize_cell = [optimize_cell['posx'], optimize_cell['posy']]

        return optimize_cell

    def find_gold(self, state):

        '''find biggest gold/num_step_to_gold'''
        max_gold = -sys.maxsize
        optimize_idx = -1
        num_step = -1
        energy = state.energy
        for i, cell in enumerate(state.mapInfo.golds):
            num_step_to_gold, energy_temp = self.count_step(state, [cell['posx'],cell['posy']])
            # print('model: ', num_step_to_gold, cell['amount'])

            if max_gold < cell['amount']/num_step_to_gold:
                optimize_idx = i
                energy = energy_temp
                max_gold = cell['amount']/num_step_to_gold
                num_step = num_step_to_gold
        # print('model: x: {}, y: {}, num_step: {}'.format(max_gold_x, max_gold_y, n))        

        return optimize_idx, energy , num_step 
        
    def count_step(self, state, gold_potision):
        energy = state.energy

        path_to_des = state.path[gold_potision[0]][gold_potision[1]]
        path_to_des.append(gold_potision)
        path_to_des = path_to_des[1:]

        num_step = 0

        for next_cell in path_to_des:
            if -self.lost_energy_next_step(next_cell, state)  > energy:
                for nang_luong_hoi in (4,3,2):
                    if energy < 40:
                        num_step += 1
                        energy += 50//nang_luong_hoi
                        energy = min(50, energy)

            energy += self.lost_energy_next_step(next_cell, state)
            num_step += 1

        gold_amount = state.gold_info[gold_potision[0], gold_potision[1]]
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


