import sys
import numpy as np
from GAME_SOCKET import GameSocket #in testing version, please use GameSocket instead of GAME_SOCKET_DUMMY
from MINER_STATE import State
import copy

TreeID = 1
TrapID = 2
SwampID = 3

class Heuristic_1:
    def __init__(self):

        self.state = None
        self.des = None


    def act(self, state):
        # return 4
        # print('step')
        self.state = state
        self.obstacle_info = self.create_obstacle_info() # khởi tạo mảng 2 chiều về thông tin chướng ngoại vật
        self.gold_info = self.create_gold_info() # khởi tạo mảng 2 chiều về thông tin vàng

        if self.state.lastAction == 4 and self.state.energy < 40:
            return 4

        self.graph = self.create_graph() # khởi tạo graph tình chi phí đường đi giữa các điểm theo năng lượng
        self.path = self.dijkstra([self.state.x, self.state.y]) # tính đường đi ngắn nhất từ vị trí hiện tại tới tất cả vị trí khác

        if self.des is None:
            self.des = self.find_gold() # ban đầu khởi tạo sẽ chưa có des
        else:
            if self.gold_info[self.des[0]][self.des[1]] == 0: # mỏ vàng đang định đi đến nhưng đã bị đào hết
                self.des = self.find_gold()

        # print('self.des: ', self.des)
        if self.des is None:
            return 4 # hết vàng rồi thì k làm gì nữa


        if self.check_den_dich(): # check xem có đang ở vị trí gold
            gold_amount = self.gold_info[self.des[0]][self.des[1]]
            if gold_amount > 0:
                if not self.check_di_truoc(gold_amount):
                    if self.state.energy > 5:
                        return 5
                    else:
                        return 4
                else:
                    new_des = self.find_gold()
                    # print(new_des, self.des)
                    if self.des[0] == new_des[0] and self.des[1] == new_des[1]:
                        if self.state.energy > 5:
                            return 5
                        else:
                            return 4
                    else:
                        self.des = new_des

        if self.gold_info[self.state.x][self.state.y] > 0:  # trên đường đi lại đi qua 1 mỏ vàng khác -> đào luôn
            if self.state.energy > 5:
                if not self.check_di_truoc(self.gold_info[self.state.x][self.state.y]):
                    return 5
            else:
                return 4

        self.path_to_des = self.path[self.des[0]][self.des[1]]
        self.path_to_des.append(self.des)  # không được phép xóa , khi nó gần sát des thì path_to_des chỉ có mình (state.x, state.y)
        next_cell = self.path_to_des[1]

        if -self.lost_energy_next_step(next_cell)  >= self.state.energy:
            return 4
        
        action = self.convert_point_to_action(next_cell)
        # print(state.x,state.y, next_cell, self.des)
    
        return action 

    def check_di_truoc(self, gold_amount):
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

    def create_obstacle_info(self):
        view = np.zeros([self.state.mapInfo.max_x + 1, self.state.mapInfo.max_y + 1], dtype=int) - 1
        for cell in self.state.mapInfo.obstacles:
            if cell['value'] == 0:
                view[cell["posx"]][cell["posy"]] = -13
            elif cell['value'] == -100:
                view[cell["posx"]][cell["posy"]] = -1000
            else:
                view[cell["posx"]][cell["posy"]] = cell['value']

        for cell in self.state.mapInfo.golds:
            view[cell["posx"]][cell["posy"]] = -4
        
        return view

    def create_gold_info(self):
        view = np.zeros([self.state.mapInfo.max_x + 1, self.state.mapInfo.max_y + 1], dtype=int)
        for cell in self.state.mapInfo.golds:
            view[cell["posx"]][cell["posy"]] = cell['amount']
        return view

    def create_graph(self):
        
        graph = []
        for i in range(21):
            graph.append([])
            for j in range(9):
                graph[i].append([])
                if i - 1 >= 0:
                    x = i - 1
                    y = j
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - self.obstacle_info[x][y]))

                if i + 1 < 21:
                    x = i + 1
                    y = j
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - self.obstacle_info[x][y]))
                
                if j - 1 >= 0:
                    x = i
                    y = j - 1
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - self.obstacle_info[x][y]))

                
                if j + 1 < 9:
                    x = i
                    y = j + 1
                    # if self.obstacle_info[x][y] != -1000:
                    graph[i][j].append((x, y, 17 - self.obstacle_info[x][y]))
        return graph    

    def dijkstra(self, src):

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
                for v_ in self.graph[u[0]][u[1]]:
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

        return path 

    def check_den_dich(self):
        return self.state.x == self.des[0] and self.state.y == self.des[1]

    def lost_energy_next_step(self, next_cell):
        if self.obstacle_info[next_cell[0]][next_cell[1]] == -13:
            return -20
        return self.obstacle_info[next_cell[0]][next_cell[1]]
    
    def convert_point_to_action(self, next_cell):
        if next_cell[0] - self.state.x == 1: return 1
        if next_cell[0] - self.state.x == -1: return 0

        if next_cell[1] - self.state.y == 1: return 3
        if next_cell[1] - self.state.y == -1: return 2

    def find_gold(self):
        ''' find nearest gold'''
        # min_dis = sys.maxsize
        # # print(self.state.mapInfo.golds)
        # for cell in self.state.mapInfo.golds:
        #     if min_dis > ((self.state.x - cell['posx'])**2 + (self.state.y - cell['posy'])**2) and cell['amount'] > 0:
        #         min_dis_x = cell['posx']
        #         min_dis_y = cell['posy']
        #         min_dis = (self.state.x - cell['posx'])**2 + (self.state.y - cell['posy'])**2
        # # print(min_dis_x, min_dis_y)
        # return [min_dis_x, min_dis_y]

        ''' find biggest gold'''
        # max_gold = -sys.maxsize
        # for cell in self.state.mapInfo.golds:
        #     if max_gold < cell['amount']:
        #         max_gold_x = cell['posx']
        #         max_gold_y = cell['posy']
        #         max_gold = cell['amount']
        # print(max_gold_x, max_gold_y)
        # return [max_gold_x, max_gold_y]
        
        '''find biggest gold/num_step_to_gold'''
        max_gold = -sys.maxsize
        for cell in self.state.mapInfo.golds:
            num_step_to_gold = self.count_step([cell['posx'],cell['posy']])
            # print('model: ', num_step_to_gold, cell['amount'])
            if max_gold < cell['amount']/num_step_to_gold:
                max_gold_x = cell['posx']
                max_gold_y = cell['posy']
                max_gold = cell['amount']/num_step_to_gold
        # print('model: {}, {}'.format(max_gold_x, max_gold_y))        

        return [max_gold_x, max_gold_y]

    def count_step(self, gold_potision):
        energy = self.state.energy

        path_to_des = self.path[gold_potision[0]][gold_potision[1]]
        path_to_des.append(gold_potision)
        path_to_des = path_to_des[::-1][:-1]
        
        # next_cell = self.path_to_des.pop()

        num_step = 0
        step = []


        # while path_to_des:
            # next_cell = path_to_des.pop()
        for next_cell in path_to_des:
            if -self.lost_energy_next_step(next_cell)  > energy:
                for nang_luong_hoi in (4,3,2):
                    if energy < 40:
                        num_step += 1
                        energy += 50//nang_luong_hoi
                        energy = min(50, energy)
                        # print(energy)
                        # step.append(4)
                
            energy += self.lost_energy_next_step(next_cell)
            num_step += 1

        gold_amount = self.gold_info[gold_potision[0], gold_potision[1]]
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

            # step.append(next_cell)
        # print(step)

        if num_step == 0: return 1
        return num_step


