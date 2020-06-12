# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import os

import collision
from wall import Wall
from player import Player

SCR_RECT = Rect(0,0,800,600) #ウィンドウサイズ取得用なんかに使えるRECT

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
  # screen = pygame.display.set_mode((400, 300))
  screen = pygame.display.set_mode((SCR_RECT.width, SCR_RECT.height))
  pygame.display.set_caption("Rappy-AI")

  img_dict = {} # 画像は辞書型で登録

  load_img(img_dict, "./img/test.jpg", "wall") # wallで画像を登録
  load_img(img_dict, os.path.join("img","rappy.png"), "bird") # birdで画像を登録

  wall = Wall(img_dict["wall"], 200, 0, 1)
  rappy = Player(img_dict["bird"], SCR_RECT.width / 2, SCR_RECT.height / 2, 0)

  clock = pygame.time.Clock()

  exit_flag = False # pygame.quit()後に再度ループに入らないようフラグを用意

  # while True:
  while not exit_flag:

    clock.tick(60) # 60fps
    screen.fill((250, 130, 80)) # 画面を黒色(#000)に塗りつぶし ⇒　夕焼けに変更

    event = pygame.event.get() # 一度pygame.event.get()を行うと中身が消えてしまうため、eventに格納してplayerへ渡している

    wall.update()
    rappy.update(event)
    collision.detection_collide(rappy)
    wall.draw(screen) # 描画は画面の情報を渡してやる必要がある
    rappy.draw(screen)

    pygame.display.update()

    for e in event:
      if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
        pygame.quit()
        exit_flag = True

if __name__ == "__main__":
  main()