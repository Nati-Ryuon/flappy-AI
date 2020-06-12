import pygame

# 壁を登録するグループ
wall_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

def add_player_obj(player_sprite):
    if player_group.has(player_sprite) == False:
        player_group.add(player_sprite)
    else:
        print("既に登録済みのplayerを追加しようとしています。")

def add_wall_obj(wall_sprite):
    if wall_group.has(wall_sprite) == False:
        wall_group.add(wall_sprite)
    else:
        print("既に登録済みのwallを追加しようとしています。")

def remove_wall_obj(wall_sprite):
    if wall_group.has(wall_sprite) == True:
        wall_group.remove(wall_sprite)
    else:
        print("存在しないwallを削除しようとしています。")

def detection_collide(player):
    # if pygame.sprite.spritecollideany(player, wall_group) == True:
    hit_group = pygame.sprite.spritecollide(player, wall_group, False)
    if hit_group:
        player.kill()