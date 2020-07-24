import pygame
from pygame.locals import *
import collision

class Wall(pygame.sprite.Sprite):
  """ 障害物用のクラス"""

  def __init__(self, image:pygame.Surface, x:float=0, y:float=0, speed:float=3.2):
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
    self.__has_passed = False

    collision.add_wall_obj(self)

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

  def has_passed(self):
    return self.__has_passed

  def pass_through(self):
    self.__has_passed = True

  def get_x(self):
    """ 座標取得用メソッド
    """
    return self.rect.x

  def get_y(self):
    """ 座標取得用メソッド
    """
    return self.rect.y
  
  def get_width(self):
    """ 座標取得用メソッド
    """
    return self.rect.width

  def get_height(self):
    """ 座標取得用メソッド
    """
    return self.rect.height