import random
import time
import pygame

from pygame import *

class HeroPlane(pygame.sprite.Sprite):
    def __init__(self,screen):
        pygame.sprite.Sprite.__init__(self)
        #记录当前窗口对象
        self.screen = screen
        #创建一个玩家飞机图片，当作真正的飞机
        self.player = pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\me1.png")
        #根据图片获取矩形对象
        self.rect = self.image.get_rect()
        self.rect.topleft = [480/2-100/2,500]#x,y
        #飞机速度
        self.speed = 10
        #子弹列表
        self.bullets=pygame.sprite.Group()

    # 监听键盘事件
    def key_control(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_w] or key_pressed[pygame.K_UP]:
            self.rect.top -= self.speed
        if key_pressed[K_a] or key_pressed[pygame.K_LEFT]:
            self.rect.bottom -= self.speed
        if key_pressed[K_s] or key_pressed[pygame.K_DOWN]:
            self.rect.left += self.speed
        if key_pressed[K_d] or key_pressed[pygame.K_RIGHT]:
            self.rect.right += self.speed
        if key_pressed[K_SPACE]:
            #按下空格发射子弹
            bullet=Bullet(self.screen,self.rect.left,self.rect.top)
            #把子弹放到列表里
            self.bullets.add(bullet)
    def update(self):
        self.key_control()
        self.display()
    def display(self):
        # 将飞机图片贴到窗口中
        self.screen.blit(self.player,self.rect)
        #更新子弹坐标
        self.bullets.update()
        #把所有子弹全部添加到屏幕
        self.bullets.draw(self.screen)


class EnemyPlane(pygame.sprite.Sprite):
    def __init__(self, screen):
        # 记录当前窗口对象
        self.screen = screen
        self.player = pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\enemy1.png")  # 57*43
        self.rect = self.image.get_rect()
        self.rect.topleft = [0,0]  # x,y
        # 飞机速度
        self.speed = 10
        # 子弹列表
        self.bullets = pygame.sprite.Group()
        # 敌军的移动方向
        self.direction = 'right'

    def display(self):
        # 将飞机图片贴到窗口中
        self.screen.blit(self.player, self.rect)
        # 更新子弹坐标
        self.bullets.update()
        # 把所有子弹全部添加到屏幕
        self.bullets.draw(self.screen)
    def update(self):
        self.auto_move()
        self.auto_fire()
        self.display()
    def auto_move(self):
        if self.direction == 'right':
            self.rect.right += self.speed
        elif self.direction == 'left':
            self.rect.right -= self.speed
        if self.rect.right > 480 - 57:
            self.direction = 'left'
        elif self.rect.right < 0:
            self.direction = 'right'
    def auto_fire(self):
        random_num=random.randint(1,10)
        if random_num ==1:
            bullet=EnemyBullet(self.screen,self.rect.left,self.rect.top)
            self.bullets.add(bullet)

#子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self,screen,x,y):
        #精灵类初始化
        pygame.sprite.Sprite.__init__(self)
        #创建图片
        self.image=pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\bullet2.png")
        #获取矩形对象
        self.rect = self.image.get_rect()
        self.rect.topleft=[x+100/2-10/2,y-11]

        #窗口
        self.screen = screen
        #速度
        self.speed = 10
    def update(self):
        #修改子弹坐标
        self.rect.top -= self.speed
        #如果子弹移出屏幕上方，则销毁子弹对象
        if self.rect.top<-11:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self,screen,x,y):
        #初始化精灵类
        pygame.sprite.Sprite.__init__(self)
        #图片
        self.image=pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\bullet1.png")#5*11
        #获取矩形对象
        self.rect = self.image.get_rect()
        self.rect.topleft = [x+57/2-43/2, y-11]
        #窗口
        self.screen = screen
        self.speed = 10

    def update(self):
        # 修改子弹坐标
        self.rect.top += self.speed
        # 如果子弹移出屏幕上方，则销毁子弹对象
        if self.rect.top > 852:
            self.kill()

class GameSound(object):
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer_music.load()#音乐的地址
        pygame.mixer_music.set_volume(0.5)#声音大小
    def playBackgroundMusic(self):
        pygame.mixer.music.play(-1)#循环播放音乐

def main():
    """完成整个程序的控制"""
    sound=GameSound()
    sound.playBackgroundMusic()
    #创建一个窗口
    screen=pygame.display.set_mode((480,700),0,32)
    #创建一个图片当作背景
    background=pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\background.png")
    #创建一个飞机类对象
    player=HeroPlane(screen)
    #创建一个敌军飞机类对象
    enemy=EnemyPlane(screen)
    while True:
        # 背景图片贴到窗口中
        screen.blit(background, (0, 0))

        #获取事件
        for event in pygame.event.get():
            #判断事件类型
            if event.type==QUIT:
                #执行Pygame退出
                pygame.quit()
                #python程序退出
                exit()
        #执行飞机的按键监听
        player.key_control()
        #飞机的显示
        player.display()
        #敌军飞机的显示
        enemy.display()
        #敌军飞机自动移动
        enemy.auto_move()
        #敌军飞机自动发射子弹
        enemy.auto_fire()
        # 更新需要显示的内容
        pygame.display.update()
        pygame.time.delay(10)


if __name__=='__main__':
    main()