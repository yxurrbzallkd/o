import pygame
pygame.mixer.init()
pygame.mixer.set_num_channels(20)

class Soundpanel():
    def __init__(self):
        shooting_sound = pygame.mixer.Sound("sounds/my_shoot.wav")
        shooting_sound.set_volume(0.2)
        enemy_shooting_sound = pygame.mixer.Sound("sounds/enemy_shoot.wav")
        enemy_shooting_sound.set_volume(0.2)
        killing_sound = pygame.mixer.Sound("sounds/kill.wav")
        killing_sound.set_volume(0.2)
        explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
        game_over_sound = pygame.mixer.Sound("sounds/game_over.ogg")
        game_over_sound.set_volume(2)
        lazer_sound = pygame.mixer.Sound("sounds/lazer_s.wav")
        healing_sound = pygame.mixer.Sound("sounds/heal.wav")
        shield_off = pygame.mixer.Sound("sounds/shields.ogg")
        serp = pygame.mixer.Sound("sounds/knives.wav")

        self.sounds = {'my_shot': shooting_sound,
                       'enemy_blast': enemy_shooting_sound,
                       'kill': killing_sound,
                       'explosion': explosion_sound,
                       'game_over': game_over_sound,
                       'lazer': lazer_sound,
                       'healing': healing_sound,
                       'shields_down': shield_off,
                       'serp': serp}
        self.n_channels = 19
        self.channels = {i: pygame.mixer.Channel(i) for i in range(20)}
        self.free_channels = list(range(20))

    def play(self, channel, sound, way=0):
        #print('playing {} on  channel {}'.format(sound, channel))
        if channel:
            self.channels[channel].play(self.sounds[sound], way)

    def get_channel(self):
        #print('handing out a channel')
        if self.free_channels:
            return self.free_channels.pop()
        return False

    def free_channel(self, n):
        #print('freeing channel')
        self.free_channels.append(n)
        #print(self.free_channels, 'are free\n')

    def stop(self, soundchannel):
        #print('stopping soundchannel')
        self.channels[soundchannel].stop()

MIXER = Soundpanel()
