import pygame
from pygame.locals import *
import random

import collision
from wall import Wall
from player import Player

WALL_INTERVAL = 240
GAP = 200

class GameScene():
  def __init__(self, img_dict:dict, font, SCR_RECT):
    self.SCR_RECT = SCR_RECT
    self.img_dict = img_dict
    self.exit_flag = False # pygame.quit()後に再度ループに入らないようフラグを用意
    self.rappy = Player(self.img_dict["bird"], SCR_RECT.width / 2, SCR_RECT.height / 2, 0)

    self.font = font
    self.init()

  def init(self):
    self.walls = []
    self.count = 0 # ループの
    self.score = 0
    self.rappy.restart()
    collision.clear_wall_obj()

  def step(self):
    self.count += 1
    event = pygame.event.get() # 一度pygame.event.get()を行うと中身が消えてしまうため、eventに格納してplayerへ渡している

    self._update_all(event=event)
    
    for e in event:
      if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
        self.exit()

    #if self.exit_flag == True:
    #    pygame.quit()

  def render(self, screen:pygame.Surface):
    self._draw_all(screen)

  def _update_all(self, event):
    if self.rappy.is_dead() == False:
      self.rappy.update(event)

      self._wall_manager()
      self._update_walls()

      collision.detection_collide(self.rappy)
    else:
      for e in event:
        if e.type == KEYDOWN and e.key == K_SPACE:
          self.init()


  def _draw_all(self, screen:pygame.Surface):
    if self.exit_flag:
      return

    screen.fill((250, 130, 80)) # 画面を黒色(#000)に塗りつぶし ⇒　夕焼けに変更

    self.rappy.draw(screen)
    for wall in self.walls:
      wall.draw(screen) # 描画は画面の情報を渡してやる必要がある

    screen.blit(self.font.render(str(int(self.score/2)), True, (0, 0, 0)), [0, 0]) # この雑なスコア計算どうにかしたい

    pygame.display.update()

  def _update_walls(self):
    for wall in self.walls:
      wall.update()
      if not wall.has_passed() and wall.rect.right <= self.rappy.rect.left:
        wall.pass_through()
        self.score += 1


  def _wall_manager(self):
    image = self.img_dict["wall"]
    if self.count % WALL_INTERVAL == 0:
      rand_y = random.uniform(0, image.get_rect().height * 2 + GAP - self.SCR_RECT.height) # 高さをランダムに
      self.walls.append(Wall(image, self.SCR_RECT.width, 0 - rand_y))
      self.walls.append(Wall(image, self.SCR_RECT.width, image.get_rect().height + GAP - rand_y))
    for i, wall in enumerate(self.walls):
      x = wall.rect.left
      w = wall.rect.width
      if x < - w:
        collision.remove_wall_obj(self.walls[i]) # 画面外へ消えた壁をwall_groupから除外
        self.walls.pop(i)

  def get_exit_flag(self):
    return self.exit_flag

  def is_rappy_dead(self):
    return self.rappy.is_dead()

  def get_score(self):
    return self.score


  # 最も近い隙間の中央座標に対するプレイヤーから見た相対座標を返す(実質state専用メソッド)
  def get_nearest_gap_distance(self):
    posx = self.SCR_RECT.width
    i = 0
    index = -1

    if len(self.walls) == 0:
      return (self.SCR_RECT.width / 2, 0)

    for w in self.walls:
      if w.rect.centerx > self.rappy.rect.centerx:
        if posx > w.rect.centerx:
          posx = w.rect.centerx
          index = i
      i = i + 1


    if self.walls[index].rect.top < self.SCR_RECT.top:
        gap_pos = (self.walls[index].rect.centerx, self.walls[index].rect.top - GAP / 2)
    else:
        gap_pos = (self.walls[index].rect.centerx, self.walls[index].rect.bottom + GAP / 2)

    return (gap_pos[0] - self.rappy.get_pos()[0], gap_pos[1], self.rappy.get_pos()[1])
    
  def exit(self):
    self.exit_flag = True