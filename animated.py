import pygame
import os
import sys
from random import randint, choice


pygame.font.init()

from settings import main_win_width, main_win_height, background_color, window, protos_settings, enemy_blaster_equipped_fighter_settings

star = pygame.image.load('images/star.png')
star = pygame.transform.scale(star, (int(star.get_width()/12), int(star.get_height()/12)))

star_height = star.get_height()
star_width = star.get_width()

stars = [[randint(0, main_win_width-1), randint(0, main_win_height-1), randint(1, 3)] for i in range(50)]

big_explosion_frames = [pygame.image.load(os.path.join('explosion', 'frame_' + str(i) +'.png')) for i in range(12)]
explosion_frames = [pygame.transform.scale(image, (image.get_width()//3, image.get_width()//3)) for image in big_explosion_frames]

scaling_factor = 2

from soundhandler import MIXER


from directives import enemy_lazership_directive_0, enemy_blasterfighter_directive_3, enemy_blasterfighter_directive_2, enemy_blasterfighter_directive_1, enemy_blasterfighter_directive_0, serp_directive_0

explosion_channel = MIXER.get_channel()

background = pygame.image.load('images/b2.png')

def docollide(recta, imagea, rectb, imageb):
    i_x_s, i_x_e = max(recta.left, rectb.left), min(recta.right, rectb.right)
    i_y_s, i_y_e = max(rectb.top, recta.top), min(recta.bottom, rectb.bottom)

    arra = pygame.PixelArray(imagea)
    arrb = pygame.PixelArray(imageb)
    for i in range(i_x_s, i_x_e):
        for j in range(i_y_s, i_y_e):
            #if arra[i-recta.left][j-recta.top] != 0 and arrb[i-rectb.left][j-rectb.top] != 0:
            if arra[i-recta.left][j-recta.top] != 0 and arrb[i-rectb.left][j-rectb.top] != 0:
                arra.close()
                arrb.close()
                return True
    arra.close()
    arrb.close()
    return False


def draw_stars(stars, window):
    k = 0
    for i, j, n in stars:
        window.blit(pygame.transform.scale(star, (int(star_width/n), int(star_height/n))), (i, j - int(star_height/n)))
        stars[k][1] = (stars[k][1]+1)%main_win_height
        k += 1


def make_lifebar_rect(width, x, y, life_capacity):
    lifebar_rect = pygame.Rect((x, y-4, width, 2))
    return lifebar_rect


class Solid(pygame.sprite.Sprite):
    def __init__(self, image, rect):
        self.image = image
        self.rect = rect
        pygame.sprite.Sprite.__init__(self)
        self.body = pygame.sprite.GroupSingle(self)

    def analyze_basic(self, target):
        if pygame.sprite.spritecollide(target, self.body, 0):
            if docollide(target.rect, target.image, self.rect, self.image):
                if not target.shields:
                    if target.life > self.life:
                        self.life = 0
                        target.life -= self.life
                    else:
                        target.life = 0
                        self.life -= target.life
                else:
                    self.life = 0


class Hitter():
    def analyze(self, target):
        self.analyze_basic(target)
        dead_bullets = self.analyze_damage(target)
        for bullet in dead_bullets:
            bullet.kill()
        if self.life <= 0:
            self.destruct()

    def draw(self, win=window):
        self.draw_basic(win)


class Spacecraft (Solid):
    def __init__(self, rect, image, speed, lifebar_rect, life_capacity, life_color = (0, 255, 0)):
        self.life_capacity = life_capacity
        self.life = life_capacity
        self.lifebar_rect = lifebar_rect
        self.lifecolor = life_color

        self.speed = speed
        self.score = 0

        global MIXER
        self.soundchannel = MIXER.get_channel()
        Solid.__init__(self, image, rect)

    def move(self, x, y):
        self.rect.y, self.rect.x = self.rect.y+y, self.rect.x+x
        self.lifebar_rect.y, self.lifebar_rect.x = self.lifebar_rect.y+y, self.lifebar_rect.x+x

    def draw_basic(self, surface=window):
        surface.blit(self.image, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.lifebar_rect)
        life_fraction = int(self.life/self.life_capacity*self.rect.width)
        lifelevel = pygame.Rect(self.lifebar_rect.left, self.lifebar_rect.top, life_fraction, self.lifebar_rect.height)
        pygame.draw.rect(surface, self.lifecolor, lifelevel)

    def destruct(self):
        global MIXER
        global explosion_channel
        MIXER.play(explosion_channel, 'explosion')
        exploading_ships.append([self.rect.left, self.rect.top, 0])
        MIXER.stop(self.soundchannel)
        MIXER.free_channel(self.soundchannel)
        self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color):
        self.speed = speed

        self.rect = pygame.Rect(x, y, 4, 15)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(color)

        pygame.sprite.Sprite.__init__(self)

    def update(self):
        self.rect.top = self.rect.top + self.speed
        if not 0 < self.rect.top < main_win_height:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Lazer(pygame.sprite.Sprite):
    def __init__(self, x, y, width, color, soundchannel, recharge_time=20):
        self.rect = pygame.Rect(x, y, width, 1)
        self.image = pygame.Surface((width, width))
        pygame.sprite.Sprite.__init__(self)

        self.on_image = pygame.Surface((width, main_win_height))
        self.on_image.fill(color)

        self.off_image = pygame.Surface((width, 0))

        self.state = False
        self.recharge_time = recharge_time
        self.recharge = self.recharge_time
        self.width = width

        self.soundchannel = soundchannel

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y

    def off(self):
        self.state = False
        self.rect.size = [self.width, 1]
        self.image = self.off_image
        self.recharge = self.recharge_time
        global MIXER
        MIXER.stop(self.soundchannel)

    def on(self):
        self.state = True
        self.rect.size = [self.width, main_win_height]
        self.image = self.on_image
        self.recharge = self.recharge_time
        global MIXER
        MIXER.play(self.soundchannel, 'lazer')

    def update(self):
        self.recharge -= 1
        if self.state:
            if self.recharge == 0:
                self.off()
        else:
            if self.recharge == 0:
                self.on()


class BlasterEquippedFighter():
    def __init__(self, damage, right_gun_pos, left_gun_pos, bullet_speed, bullet_color):
        self.damage = damage
        self.bullets = pygame.sprite.Group()

        self.bullet_speed = bullet_speed
        self.bullet_color = bullet_color

        self.right_gun_position = right_gun_pos
        self.left_gun_position = left_gun_pos

    def shoot(self):
        if len(self.bullets.sprites()) % 2 == 0:
            x, y = self.left_gun_position[0], self.left_gun_position[1]
            self.bullets.add(Bullet(x+self.rect.left, y+self.rect.top, self.bullet_speed, self.bullet_color))
        else:
            x, y = self.right_gun_position[0], self.right_gun_position[1]
            self.bullets.add(Bullet(x+self.rect.left, y+self.rect.top, self.bullet_speed, self.bullet_color))


class MainUnit(BlasterEquippedFighter, Spacecraft):
    def __init__(self):
        speed = 20
        x, y = 300, 500
        life_capacity = 30
        bullet_speed = -20
        bullet_color = (0, 255, 140)
        damage = 1

        #frames = [pygame.image.load('images/animated/'+i) for i in os.listdir('images/animated/')]
        frames = [pygame.image.load('images/o/'+i) for i in os.listdir('images/o/')]
        global scaling_factor
        frames = [pygame.transform.scale(i, (int(i.get_width()/scaling_factor), int(i.get_height()/scaling_factor))) for i in frames]

        image = frames[-2]
        width, height = image.get_width(), image.get_height()
        rect = pygame.Rect(x, y, width, height)

        lifebar_rect = pygame.Rect((x, y+height+5, width, 3))

        left_gun_pos = [5, 0]
        right_gun_pos = [width-5, 0]

        self.shields = False
        self.shield_image = frames[-1]
        self.state = 0

        Spacecraft.__init__(self, rect, image, speed, lifebar_rect, life_capacity, life_color=(0, 255, 140))
        BlasterEquippedFighter.__init__(self, damage, right_gun_pos, left_gun_pos, bullet_speed, bullet_color)

    def update(self):
        x = 0
        y = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += 1
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
        if keys[pygame.K_SPACE]:
            character.shoot()
            global MIXER
            MIXER.play(self.soundchannel, 'my_shot')

        self.move(x*self.speed, y*self.speed)
        self.bullets.update()

    def draw(self, surface=window):
        self.draw_basic(surface)
        self.bullets.draw(surface)
        if self.shields:
            window.blit(self.shield_image, self.rect)


class Enemy():
    def __init__(self, directive, settings):
        self.status = 'i am evil'
        self.directive = directive
        self.state = 0
        self.damage = settings['damage']
        self.settings = settings

    def analyze_damage(self, target):
        self.analyze_basic(target)
        dead_bullets = []

        # Analyzing damage from enemy bullets
        collisions = pygame.sprite.spritecollide(self, target.bullets, 0)
        if collisions:
            n = 0
            for bullet in target.bullets:
                if docollide(self.rect, self.image, bullet.rect, bullet.image):
                    n += 1
                    dead_bullets.append(bullet)
            self.life = max(self.life - n*target.damage, 0)

        if self.life <= 0:
            self.destruct()
        return dead_bullets

    def update_basic(self, target):
        self.directive(self, target)
        self.analyze(target)


class Shooter():
    def analyze(self, target):
        # Damage Analysis begins
        dead_bullets = self.analyze_damage(target)
        # Checking own vitals
        if self.life == 0:
            target.score += 1
            self.destruct()
        # Damage Analysis complete
        # Analyzing damage suffered by target...
        if not target.shields:
            collisions = pygame.sprite.spritecollide(target, self.bullets, 0)
            if collisions:
                n = 0
                for bullet in self.bullets:
                    if docollide(target.rect, target.image, bullet.rect, bullet.image):
                        dead_bullets.append(bullet)
                        n += 1
                target.life = max(target.life - n*self.damage, 0)
                self.score += n
                if target.life < 0:
                    target.life = 0

                    global MIXER
                    MIXER.play(self.soundchannel, 'kill')
        for bullet in dead_bullets:
            bullet.kill()

    def draw(self, surface=window):
        self.bullets.draw(surface)
        self.draw_basic(surface)


class EnemyBlasterEquippedFighter(BlasterEquippedFighter, Enemy, Spacecraft, Shooter):
    def __init__(self, x, y, settings=enemy_blaster_equipped_fighter_settings, directive=enemy_blasterfighter_directive_0):
        image=settings['image']
        speed=settings['speed']
        life_capacity=settings['life_capacity']
        bullet_speed=settings['bullet_speed']
        bullet_color=settings['bullet_color']
        recharge_time=settings['recharge_time']

        if directive == enemy_blasterfighter_directive_0:
            x, y = 0, 0
        elif directive == enemy_blasterfighter_directive_1:
            x, y = main_win_width, 0

        frames = [pygame.image.load('images/enemy/'+i) for i in os.listdir('images/enemy/')]
        global scaling_factor
        frames = [pygame.transform.scale(i, (int(i.get_width()/scaling_factor), int(i.get_height()/scaling_factor))) for i in frames]
        image = frames[0]

        width, height = image.get_width(), image.get_height()
        rect = pygame.Rect(x, y, width, height)

        lifebar_rect = make_lifebar_rect(width, x, y, life_capacity)

        left_gun_pos = [5, height+10]
        right_gun_pos = [width-5, height+10]

        self.recharge_time = recharge_time
        self.guns_recharge = 0

        Spacecraft.__init__(self, rect, image, speed, lifebar_rect, life_capacity, (255, 0, 0))
        BlasterEquippedFighter.__init__(self, settings['damage'], right_gun_pos, left_gun_pos, bullet_speed, bullet_color)
        Enemy.__init__(self, directive, settings)
        Shooter.__init__(self)

    def update(self, target):
        self.update_basic(target)


class Station(Spacecraft, Enemy, Hitter):
    def __init__(self, x=0, y=0):
        frames = [pygame.image.load('images/station/'+i) for i in os.listdir('images/station/')]
        global scaling_factor
        frames = [pygame.transform.scale(i, (int(i.get_width()/scaling_factor), int(i.get_height()/scaling_factor))) for i in frames]
        image = frames[0]
        self.frames = frames
        width, height = image.get_width(), image.get_height()
        rect = pygame.Rect(x, y, width, height)
        life_capacity = 35
        speed = 0
        lifebar_rect = make_lifebar_rect(width, x, y, life_capacity)
        self.state = 0
        self.bullets = pygame.sprite.Group()
        Spacecraft.__init__(self, rect, image, speed, lifebar_rect, life_capacity, (255, 0, 0))
        Enemy.__init__(self, lambda x, y: None, {'damage': 0})
        Hitter.__init__(self)

    def update(self, target):
        self.analyze(target)
        self.update_basic(target)  # Enemy class
        self.state = (self.state+1)%(len(self.frames))
        self.image = self.frames[self.state]


class Serp(Spacecraft, Enemy, Hitter):
    def __init__(self, x=0, y=0, dx=10, dy=10):
        frames = [pygame.image.load('images/serp/'+i) for i in os.listdir('images/serp/')]
        global scaling_factor
        frames = [pygame.transform.scale(i, (int(i.get_width()/scaling_factor), int(i.get_height()/scaling_factor))) for i in frames]
        image = frames[0]
        self.frames = frames
        width, height = image.get_width(), image.get_height()
        rect = pygame.Rect(x, y, width, height)
        life_capacity = 20
        speed = 0
        lifebar_rect = make_lifebar_rect(width, x, y, life_capacity)
        self.state = 0
        self.bullets = pygame.sprite.Group()
        Spacecraft.__init__(self, rect, image, speed, lifebar_rect, life_capacity, (255, 0, 0))
        Enemy.__init__(self, serp_directive_0, {'damage': 0})
        self.dx = dx
        self.dy = dy
        global MIXER
        MIXER.play(self.soundchannel, 'serp', way=-1)
        Hitter.__init__(self)

    def update(self, target):
        self.move(self.dx, self.dy)
        self.analyze(target)
        self.update_basic(target)  # Enemy class
        self.state = (self.state+1)%(len(self.frames))
        self.image = self.frames[self.state]


class Protos(Enemy, Spacecraft, Shooter):
    def __init__(self, speed=2, settings=protos_settings, directive=enemy_lazership_directive_0):
        print('\niniting protos\n\n')
        x, y = 1, 15

        image=settings['image']
        speed=settings['speed']
        life_capacity=20
        recharge_time=settings['recharge_time']
        lazer_width=6

        frames = [pygame.image.load('images/lazership/'+i) for i in os.listdir('images/lazership/')]
        global scaling_factor
        frames = [pygame.transform.scale(i, (int(i.get_width()/scaling_factor), int(i.get_height()/scaling_factor))) for i in frames]
        image = frames[0]
        self.frames = frames
        width, height = image.get_width(), image.get_height()

        width, height = image.get_width(), image.get_height()
        rect = pygame.Rect(x, y, width, height)

        lifebar_rect = make_lifebar_rect(width, x, y, life_capacity)

        Spacecraft.__init__(self, rect, image, speed, lifebar_rect, life_capacity, life_color = (255, 0, 0))

        self.lazer = Lazer(x + image.get_width()//2 - lazer_width//2, y + image.get_height()//2, lazer_width, (255, 255, 255), self.soundchannel, recharge_time) 
        self.bullets = pygame.sprite.GroupSingle(self.lazer)
        self.damage = 1
        self.frame = 0

        Spacecraft.__init__(self, rect, image, speed, lifebar_rect, life_capacity, life_color = (255, 0, 0))
        Shooter.__init__(self)
        Enemy.__init__(self, directive, settings)
 
    def destruct(self):
        global MIXER
        global explosion_channel
        MIXER.stop(self.soundchannel)
        MIXER.stop(self.lazer.soundchannel)
        MIXER.free_channel(self.soundchannel)
        MIXER.play(explosion_channel, 'explosion')
        exploading_ships.append([self.rect.left, self.rect.top, 0])
        self.lazer.kill()
        self.kill()

    def update(self, target):
        #print(self.rect.top, self.rect.left)
        #print('updating a lazership', self.rect.top, self.rect.left)
        self.update_basic(target)
        self.bullets.add(self.lazer)
        self.frame = (self.frame+1)%len(self.frames)
        self.image = self.frames[self.frame]


class Subportal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        frames = [pygame.image.load('images/portal/'+i) for i in os.listdir('images/portal/')]
        global scaling_factor
        frames = [pygame.transform.scale(i, (int(i.get_width()/scaling_factor), int(i.get_height()/scaling_factor))) for i in frames]
        image = frames[0]
        self.frames = frames
        width, height = image.get_width(), image.get_height()

        width, height = image.get_width(), image.get_height()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        self.state = 0
        pygame.sprite.Sprite.__init__(self)
        self.body = pygame.sprite.GroupSingle(self)
        Hitter.__init__(self)

    def draw(self, win=window):
        window.blit(self.image, self.rect)
        self.state = (self.state+1)%len(self.frames)
        self.image = self.frames[self.state]


class Portal():
    def __init__(self, x1, y1, x2, y2):
        self.portal1 = Subportal(x1, y1)
        self.portal2 = Subportal(x2, y2)

    def update(self, target):
        #print('collision analysis')
        if pygame.sprite.spritecollide(target, self.portal1.body, 0):
            #print('collides 1')
            if docollide(self.portal1.rect, self.portal1.image, target.rect, target.image):
                #print('definitely collides 1')
                target.move(self.portal2.rect.left-target.rect.left, self.portal2.rect.top-target.rect.bottom-10)
        elif pygame.sprite.spritecollide(target, self.portal2.body, 0):
            #print('collides 2')
            if docollide(self.portal2.rect, self.portal2.image, target.rect, target.image):
                #print('definitely collides 2')
                target.move(self.portal1.rect.left-target.rect.left, self.portal1.rect.top-target.rect.bottom-10)

    def draw(self, win=window):
        self.portal1.draw(win)
        self.portal2.draw(win)


def end_game(character, enemies, exploading_ships, stars, window=window, explosion_frames=explosion_frames):
    x_init = character.rect.left + character.image.get_width()//2
    y_init = character.rect.top + character.image.get_height()//2
    character.kill()

    global MIXER
    MIXER.play(MIXER.get_channel(), 'explosion')
    for image in big_explosion_frames:
        window.fill(background_color)
        draw_stars(stars, window)
        for enemy in enemies:
            enemy.update(character)
            enemy.draw(window)
        x = x_init - image.get_width()//2
        y = y_init - image.get_height()//2

        window.blit(image, (x, y))
        expload(exploading_ships)

        window.blit(score_word_surf, (10, 10))
        window.blit(score_text.render(str(character.score), True, (255, 255, 255)), (score_width+10, 10))

        pygame.display.flip()
        pygame.time.delay(100)
    MIXER.play(explosion_channel, 'game_over')
    pygame.mixer.stop()
    window.fill(background_color)

    pygame.time.delay(1500)


def expload(exploading_ships):
    n = 0
    while n != len(exploading_ships):
        if exploading_ships[n][2] == 11:
            del exploading_ships[n]
            pass
        else:
            window.blit(explosion_frames[exploading_ships[n][2]], (exploading_ships[n][0], exploading_ships[n][1]))
            exploading_ships[n][2] += 1
            n += 1


class AidKit(pygame.sprite.Sprite):
    def __init__(self):
        x = randint(0, main_win_width-20)
        self.rect = pygame.Rect(x, 0, 20, 20)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill((220, 40, 40))
        pygame.draw.rect(self.image, (255, 255, 255), (8, 0, 4, 20))
        pygame.draw.rect(self.image, (255, 255, 255), (0, 8, 20, 4))
        pygame.sprite.Sprite.__init__(self)

        global MIXER
        self.soundchannel = MIXER.get_channel()

    def update(self, character):
        self.rect.y += 5
        collision = pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(character), 1)
        if collision != []:
            character.life = character.life_capacity
            global MIXER
            MIXER.play(self.soundchannel, 'healing')
            self.respawn()
        if self.rect.y == main_win_width:
            self.respawn()

    def draw(self, surface=window):
        window.blit(self.image, self.rect)

    def respawn(self):
        self.rect.y = self.rect.y-main_win_height-100
        self.rect.x = randint(1, main_win_width)


class Resistance(pygame.sprite.Sprite):
    def __init__(self):
        x = randint(0, main_win_width-20)
        self.rect = pygame.Rect(x, 0, 20, 20)
        self.image = pygame.Surface(self.rect.size)
        pygame.draw.circle(self.image, (160, 160, 180), (10, 10), 10)

        self.gathered = False
        self.timer = 0

        self.recharge_time = 100
        pygame.sprite.Sprite.__init__(self)

        global MIXER
        self.soundchannel = MIXER.get_channel()

    def update(self, character):
        global MIXER
        self.rect.y += 5
        collision = pygame.sprite.spritecollide(self, pygame.sprite.GroupSingle(character), 1)

        if collision != []:
            character.shields = True
            self.gathered = True

            MIXER.play(self.soundchannel, 'healing')
            self.respawn()

        if self.rect.y == main_win_width:
            self.respawn()

        if self.gathered:
            if self.timer >= self.recharge_time:
                character.shields = False
                self.timer = 0
                self.gathered = False

                MIXER.play(self.soundchannel, 'shields_down')

            self.timer += 1

    def draw(self, surface=window):
        window.blit(self.image, self.rect)

    def respawn(self):
        self.rect.y = self.rect.y-main_win_height-100
        self.rect.x = randint(1, main_win_width)

    def destruct(self):
        global MIXER
        MIXER.free_channel(self.soundchannel)
        self.kill()


exploading_ships = []

score_text = pygame.font.SysFont('arial', 30)
score_word_surf = score_text.render('Score: ', True, (255, 255, 255))
score_width = score_word_surf.get_width()

enemies = pygame.sprite.Group()
character = MainUnit()
character.draw(window)

aid_kits = pygame.sprite.Group()
aid_kits.add(AidKit())
shields = pygame.sprite.Group()
shields.add(Resistance())

c = 0
'''
enemies.add(EnemyBlasterEquippedFighter())
enemies.add(Protos())
enemies.add(Protos())
'''
run = True

t_b = 200
t_p_a = 200
t_p_b = 200
s_t = 800


portal = Portal(100, 550, 400, 550)

'''
enemies.add(Station(0, 100))
enemies.add(Station(100, 100))
enemies.add(Station(200, 100))
enemies.add(Station(300, 100))
enemies.add(Station(400, 100))
'''

X = background.get_width()-main_win_width
#enemies.add(Protos())
#enemies.add(EnemyBlasterEquippedFighter(0, 0, directive=enemy_blasterfighter_directive_2))

while run:
    pygame.time.delay(100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.event.pump()
    character.update()

    window.fill(background_color)
    draw_stars(stars, window)
    #window.blit(background, (0, X))

    portal.draw()
    portal.update(character)


    for aid_kit in aid_kits:
        aid_kit.update(character)
    aid_kits.draw(window)
    for shield in shields:
        shield.update(character)
    shields.draw(window)


    for enemy in enemies:
        enemy.update(character)
        #print(dir(enemy))
        enemy.draw(window)

    
    if c%t_p_a == 0:
        enemies.add(EnemyBlasterEquippedFighter(0, 0, directive=enemy_blasterfighter_directive_2))
        enemies.add(Serp())
        enemies.add(Serp(x=500, y=0, dx=-10, dy=10))
    if c%t_p_b == 0:
        enemies.add(EnemyBlasterEquippedFighter(main_win_width, 0, directive=choice([enemy_blasterfighter_directive_3, enemy_blasterfighter_directive_3])))
    if c%t_b == 0:
        enemies.add(Protos(directive=enemy_lazership_directive_0))
    
    if c%s_t == 0:
        enemies.add(Station(0, 100))
        enemies.add(Station(100, 100))
        enemies.add(Station(200, 100))
        enemies.add(Station(400, 100))
        enemies.add(Station(500, 100))

    if character.life <= 0:
        print('Game Over')
        end_game(character, enemies, exploading_ships, stars)
        run = False

    character.draw(window)
    expload(exploading_ships)

    window.blit(score_word_surf, (10, 10))
    window.blit(score_text.render(str(character.score), True, (255, 255, 255)), (score_width+10, 10))

    pygame.display.update()
    c += 1

    '''
    if c%400 == 0:
        t_b -= 10
        t_p_a -= 10
        t_p_b -= 10
    '''
    #X -= 1

pygame.quit()
sys.exit()
