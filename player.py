import pygame
from pygame.locals import *

SCR_RECT = Rect(0,0,800,600) #ウィンドウサイズ取得用なんかに使えるRECT

class Player(pygame.sprite.Sprite):

    GRAVITY = 0.5
    # SPEED_MAX = 9 JUMP_SPEED側と同値に設定。そこまで影響はないかと
    SPEED_MAX = 10
    JUMP_SPEED = 10

    def __init__(self, image:pygame.Surface, x:float=0, y:float=0, speed:float=0):

        pygame.sprite.Sprite.__init__(self)
        self.__image = image
        self.__image_dead = self.__image.copy() #imageをコピーし、死んでいるラッピーを作成する
        self.__image_dead.fill((80, 160, 160, 0), special_flags = pygame.BLEND_RGBA_SUB) #この部で唐揚げに加工
        self.__image_fallen = pygame.transform.rotate(self.__image, -120) #落ちているラッピーを作成する
        self.__image_fallen_dead = self.__image_fallen.copy() #imageをコピーし、落ちている死んでいるラッピーを作成する
        self.__image_fallen_dead.fill((80, 160, 160, 0), special_flags = pygame.BLEND_RGBA_SUB) #この部で唐揚げに加工       
        self.rect = self.__image.get_rect()
        self.__width = self.rect.width
        self.__height = self.rect.height
        self.__default_pos = (x, y) # 初期地点を記憶させ、restart時に正確に戻ってこれるようにしている
        self.rect.center = self.__default_pos
        self.__speed = speed
        
        self.__exist = True
        self.__alive = True
        self.__stop = True
        self.__fallen = False
        self.__on_top = False

        self.__sysfont = pygame.font.SysFont(None, 60)
    
    def is_jump(self):
        if self.__speed > 0:
            return True
        else:
            return False

    def do_jump(self):
        if self.__speed > 0:
            self.__speed = 0
        self.__speed = -Player.JUMP_SPEED # ジャンプ実行時、徐々に加速
    
    def is_dead(self):
        if self.__alive == False:
            return True
        else:
            return False

    def kill(self):
        self.__alive = False

    def is_stop(self):
        return self.__stop
    
    def do_stop(self):
        self.__stop = True

    def do_resume(self):
        self.__stop = False

    def is_fallen(self):
        return self.__fallen

    def is_on_top(self):
        return self.__on_top

    def get_pos(self):
        return self.rect.center # (x, y)でrectの中央座標を返す

    def get_size(self):
        return (self.rect.width, self.rect.height)

    def get_speed(self):
        return self.__speed

    def restart(self):
        self.rect.center = self.__default_pos
        self.__speed = 0
        self.__exist = True
        self.__alive = True
        self.__fallen = False
        self.do_resume()

    def update(self, event, action):
        # pressed_key = pygame.key.get_pressed() # 押されているキーを取得

        if self.is_dead() == False and self.is_stop() == False: # 死んでも止まってもいなければ実行
            
            if self.__speed < Player.SPEED_MAX:
                self.__speed += Player.GRAVITY # __speedにGRAVITY定数を加算(徐々に落下速度が上昇)
                self.__fallen = False
            else:
                self.__fallen = True

            if action != None:
                if action == 1:
                    self.do_jump()

            for e in event:
                # if event.type == KEYDOWN and pressed_key[K_SPACE] == True:
                if e.type == KEYDOWN and e.key == K_SPACE:
                    self.do_jump() # SPACEが押されていればジャンプを実行

            self.rect.move_ip(0, self.__speed) # y座標を__speed分移動

            # 足が天井を超えそうなら止める
            if self.rect.centery < SCR_RECT.top:
                self.rect.centery = SCR_RECT.top
                self.__on_top = True
                #self.__speed = 0
                # 本家は天井がなかった
            else:
                self.__on_top = False
            
            # 足が床に触れたら死亡判定
            if self.rect.bottom >= SCR_RECT.bottom:
                self.rect.bottom = SCR_RECT.bottom
                self.__alive = False
        else:
            for e in event:
                if e.type == KEYDOWN and e.key == K_SPACE:
                    #self.restart()
                    self.do_resume()

    def draw(self, screen:pygame.Surface):
        if self.__exist == True:
            if self.is_dead() == True:
                if self.is_fallen() == False:
                    screen.blit(self.__image_dead, self.rect)
                else:
                    screen.blit(self.__image_fallen_dead, self.rect)
                # screen.blit(self.__image, self.rect, special_flags=pygame.BLEND_RGBA_ADD

                # ↓ゲームオーバー時メッセージ。メッセージを削除、移行する場合はこの部分をコメントアウトしてください。
                msg = self.__sysfont.render("Press SPACE to restart.", True, (255, 255, 255)) # リスタートメッセージを書いた画像を生成
                screen.blit(msg, ((SCR_RECT.width - msg.get_width())//2, (SCR_RECT.height - msg.get_height())//2)) # 画面中央にリスタートの案内を表示

            else:
                if self.is_fallen() == False:
                    screen.blit(self.__image, self.rect)
                else:
                    screen.blit(self.__image_fallen, self.rect)
