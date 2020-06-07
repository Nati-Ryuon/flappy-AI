import pygame
from pygame.locals import *
import sys

def main():
  pygame.init()
  screen = pygame.display.set_mode((400, 300))
  pygame.display.set_caption("Rappy-AI")

  while True:
    screen.fill((0, 0, 0)) # 画面を黒色(#000)に塗りつぶし
    pygame.display.update()

    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()

if __name__ == "__main__":
  main()