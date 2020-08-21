from MINER_STATE import State
import numpy as np
from MapInfo import MapInfo
import sys

class PlayerInfo:
    def __init__(self, id):
        self.playerId = id
        self.score = 0
        self.energy = 0
        self.posx = 0
        self.posy = 0
        self.lastAction = -1
        self.status = 0
        self.freeCount = 0

#create graph
# dfs đến tất cả vàng
# đi đến mỏ gần nhất
class Bot1:
    ACTION_GO_LEFT = 0
    ACTION_GO_RIGHT = 1
    ACTION_GO_UP = 2
    ACTION_GO_DOWN = 3
    ACTION_FREE = 4
    ACTION_CRAFT = 5

    def __init__(self, id):
        self.state = State()
        self.info = PlayerInfo(id)
        self.des = None
        self.step_count = 0

    def next_action(self):
        self.step_count += 1
        # print('energy: {}'.format(self.info.energy))
        
        # return 4

        if self.info.lastAction == 4 and self.info.energy < 40:
            return 4

        self.graph = self.create_graph()
        # print('graph: ', self.graph, '\n\n\n')
        self.path = self.dijkstra([self.info.posx, self.info.posy])

        if self.des is None: 
            self.des = self.find_gold()

        if self.check_den_dich(): # đang ở vị trí gold
            gold_amount = self.get_gold_amount(self.des[0], self.des[1])
            if gold_amount > 0:
                if self.info.energy > 5:
                    return 5
                else:
                    return 4
                    
            self.des = self.find_gold()

        # print(self.path[self.des[0]][self.des[1]])
        self.path_to_des = self.path[self.des[0]][self.des[1]]
        self.path_to_des.append(self.des)

        self.path_to_des = self.path_to_des[::-1][:-1]
        next_cell = self.path_to_des.pop()

        # print('lost_energy: {}'.format(-self.lost_energy_next_step(next_cell)))

        if -self.lost_energy_next_step(next_cell)  >= self.info.energy:
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
        return self.info.posx == self.des[0] and self.info.posy == self.des[1]

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
        if next_cell[0] - self.info.posx == 1: return 1
        if next_cell[0] - self.info.posx == -1: return 0

        if next_cell[1] - self.info.posy == 1: return 3
        if next_cell[1] - self.info.posy == -1: return 2


    def find_gold(self):
        # ''' find nearest gold'''
        min_dis = sys.maxsize
        # print(self.state.mapInfo.golds)
        for cell in self.state.mapInfo.golds:
            if min_dis > ((self.info.posx - cell['posx'])**2 + (self.info.posy - cell['posy'])**2) and cell['amount'] > 0:
                min_dis_x = cell['posx']
                min_dis_y = cell['posy']
                min_dis = (self.info.posx - cell['posx'])**2 + (self.info.posy - cell['posy'])**2
        # print('bot1: {}, {}'.format(min_dis_x, min_dis_y))
        return [min_dis_x, min_dis_y]

        ''' find biggest gold'''
        # max_gold = -sys.maxsize
        # for cell in self.state.mapInfo.golds:
        #     if max_gold < cell['amount']:
        #         max_gold_x = cell['posx']
        #         max_gold_y = cell['posy']
        #         max_gold = cell['amount']
        # print(max_gold_x, max_gold_y)
        
        '''find biggest gold/num_step_to_gold'''
        # max_gold = -sys.maxsize
        # for cell in self.state.mapInfo.golds:
        #     num_step_to_gold = len(self.path[cell['posx']][cell['posy']]) + 1
        #     if max_gold < cell['amount']/num_step_to_gold:
        #         max_gold_x = cell['posx']
        #         max_gold_y = cell['posy']
        #         max_gold = cell['amount']/num_step_to_gold
        # print(max_gold_x, max_gold_y)        

        # return [max_gold_x, max_gold_y]



    def new_game(self, data):
        try:
            self.state.init_state(data)
            self.create_graph()
        except Exception as e:
            import traceback
            traceback.print_exc()

    def new_state(self, data):
        # action = self.next_action();
        # self.socket.send(action)
        try:
            self.state.update_state(data)
        except Exception as e:
            import traceback
            traceback.print_exc()