import pygame
from pygame.locals import *

class Player:
    pos = {'x':0,'y':0}
    speed = {'x':0,'y':0}

    def __init__(self):
        self.pos['x'] = 50
        self.pos['y'] = 150
        self.speed['x'] = 0
        self.speed['y'] = 2
    
    def is_jump(self):
        if self.speed['y'] > 0:
            return True
        else:
            return False
    
    def is_dead(self):
        if self.speed['x'] == 0 and self.speed['y'] == 0:
            return True
        else:
            return False

    def update(self):
        key = pygame.key.get_pressed()
        if not self.is_dead():
            self.pos['x'] += self.speed['x']
            self.pos['y'] += self.speed['y']
            
            if key[K_SPACE] == False:
                self.speed['y'] += 2
            else:
                self.speed['y'] -= 5
    
    def draw(self, surface):
        pygame.draw.circle(surface, Color(255,255,50,0), (self.pos['x'], self.pos['y']), 10)
    