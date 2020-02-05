import pygame
main_win_height = 600
main_win_width = 600
background_color = (0, 0, 0)

global window
window = pygame.display.set_mode((main_win_width, main_win_height))
window.fill(background_color)
pygame.display.set_caption('Space Fight')

enemy_image = pygame.image.load('images/enemy.png')
enemy_image = pygame.transform.scale(enemy_image, (int(enemy_image.get_width()/5), int(enemy_image.get_height()/5)))

lazership_image = pygame.image.load('images/lazership.png')
lazership_image = pygame.transform.scale(lazership_image, (int(lazership_image.get_width()/5), int(lazership_image.get_height()/5)))


protos_settings = {
    'frames': 'images/protos/',
    'image': lazership_image,
    'speed': 3,
    'life_capacity': 10,
    'lazer_color': (255, 0, 0),
    'damage': 1,
    'recharge_time': 20,
    'width': lazership_image.get_width(),
    'height': lazership_image.get_width(),
    'lazer_width': 8,
    }

enemy_blaster_equipped_fighter_settings = {
    'frames': 'images/enemy/',
    'image': enemy_image,
    'speed': 4,
    'life_capacity': 10,
    'bullet_speed': 10,
    'bullet_color': (255, 0, 0),
    'damage': 1,
    'recharge_time': 6,
    }
