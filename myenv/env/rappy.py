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
DIVIDE_NUM_X = 20
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
        'video.frames_per_second' : 60
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
        self.pre_y_distance = -1 # ラッピーと隙間との距離を記録しておくための変数

        # 行動空間の定義(0, 1)
        self.action_space = spaces.Discrete(2)

        # 状態空間の最大と最小を定義
        # low = np.array([0, -WINDOW_HEIGHT])
        # high = np.array([WINDOW_WIDTH, WINDOW_HEIGHT])
        
        # ラッピーのy座標、y方向速度、壁の隙間の座標x,yの順番
        # low = np.array([0, -GameScene.PLAYER_SPEED_MAX, 0, 0])
        # high = np.array([DIVIDE_NUM_Y, GameScene.PLAYER_SPEED_MAX, DIVIDE_NUM_X, DIVIDE_NUM_Y])

        # ラッピーの上端と隙間の上端の距離、ラッピーの上端と隙間の下端の距離
        low = np.array([-1.0,-1.0])
        high = np.array([DIVIDE_NUM_Y, DIVIDE_NUM_Y])

        self.observation_space = spaces.Box(low=low, high=high)

        self._seed()
        self.screen = None
        self._reset()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" %(action, type(action))

        # self.clock.tick(60) # テスト用

        # 無条件報酬(生存時間あたりの報酬)
        reward = 0.0 # y座標に比例して増やす報酬を下に追加したため一旦0に変更

        self.game_scene.step(action)

        # self.state = self.game_scene.get_nearest_gap_distance()

        # state計算(ラッピーのy座標、yスピード、隙間のx座標、y座標)v2
        # self.state = np.array([simplify_pos(self.game_scene.get_rappy_pos()[1], SCR_RECT.height, DIVIDE_NUM_Y),
        #              self.game_scene.get_rappy_speed(),
        #              simplify_pos(self.game_scene.get_nearest_gap_pos()[0], SCR_RECT.width, DIVIDE_NUM_X),
        #              simplify_pos(self.game_scene.get_nearest_gap_pos()[1], SCR_RECT.height, DIVIDE_NUM_Y)])
        

        # state計算(隙間の上部とラッピーのy方向距離、隙間の下部とラッピーのy方向距離)。
        gap_pos = self.game_scene.get_nearest_gap_pos()
        gap_top = gap_pos[1] - self.game_scene.GAP / 2
        gap_bottom = gap_top + self.game_scene.GAP
        rappy_top = self.game_scene.rappy.rect.top
        rappy_bottom = self.game_scene.rappy.rect.bottom

        if rappy_top > gap_top:
            top_distance = simplify_pos(rappy_top - gap_top, SCR_RECT.height, DIVIDE_NUM_Y)
        else:
            top_distance = -1.0

        if rappy_bottom < gap_bottom:
            bottom_distance = simplify_pos(gap_bottom - rappy_bottom, SCR_RECT.height, DIVIDE_NUM_Y)
        else:
            bottom_distance = -1.0

        self.state = np.array([top_distance, bottom_distance])        


        # ジャンプした場合にマイナスの報酬(ジャンプしすぎるので)。
        # 連続でジャンプした場合に限定(2020/07/26)
        if action == 1 and self.game_scene.get_rappy_speed() <= -GameScene.PLAYER_SPEED_MAX + 1:
            reward += 0.0

        # 天井に接着しているときマイナスの報酬
        if self.game_scene.is_rappy_on_top():
            reward += 0.0

        # スコアを獲得したときの報酬
        if self.score < self.game_scene.get_score():
            reward += 3000.0
            self.score = self.game_scene.get_score()
        else:
            reward += 0.0

        """
        # ラッピーのy座標と隙間のy座標が近ければ近いほど報酬が多くもらえる
        # reward += np.round((DIVIDE_NUM_Y - (abs(self.state[3] - self.state[0]))) / 10, decimals=2)
        y_distance = abs(self.state[0] - self.state[3])
        if self.pre_y_distance < 0:
            # 最初のフレームのみこちらを通る
            self.pre_y_distance = y_distance
        else:
            if self.pre_y_distance > y_distance:
                reward += 0.0
            self.pre_y_distance = y_distance
        # reward += DIVIDE_NUM_Y - (abs(self.state[3] - self.state[0]))
        """

        if self.state[0] == -1:
            reward += -self.state[1] / 2
        else:
            if self.state[1] == -1:
                reward += -self.state[0] / 2
            else:
                reward += 20.0
        
        done = self.game_scene.is_rappy_dead() or self.game_scene.count > 100000

        if done:
            # 死んだときマイナスの報酬
            # reward += -500.0
            near_line = self.game_scene.GAP / (self.game_scene.SCR_RECT.height / DIVIDE_NUM_Y)
            if self.state[0] < near_line and self.state[1] < near_line:
                reward += 0.0
            else:
                reward += -500.0

            # 死亡地点にて、隙間との距離に応じて追加報酬もあり→加点だと、壁にぶつかることで報酬が増えると勘違いされる可能性がある
            # reward += (DIVIDE_NUM_Y - (abs(self.state[3] - self.state[0]))) ** 2
            # reward += -((self.state[3] - self.state[0]) ** 2)
            self.game_scene.exit()

        return np.array(self.state), reward, done, {}

    def _reset(self):
        # とりあえず画面右端の真ん中に隙間がある状態を初期状態とする
        self.game_scene.init()
        # self.state = np.array([SCR_RECT.width / 2, 0])
        # self.state = np.array([DIVIDE_NUM_Y / 2, 0, DIVIDE_NUM_X / 2, DIVIDE_NUM_Y / 2])
        self.state = np.array([-1.0, -1.0])

        self.steps_beyond_done = None

        return np.array(self.state)

    def _render(self, mode='human', close=False):
        if self.screen is None:
            self.screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
            pygame.display.set_caption("Rappy-AI")

        self.game_scene.render(self.screen)

        return