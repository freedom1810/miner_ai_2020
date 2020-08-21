import sys
import numpy as np
from GAME_SOCKET_DUMMY import GameSocket #in testing version, please use GameSocket instead of GAME_SOCKET_DUMMY
from MINER_STATE import State
import copy
import sys

TreeID = 1
TrapID = 2
SwampID = 3

class Heuristic_1:
    def __init__(self):

        self.state = None
        self.des = None


    def act(self, state):
        # return 4

        self.state = state

        if self.state.lastAction == 4 and self.state.energy < 40:
            return 4

        self.graph = self.create_graph()
        self.path = self.dijkstra([self.state.x, self.state.y])
        # print('graph: ', self.graph, '\n\n\n')

        if self.des is None:
            self.des = self.find_gold()

        if self.check_den_dich(): # đang ở vị trí gold
            gold_amount = self.get_gold_amount(self.des[0], self.des[1])
            if gold_amount > 0:
                if self.state.energy > 5:
                    return 5
                else:
                    return 4
                    
            self.des = self.find_gold()


        self.path_to_des = self.path[self.des[0]][self.des[1]]
        self.path_to_des.append(self.des)
        # self.path_to_des = self.path_to_des[::-1][:-1]
        # next_cell = self.path_to_des.pop()
        next_cell = self.path_to_des[1]

        if -self.lost_energy_next_step(next_cell)  > self.state.energy:
            return 4
        
        action = self.convert_point_to_action(next_cell)

    
        return action 

    def get_obstacle_value(self, x, y):  # Get the kind of the obstacle at cell(x,y)
        for cell in self.state.mapInfo.obstacles:
            if x == cell["posx"] and y == cell["posy"]:
                if cell["value"] == 0:
                    return -13
                if cell["value"] == -100:
                    return -1000
                return cell["value"]
        
        return -1

    def get_gold_position(self, x, y):  # Get the kind of the obstacle at cell(x,y)
        for cell in self.state.mapInfo.golds:
            if x == cell["posx"] and y == cell["posy"]:
                return -4
        
        return None

    def get_gold_amount(self, x, y):  # Get the kind of the obstacle at cell(x,y)
        for cell in self.state.mapInfo.golds:
            if x == cell["posx"] and y == cell["posy"]:
                return cell["amount"]
        
        return 0

    def create_graph(self):
        
        graph = []
        for i in range(21):
            graph.append([])
            for j in range(9):
                graph[i].append([])
                if i - 1 >= 0:
                    x = i - 1
                    y = j
                    if self.get_gold_position(x, y) is not None:
                        graph[i][j].append((x, y, 17 - -4))
                    else:
                        graph[i][j].append((x, y, 17 - self.get_obstacle_value(x, y)))

                if i + 1 < 21:
                    x = i + 1
                    y = j
                    if self.get_gold_position(x, y) is not None:
                        graph[i][j].append((x, y, 17 - -4))
                    else:
                        graph[i][j].append((x, y, 17 - self.get_obstacle_value(x, y)))
                
                if y - 1 >= 0:
                    x = i
                    y = j - 1
                    if self.get_gold_position(x, y) is not None:
                        graph[i][j].append((x, y, 17 - -4))
                    else:
                        graph[i][j].append((x, y, 17 - self.get_obstacle_value(x, y)))

                
                if y + 1 < 9:
                    x = i
                    y = j + 1
                    if self.get_gold_position(x, y) is not None:
                        graph[i][j].append((x, y, 17 - -4))
                    else:
                        graph[i][j].append((x, y, 17 - self.get_obstacle_value(x, y)))

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
    
            return min_index_i, min_index_j

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

        # sptSet[src[0]][src[1]] == True

        for _ in range(21*9):

            u = minDistance(dist, sptSet)

            sptSet[u[0]][u[1]] = True

            for i in range(21):
                for j in range(9):
                    distance = get_distance(u, [i, j])
                    if distance != -1 and \
                        sptSet[i][j] == False and \
                        dist[i][j] > dist[u[0]][u[1]] + distance:

                        dist[i][j] = dist[u[0]][u[1]] + distance
                        path[i][j] = path[u[0]][u[1]] + [[u[0], u[1]]]

        # print(path) 
        return path 

    def check_den_dich(self):
        return self.state.x == self.des[0] and self.state.y == self.des[1]

    def lost_energy_next_step(self, next_cell):

        for cell in self.state.mapInfo.obstacles:
            if next_cell[0] == cell["posx"] and next_cell[1] == cell["posy"]:
                if cell["value"] == 0:
                    return -20
                elif cell["value"] == -100:
                    return -100
                else:
                    return cell["value"]
                    
        
        for cell in self.state.mapInfo.golds:
            if next_cell[0] == cell["posx"] and next_cell[1] == cell["posy"]:
                return -4
        
        return -1
    
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


        while path_to_des:
            next_cell = path_to_des.pop()
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

            step.append(next_cell)
        # print(step)

        if num_step == 0: return 1
        return num_step


