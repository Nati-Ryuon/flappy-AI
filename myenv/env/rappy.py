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

# 受け取った座標を簡易化するための数字。各向きを(DIVIDE_NUM_○)段階に分割する。
DIVIDE_NUM_X = 30
DIVIDE_NUM_Y = 30


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

def simplify_pos(pos:float, pos_max:float, div_num:int):
  """ 座標を簡素化するための関数
    posで指定された座標を0～div_numまでのint型整数で返す。
  Args:
    pos：簡素化したい座標(一方向ずつ)
    pos_max：posに指定した座標が取りうる最大値(画面サイズ等)
    div_num：簡素化した際に何段階に分けるかを指定する数値
  """
  simple_pos = int(pos / (pos_max / div_num))
  
  if simple_pos < 0:
    simple_pos = 0
  else:
    if simple_pos > div_num:
      simple_pos = div_num

  return simple_pos

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
        # low = np.array([0, -WINDOW_HEIGHT])
        # high = np.array([WINDOW_WIDTH, WINDOW_HEIGHT])
        
        # ラッピーのy座標、y方向速度、壁の隙間の座標x,yの順番
        low = np.array([0, -GameScene.PLAYER_SPEED_MAX, 0, 0])
        high = np.array([DIVIDE_NUM_Y, GameScene.PLAYER_SPEED_MAX, DIVIDE_NUM_X, DIVIDE_NUM_Y])

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

        # self.state = self.game_scene.get_nearest_gap_distance()
        # state計算(ラッピーのy座標、yスピード、隙間のx座標、y座標)
        self.state = np.array([simplify_pos(self.game_scene.get_rappy_pos()[1], SCR_RECT.height, DIVIDE_NUM_Y),
                      self.game_scene.get_rappy_speed(),
                      simplify_pos(self.game_scene.get_nearest_gap_pos()[0], SCR_RECT.width, DIVIDE_NUM_X),
                      simplify_pos(self.game_scene.get_nearest_gap_pos()[1], SCR_RECT.height, DIVIDE_NUM_Y)])

        reward = self._compute_reward(action)
        
        done = self.game_scene.is_rappy_dead() or self.game_scene.count > 1000

        if done:
            # 死んだときマイナスの報酬
            reward += -500.0

            # 死亡地点にて、隙間との距離に応じて追加報酬もあり→加点だと、壁にぶつかることで報酬が増えると勘違いされる可能性がある
            # reward += (DIVIDE_NUM_Y - (abs(self.state[3] - self.state[0]))) ** 2
            reward += -((self.state[3] - self.state[0]) ** 2)
            self.game_scene.exit()

        return np.array(self.state), reward, done, {}

    def _reset(self):
        # とりあえず画面右端の真ん中に隙間がある状態を初期状態とする
        self.game_scene.init()
        # self.state = np.array([SCR_RECT.width / 2, 0])
        self.state = np.array([DIVIDE_NUM_Y / 2, 0, DIVIDE_NUM_X / 2, DIVIDE_NUM_Y / 2])

        self.steps_beyond_done = None

        return np.array(self.state)

    def _render(self):
        if self.screen is None:
            self.screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
            pygame.display.set_caption("Rappy-AI")

        self.game_scene.render(self.screen)

        return

    def _compute_reward(self, action):
      # 無条件報酬(生存時間あたりの報酬)
      reward = 5.0 # y座標に比例して増やす報酬を下に追加したため一旦0に変更
      # ジャンプした場合にマイナスの報酬(ジャンプしすぎるので)。
      # 連続でジャンプした場合に限定(2020/07/26)
      if action == 1 and self.game_scene.get_rappy_speed() <= -GameScene.PLAYER_SPEED_MAX + 50:
          reward += -50.0
          #reward += -1.0

      # 天井に接着しているときマイナスの報酬
      if self.game_scene.is_rappy_on_top():
          reward -= 1.0

      # スコアを獲得したときの報酬
      if self.score < self.game_scene.get_score():
          reward += 3000.0
          self.score = self.game_scene.get_score()
     

      # ラッピーのy座標と隙間のy座標が近ければ近いほど報酬が多くもらえる
      # reward += np.round((DIVIDE_NUM_Y - (abs(self.state[3] - self.state[0]))) / 10, decimals=2)
      reward += DIVIDE_NUM_Y - (abs(self.state[3] - self.state[0]))
      
      return reward