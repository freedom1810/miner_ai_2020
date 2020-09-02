import sys
import numpy as np
from sklearn.cluster import DBSCAN


class DbScan():
    
    def __init__(self, state, obstacle_info, gold_info, graph):

        self.state = state
        self.obstacle_info = obstacle_info
        self.gold_info = gold_info
        self.graph = graph

    def run(self):
        self.dbscan_path, self.dbscan_distance = self.create_gold_distance()
        
        def dbscan_dis(x, y):

            return self.dbscan_dis[x[0]][x[1]][y[0]][y[1]] 
        
        list_gold = []
        for cell in self.state.mapInfo.golds:
            list_gold.append([cell['posx'], cell['posy']])
        list_gold = np.array(list_gold)

        dbscan = DBSCAN(n_jobs = 1, eps=6.0, min_samples=1, metric=dbscan_dis).fit_predict(list_gold)

    

    def create_gold_distance():

        dbscan_path = []
        dbscan_distance = []
        for i in range(21):
            dbscan_distance.append([])
            for j in range(9):
                view = np.ones([self.state.mapInfo.max_x + 1, self.state.mapInfo.max_y + 1], dtype=float) * 100
                dbscan_distance[i].append(view)
                

        for i in range(21):
            dbscan_path.append([])
            for j in range(9):
                dbscan_path[i].append(None)

                if self.gold_info[i][j] > =50:
                    dbscan_path[i][j] = self.dijkstra([i, j])

                    for cell in self.state.mapInfo.golds:
                        if cell['posx'] == i and cell['posy'] == j:
                            continue

                        gold_potision = [cell['posx'],cell['posy']]
                        num_step_to_gold = self.count_step(gold_potision, dbscan_path[i][j])

                        dbscan_distance[i][j][cell['posx']][cell['posy']] = cell['amount'] / num_step_to_gold

        return dbscan_path, dbscan_distance

    def dijkstra(self, src, des):

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

    def count_step(self, gold_potision, path):
        energy = 50

        path_to_des = path[gold_potision[0]][gold_potision[1]]
        path_to_des.append(gold_potision)
        path_to_des = path_to_des[1:]

        num_step = 0
        step = []

        for next_cell in path_to_des:
            if -self.lost_energy_next_step(next_cell)  > energy:
                for nang_luong_hoi in (4,3,2):
                    if energy < 40:
                        num_step += 1
                        energy += 50//nang_luong_hoi
                        energy = min(50, energy)

                
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


        if num_step == 0: return 1
        return num_step


    
                    