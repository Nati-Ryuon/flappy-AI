import pygame

from ple.games import base
from pygame.constants import K_SPACE

import player
import wall

class RappyBird(base.PyGameWapper):
  def __init__(self, width=800, height=600):
    actions = {
      "jump": K_SPACE
      # 何も無しっていうアクションが必要かもしれない
    }

    base.PyGameWapper.__init__(self, width, height, actions=actions)
    self.init()

  def init(self):
    # ゲームの再スタートに必要な初期化
    self.distance_to_target = float("inf")
    self.score = 0

  def getGameState(self):
    state = {
      "distance_to_target": self.distance_to_target
    }
    return state

  def getScore(self):
    return self.score

  def game_over(self):
    pass # ラッピーの生存情報を返す(死んだ時True)

  def step(self, dt):
    # dtは1フレームにかかる時間
    # メインループ
    pass
