import pygame
from pygame.locals import *

class Wall(pygame.sprite.Sprite):
  """ 障害物用のクラス"""

  def __init__(self, image:pygame.Surface, x:float=0, y:float=0, speed:float=0):
    """コンストラクタ

    Args:
      screen pygame.Surface: 描画対象の画面
      x float: x座標 optional
      y float: y座標 optional
      speed float: 移動速度 optional
    """
    pygame.sprite.Sprite.__init__(self)
    self.__image = image
    self.__width = image.get_width()
    self.__height = image.get_height()
    self.rect = Rect(x, y, self.__width, self.__height)
    self.__speed = speed

  def update(self):
    """ 更新用メソッド
      ・毎フレーム呼ばれる
      ・移動のみを行う
    Args: void

    Returns: void
    """
    self.rect.move_ip(-self.__speed, 0)

  def draw(self, screen:pygame.Surface):
    screen.blit(self.__image, self.rect)


  def get_pos(self) -> tuple:
    """ 座標取得用メソッド
      ・障害物の座標をタプルで返す

    Args: void

    Returns:
      tuple: (x座標, y座標)
    """
    return (self.__x, self.__y)