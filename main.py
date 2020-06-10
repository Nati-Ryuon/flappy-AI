import pygame
from pygame.locals import *

from wall import Wall

def load_img(img_dict:dict, filepath:str, name:str):
  """ 画像を辞書に登録する用の関数
  """
  if name in img_dict:
    print('the key is already exist')
  else:
    img_dict[name] = pygame.image.load(filepath).convert_alpha()

def main():
  pygame.init()
  screen = pygame.display.set_mode((400, 300))
  pygame.display.set_caption("Rappy-AI")

  img_dict = {} # 画像は辞書型で登録

  load_img(img_dict, "./img/test.jpg", "wall") # wallで画像を登録

  wall = Wall(img_dict["wall"], 200, 0, 1)

  clock = pygame.time.Clock()

  while True:
    clock.tick(60) # 60fps
    screen.fill((0, 0, 0)) # 画面を黒色(#000)に塗りつぶし

    wall.update()
    wall.draw(screen) # 描画は画面の情報を渡してやる必要がある

    pygame.display.update()

    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()

if __name__ == "__main__":
  main()