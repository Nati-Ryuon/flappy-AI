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
    pass

  def getGameState(self):
    state = {
      
    }
    return state