import pygame
from soundhandler import MIXER
from settings import main_win_width, main_win_height

def enemy_lazership_directive_0(ship, target):
    if ship.state < 100:
        ship.move(3, 0)
        ship.lazer.move(3, 0)
        ship.lazer.update()
    elif ship.state < 200:
        ship.move(-3, 0)
        ship.lazer.move(-3, 0)
        ship.lazer.update()
    else:
        ship.state = 0
    ship.state += 1


def enemy_blasterfighter_directive_0(ship, target):
    if ship.state < 100:
        ship.move(4, 5)
    elif ship.state < 200:
        ship.move(-4, 5)
    else:
        ship.state = 0
    ship.state += 1

    if ship.guns_recharge == 0:
        ship.shoot()
        ship.guns_recharge = ship.recharge_time

        global MIXER
        MIXER.play(ship.soundchannel, 'enemy_blast')
    else:
        ship.guns_recharge -= 1
        
    for bullet in ship.bullets:
        bullet.update()
    pygame.sprite.groupcollide(target.bullets, ship.bullets, 1, 1)


def enemy_blasterfighter_directive_1(ship, target):
    if ship.state > 100:
        ship.move(4, 5)
    elif ship.state < 200:
        ship.move(-4, 5)
    else:
        ship.state = 0
    ship.state += 1

    if ship.guns_recharge == 0:
        ship.shoot()
        ship.guns_recharge = ship.recharge_time

        global MIXER
        MIXER.play(ship.soundchannel, 'enemy_blast')
    else:
        ship.guns_recharge -= 1
        
    for bullet in ship.bullets:
        bullet.update()
    pygame.sprite.groupcollide(target.bullets, ship.bullets, 1, 1)


def enemy_blasterfighter_directive_2(ship, target):
    if ship.state < 20:
        ship.move(8, 5)
    elif ship.state < 40:
        ship.move(8, -5)
    elif ship.state < 60:
        ship.move(-8, 5)
    elif ship.state < 80:
        ship.move(-8, -5)
    else:
        ship.state = 0
    ship.state += 1

    if ship.guns_recharge == 0:
        ship.shoot()
        ship.guns_recharge = ship.recharge_time

        global MIXER
        MIXER.play(ship.soundchannel, 'enemy_blast')
    else:
        ship.guns_recharge -= 1

    for bullet in ship.bullets:
        bullet.update()
    pygame.sprite.groupcollide(target.bullets, ship.bullets, 1, 1)


def enemy_blasterfighter_directive_3(ship, target):
    if ship.state < 20:
        ship.move(-8, 7)
    elif ship.state < 40:
        ship.move(-8, -7)
    elif ship.state < 60:
        ship.move(8, 7)
    elif ship.state < 80:
        ship.move(8, -7)
    else:
        ship.state = 0
    ship.state += 1

    if ship.guns_recharge == 0:
        ship.shoot()
        ship.guns_recharge = ship.recharge_time

        global MIXER
        MIXER.play(ship.soundchannel, 'enemy_blast')
    else:
        ship.guns_recharge -= 1

    for bullet in ship.bullets:
        bullet.update()
    pygame.sprite.groupcollide(target.bullets, ship.bullets, 1, 1)


def serp_directive_0(serp, target):
    if not 0 < serp.rect.top < main_win_height or not 0 < serp.rect.left < main_win_width:
        serp.dx = -serp.dx
        serp.dy = -serp.dy