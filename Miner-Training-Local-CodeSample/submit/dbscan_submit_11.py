import sys
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import pairwise_distances
import copy

class DbScan():
    
    def __init__(self, state, obstacle_info, gold_info, graph, path):

        self.state = state
        self.obstacle_info = obstacle_info
        self.gold_info = gold_info
        self.graph = graph
        self.heuristic_path = path

    def run(self):
        self.dbscan_path, self.dbscan_distance = self.create_gold_distance()
        
        def dbscan_dis(x, y):          
            return max(self.dbscan_distance[int(x[0])][int(x[1])][int(y[0])][int(y[1])] , 
                    self.dbscan_distance[int(y[0])][int(y[1])][int(x[0])][int(x[1])] )
        
        list_gold = []
        for cell in self.state.mapInfo.golds:
            list_gold.append([cell['posx'], cell['posy']])
        self.list_gold = np.array(list_gold, dtype=int)

        list_gold_pairwise = pairwise_distances(self.list_gold, metric=dbscan_dis)
        
        self.dbscan = DBSCAN(n_jobs = 1, eps=5, min_samples=0, metric='precomputed').fit(list_gold_pairwise)

        n_cluster = max(self.dbscan.labels_) + 1

        clusters = []
        for i in range(n_cluster):

            clusters.append(self.list_gold[self.dbscan.labels_ == i])

        self.best_cluster, self.order_point_in_cluster = self.find_cluster(clusters)

    def find_cluster(self, clusters):
        
        #---------------------------------
        def find_des(source, cluster):

            first_point = source
            idx = None
            max_dis = sys.maxsize
            
            for i, point in enumerate(cluster):
                if max_dis > len(self.dbscan_path[point[0]][point[1]][source[0]][source[1]]):
                    max_dis = len(self.dbscan_path[point[0]][point[1]][source[0]][source[1]])
                    first_point = point
                    idx = i
                    
            return first_point, idx
        #---------------------------------

        max_gold = -sys.maxsize
        best_cluster = -1
        order_point_in_cluster = None

        for idx_clus, cluster in enumerate(clusters):
            order_point_in_cluster_ = []

            cluster = list(cluster)
            state = copy.deepcopy(self.state)

            source = [state.x, state.y]
            gold = self.gold_info[source[0]][source[1]]
            des, idx_des = find_des(source, cluster)
            order_point_in_cluster_.append(des)
            cluster.pop(idx_des)
            num_step_, energy_ = self.count_step(des, self.heuristic_path, energy=self.state.energy)
            num_step = num_step_
            energy = energy_
        
            while cluster:
                source = [des[0], des[1]]
                gold += self.gold_info[source[0]][source[1]]
                des, idx_des = find_des(source, cluster)
                order_point_in_cluster_.append(des)
                cluster.pop(idx_des)
                num_step_, energy = self.count_step(des, self.dbscan_path[source[0]][source[1]], energy=energy)
                num_step += num_step_
                
            if max_gold < gold:
                max_gold = gold
                best_cluster = idx_clus
                order_point_in_cluster = copy.deepcopy(order_point_in_cluster_)
        
        return best_cluster, order_point_in_cluster[::-1]

    def create_gold_distance(self):

        dbscan_path = []
        dbscan_distance = []
        for i in range(21):
            dbscan_distance.append([])
            for j in range(9):
                view = np.ones([self.state.mapInfo.max_x + 1, self.state.mapInfo.max_y + 1], dtype=float) * 100000
                dbscan_distance[i].append(view)
                
        for i in range(21):
            dbscan_path.append([])
            for j in range(9):
                dbscan_path[i].append(None)

                if self.gold_info[i][j] >= 50:
                    dbscan_path[i][j] = self.dijkstra([i, j])

                    for cell in self.state.mapInfo.golds:
                        if cell['posx'] == i and cell['posy'] == j:
                            continue

                        gold_potision = [cell['posx'],cell['posy']]
                        num_step_to_gold, _ = self.count_step(gold_potision, dbscan_path[i][j])

                        dbscan_distance[i][j][cell['posx']][cell['posy']] = num_step_to_gold

        return dbscan_path, dbscan_distance

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

    def count_step(self, gold_potision, path, energy = 50):
        # energy = 50

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

        # gold_amount = self.gold_info[gold_potision[0], gold_potision[1]]
        # while gold_amount > 0:
        #     if 5 >= energy:
        #         for nang_luong_hoi in (4,3,2):
        #             if energy < 40:
        #                 num_step += 1
        #                 energy += 50//nang_luong_hoi
        #                 energy = min(50, energy)
        #     energy += -5
        #     num_step += 1
        #     gold_amount -= 50


        if num_step == 0: return 1, energy
        return num_step, energy

    def lost_energy_next_step(self, next_cell):
        if self.obstacle_info[next_cell[0]][next_cell[1]] == -13:
            return -20
        return self.obstacle_info[next_cell[0]][next_cell[1]]


    
                    