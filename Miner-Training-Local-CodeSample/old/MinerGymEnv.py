import os

import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np

# from Config import *
from Config import *


from MinerEnv import MinerEnv, TreeID, TrapID, SwampID
import cv2
from prettytable import PrettyTable
from PIL import ImageFont, ImageDraw, Image

ACTIONS = {0: 'left', 1: 'right', 2: 'up', 3: 'down', 4: 'stand', 5: 'mining',6:'DIE'}
# font = ImageFont.truetype("Data/Roboto-Regular.ttf", 15)
font = ImageFont.load_default()

class MinerGymEnv(gym.Env):
    def __init__(self, HOST, PORT, debug=False):
        self.minerEnv = MinerEnv(HOST,
                                 PORT)
        self.minerEnv.start()
        self.action_space = spaces.Discrete(6)
        self.observation_space = spaces.Discrete(198)
        self.debug= debug
        self.view = None
        self.action = None
        self.reward = None
        self.ob = None
        self.state = self.minerEnv.state

    def print(self, message):
        if self.debug:
            print(message)

    def draw_text(self,mat,text):
        cv2_im_rgb = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)

        draw = ImageDraw.Draw(pil_im)

        draw.text((10, 10),text, font=font)

        cv2_im_processed = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
        return cv2_im_processed
        # cv2.imwrite("result.png", cv2_im_processed)


    def step(self, action):
        self.minerEnv.step(str(action))
        self.status = self.minerEnv.get_state()
        reward = self.get_reward()
        ob = self.get_state()
        episode_over = self.check_terminate()
        self.ob = ob
        self.action = action
        self.reward = reward
        if self.debug:
            self.render()
        # if episode_over:
        #     print('Score : {}'.format(self.minerEnv.state.score))
        return ob, reward, episode_over, {'score':self.minerEnv.state.score ,'action':action}

    def check_terminate(self):
        return self.minerEnv.check_terminate()

    def send_map_info(self, request):
        return self.minerEnv.send_map_info(request)

    def get_state(self):
        view = np.zeros([self.state.mapInfo.max_x + 1, self.state.mapInfo.max_y + 1], dtype=int)
        for i in range(self.state.mapInfo.max_x + 1):
            for j in range(self.state.mapInfo.max_y + 1):
                if self.state.mapInfo.get_obstacle(i, j) == TreeID:  # Tree
                    view[i, j] = -TreeID
                if self.state.mapInfo.get_obstacle(i, j) == TrapID:  # Trap
                    view[i, j] = -TrapID
                if self.state.mapInfo.get_obstacle(i, j) == SwampID:  # Swamp
                    view[i, j] = -SwampID
                if self.state.mapInfo.gold_amount(i, j) > 0:
                    view[i, j] = self.state.mapInfo.gold_amount(i, j)

        self.view = view
        return self.minerEnv.get_state()



    def reset(self):
        # try:
        print()
        print('------RESET--------')
        # print(self.minerEnv.socket.bots)
        if len(self.minerEnv.socket.bots) > 0:
            print('bot1_score: ', self.minerEnv.socket.bots[0].info.score)
            print('bot2_score: ', self.minerEnv.socket.bots[1].info.score)
            print('bot3_score: ', self.minerEnv.socket.bots[2].info.score)
            print('user_score: ', self.minerEnv.socket.user.score)

        # else:
        #     print('no player')
        # except:
            # pass

        # mapID = np.random.randint(1, 6)
        mapID = 1
        posID_x = np.random.randint(MAP_MAX_X)
        posID_y = np.random.randint(MAP_MAX_Y)
        request = ("map" + str(mapID) + "," + str(posID_x) + "," + str(posID_y) + ",50,100")
        self.minerEnv.send_map_info(request)
        state = self.get_state()
        self.minerEnv.reset()
        return state

    def render(self, mode='human'):
        if self.view is None:
            return
        h, w = self.view.shape
        mat = np.zeros(shape=(h, w, 3), dtype=np.uint8)


        mat[self.view == -1, 1] = 153
        mat[self.view == -3, 1] = 53
        mat[self.view == -2, 0] = 153

        mat[self.view > 0, 1:3] = np.array([self.view[self.view>0],self.view[self.view>0]]).T
        remaining_gold = sum(self.view[self.view>0].flatten())
        t = PrettyTable(['ID', 'Score','Engergy','Free count','status','last action'])
        for player in self.minerEnv.state.players:
            id = player['playerId']
            score = player['score']
            engergy = player['energy']
            free_count = player['freeCount']
            last_action = ACTIONS[player['lastAction']]
            # last_action = ACTIONS[self.action]
            status = player['status']

            x = player['posx']
            y = player['posy']

            if x >= h or y>=w:
                continue

            if player['playerId'] == self.minerEnv.state.id:
                mat[x, y, :] = 255
                t.add_row(['player', score,engergy,free_count,status,last_action])
            else:
                mat[x, y, 2] = 153
                t.add_row(['bot {}'.format(id), score,engergy,free_count,status,last_action])


        blank =  np.zeros(shape=(h*38,w*38+100,3),dtype=np.uint8)
        z = 'Remaining gold: {}\n'.format(remaining_gold)
        z += t.get_string()
        z += '\nReward : {}'.format(self.reward)
        blank = self.draw_text(mat=blank,text=z)

        mat = cv2.resize(mat, (w*38, h*38), interpolation=cv2.INTER_AREA)
        mat= np.concatenate((mat,blank),1)
        cv2.imshow('game view', mat)
        cv2.waitKey(100)

    def get_reward(self):
        return self.minerEnv.get_reward()

    def close(self):
        self.minerEnv.end()

    def start(self):

        return self.minerEnv.start()