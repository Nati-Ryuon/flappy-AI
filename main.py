# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import os
import random

from game_scene import GameScene

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



def main():
  pygame.init()
  screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
  pygame.display.set_caption("Rappy-AI")

  font = pygame.font.Font(None, 48)
  clock = pygame.time.Clock()
  img_dict = {} # 画像は辞書型で登録

  load_img(img_dict, os.path.join("img", "wall.png"), "wall") # wallで画像を登録
  load_img(img_dict, os.path.join("img","rappy.png"), "bird") # birdで画像を登録

  game_scene = GameScene(img_dict=img_dict, font=font, SCR_RECT=SCR_RECT) 

  # while True:
  while not game_scene.get_exit_flag():
    clock.tick(60) # 60fps
    game_scene.step(screen=screen)

      

if __name__ == "__main__":
  main()