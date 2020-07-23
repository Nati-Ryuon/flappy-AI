# coding:utf-8
import logging
import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np
import pygame
from pygame.locals import *
import os

from game_scene import GameScene

logger = logging.getLogger(__name__)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SCR_RECT = Rect(0,0,WINDOW_WIDTH,WINDOW_HEIGHT) #ウィンドウサイズ取得用なんかに使えるRECT


def load_img(img_dict:dict, file_path:str, name:str):
  """ 画像を辞書に登録する用のメソッド
    とりあえず登録名がダブったら表示するだけにしてます
  Args:
    img_dict dict: 画像を登録する辞書
    file_path str: 読み込む画像の相対パス
    name str: 登録する辞書のkey
  """
  if name in img_dict:
    print('the key is already exist')
  else:
    img_dict[name] = pygame.image.load(file_path).convert_alpha()


class RappyEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : 50
    }

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
        pygame.display.set_caption("Rappy-AI")
        
        self.font = pygame.font.Font(None, 48)
        self.clock = pygame.time.Clock()
        self.img_dict = {} # 画像は辞書型で登録

        load_img(self.img_dict, os.path.join("img", "wall.png"), "wall") # wallで画像を登録
        load_img(self.img_dict, os.path.join("img","rappy.png"), "bird") # birdで画像を登録

        self.game_scene = GameScene(img_dict=self.img_dict, font=self.font, SCR_RECT=SCR_RECT) 
        self.score = 0

        # 行動空間の定義(0, 1)
        self.action_space = spaces.Discrete(2)

        # 状態空間の最大と最小を定義
        low = np.array([0, -WINDOW_HEIGHT])
        high = np.array([WINDOW_WIDTH, WINDOW_HEIGHT])

        self.observation_space = spaces.Box(low=low, high=high)

        self._seed()
        self.screen = None
        self._reset()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" %(action, type(action))

        self.game_scene.step(action)

        self.state = self.game_scene.get_nearest_gap_distance()

        if self.score < self.game_scene.get_score():
            reward = 1.0
            self.score = self.game_scene.get_score()
        else:
            reward = 0.0
        
        done = self.game_scene.is_rappy_dead()

        if done:
            self.game_scene.exit()

        return np.array(self.state), reward, done, {}

    def _reset(self):
        # とりあえず画面右端の真ん中に隙間がある状態を初期状態とする
        self.game_scene.init()
        self.state = np.array([SCR_RECT.width / 2, 0])

        self.steps_beyond_done = None

        return np.array(self.state)

    def _render(self):
        if self.screen is None:
            self.screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
            pygame.display.set_caption("Rappy-AI")

        self.game_scene.render(self.screen)

        return