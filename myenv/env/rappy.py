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
import random

import collision
from wall import Wall
from player import Player

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
SCR_RECT = Rect(0,0,WINDOW_WIDTH,WINDOW_HEIGHT) #ウィンドウサイズ取得用なんかに使えるRECT


logger = logging.getLogger(__name__)


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

WALL_INTERVAL = 240
GAP = 200

next_wall_inx:int   #次の壁がどれかわからないため添え字を格納する変数

def wall_manager(count:int, walls:list, image:pygame.Surface):
  if count % WALL_INTERVAL == 0:
    rand_y = random.uniform(0, image.get_rect().height * 2 + GAP - WINDOW_HEIGHT) # 高さをランダムに
    walls.append(Wall(image, WINDOW_WIDTH, 0 - rand_y))
    walls.append(Wall(image, WINDOW_WIDTH, image.get_rect().height + GAP - rand_y))
  for i, wall in enumerate(walls):
    x = wall.rect.left
    w = wall.rect.width
    if x < - w:
      collision.remove_wall_obj(walls[i]) # 画面外へ消えた壁をwall_groupから除外
      walls.pop(i)

def restart(player:Player, walls:list):
  player.restart()
  walls.clear()
  collision.clear_wall_obj()

def main():
  pygame.init()
  # screen = pygame.display.set_mode((400, 300))
  screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
  pygame.display.set_caption("Rappy-AI")

  img_dict = {} # 画像は辞書型で登録

  load_img(img_dict, os.path.join("img", "wall.png"), "wall") # wallで画像を登録
  load_img(img_dict, os.path.join("img","rappy.png"), "bird") # birdで画像を登録

  # wall = Wall(img_dict["wall"], 200, 0, 1)
  rappy = Player(img_dict["bird"], SCR_RECT.width / 2, SCR_RECT.height / 2, 0)

  clock = pygame.time.Clock()

  exit_flag = False # pygame.quit()後に再度ループに入らないようフラグを用意

  walls = []
  count = 0 # ループの

  font = pygame.font.Font(None, 48)
  score = 0

  # while True:
  while not exit_flag:
    count += 1
    clock.tick(60) # 60fps
    screen.fill((250, 130, 80)) # 画面を黒色(#000)に塗りつぶし ⇒　夕焼けに変更

    event = pygame.event.get() # 一度pygame.event.get()を行うと中身が消えてしまうため、eventに格納してplayerへ渡している


    if rappy.is_dead() == False:
      wall_manager(count, walls, img_dict["wall"])
      rappy.update(event)
      for wall in walls:
        wall.update()
        if not wall.has_passed() and wall.rect.right <= rappy.rect.left:
          wall.pass_through()
          score += 1
      collision.detection_collide(rappy)
    else:
      for e in event:
        if e.type == KEYDOWN and e.key == K_SPACE:
          restart(rappy, walls)
          score = 0
          count = 0

    rappy.draw(screen)
    for wall in walls:
      wall.draw(screen) # 描画は画面の情報を渡してやる必要がある

    screen.blit(font.render(str(int(score/2)), True, (0, 0, 0)), [0, 0])

    pygame.display.update()

    for e in event:
      if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
        pygame.quit()
        exit_flag = True


class RappyBirdEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : 60
    }

    def __init__(self):
        
        #---------------------------
        pygame.init()
        # screen = pygame.display.set_mode((400, 300))
        screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
        pygame.display.set_caption("Rappy-AI")

        img_dict = {} # 画像は辞書型で登録

        load_img(img_dict, os.path.join("img", "wall.png"), "wall") # wallで画像を登録
        load_img(img_dict, os.path.join("img","rappy.png"), "bird") # birdで画像を登録

        # wall = Wall(img_dict["wall"], 200, 0, 1)
        rappy = Player(img_dict["bird"], SCR_RECT.width / 2, SCR_RECT.height / 2, 0)

        clock = pygame.time.Clock()

        exit_flag = False # pygame.quit()後に再度ループに入らないようフラグを用意

        walls = []
        count = 0 # ループの

        font = pygame.font.Font(None, 48)
        score = 0
        #---------------------------


        self.action_space = spaces.Discrete(2)

        high = np.array([
            self.cx_threshold,
            np.finfo(np.float32).max,
            self.bx_threshold,
            self.by_threshold,
            np.finfo(np.float32).max
            ])
        self.observation_space = spaces.Box(-high, high)

        self._seed()
        self.viewer = None
        self._reset()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" %(action, type(action))

        state = self.state

        count += 1
        clock.tick(60) # 60fps
        screen.fill((250, 130, 80)) # 画面を黒色(#000)に塗りつぶし ⇒　夕焼けに変更

        event = pygame.event.get() # 一度pygame.event.get()を行うと中身が消えてしまうため、eventに格納してplayerへ渡している

        if rappy.is_dead() == False:
          wall_manager(count, walls, img_dict["wall"])
          rappy.update(event)
          for wall in walls:
            wall.update()
            if not wall.has_passed() and wall.rect.right <= rappy.rect.left:
              wall.pass_through()
              score += 1
          collision.detection_collide(rappy)
        else:
          for e in event:
            if e.type == KEYDOWN and e.key == K_SPACE:
              restart(rappy, walls)
              score = 0
              count = 0

        rappy.draw(screen)
        for wall in walls:
          wall.draw(screen) # 描画は画面の情報を渡してやる必要がある

        screen.blit(font.render(str(int(score/2)), True, (0, 0, 0)), [0, 0])

        pygame.display.update()

        for e in event:
          if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            pygame.quit()
            exit_flag = True
        done = cx < -self.cx_threshold-self.racketwidth \
               or cx > self.cx_threshold + self.racketwidth \
               or by < 0
        done = bool(done)

        if done:
            reward = 0.0

        return np.array(self.state), reward, done, {}

    def _reset(self):
        self.state = np.array([0,0,0,self.ballPosition,self.ballVelocity])
        self.steps_beyond_done = None
        self.by_dot = 0
        return np.array(self.state)

    def _render(self, mode='human', close=False):
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return

        screen_width = 600
        screen_height = 400
        world_width = self.cx_threshold*2
        scale = screen_width/world_width
        racketwidth = self.racketwidth*scale    # 50.0
        racketheight = self.racketheight*scale  # 30.0

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(screen_width, screen_height)
            l,r,t,b = -racketwidth/2, racketwidth/2, racketheight/2, -racketheight/2
            axleoffset = racketheight/4.0
            racket = rendering.FilledPolygon([(1,b), (1,t), (r,t), (r,b)])
            self.rackettrans = rendering.Transform()
            racket.add_attr(self.rackettrans)
            self.viewer.add_geom(racket)

            ball = rendering.make_circle(0.1*scale)
            self.balltrans = rendering.Transform()
            ball.add_attr(self.balltrans)
            self.viewer.add_geom(ball)

        if self.state is None: return None

        x = self.state
        rackety = self.racketposition*scale  # 100 # TOP OF racket
        racketx = x[0]*scale+screen_width/2.0      # MIDDLE OF racket
        ballx = x[2]*scale+screen_width/2.0        # MIDDLE OF racket
        bally = x[3]*scale#+screen_width/2.0       # MIDDLE OF racket
        self.rackettrans.set_translation(racketx, rackety)
        self.balltrans.set_translation(ballx, bally)

        return self.viewer.render(return_rgb_array = mode=="rgb_array")