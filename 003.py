import random
import time
import pygame

from pygame import *

class HeroPlane(object):
    def __init__(self,screen):
        #记录当前窗口对象
        self.screen = screen
        self.player = pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\me1.png")
        self.x = 480 / 2 - 100 / 2
        self.y = 500
        self.speed = 10
        #子弹列表
        self.bullets=[]
    # 监听键盘事件
    def key_control(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_w] or key_pressed[pygame.K_UP]:
            self.y -= self.speed
        if key_pressed[K_a] or key_pressed[pygame.K_LEFT]:
            self.x -= self.speed
        if key_pressed[K_s] or key_pressed[pygame.K_DOWN]:
            self.y += self.speed
        if key_pressed[K_d] or key_pressed[pygame.K_RIGHT]:
            self.x += self.speed
        if key_pressed[K_SPACE]:
            #按下空格发射子弹
            bullet=Bullet(self.screen,self.x,self.y)
            #把子弹放到列表里
            self.bullets.append(bullet)
    def display(self):
        # 将飞机图片贴到窗口中
        self.screen.blit(self.player,(self.x, self.y))
        #遍历所有子弹
        for bullet in self.bullets:
            #让子弹飞，修改子弹的y坐标
            bullet.auto_move()
            #子弹显示在窗口
            bullet.display()


class EnemyPlane(object):
    def __init__(self, screen):
        # 记录当前窗口对象
        self.screen = screen
        self.player = pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\enemy1.png")  # 57*43
        self.x = 0
        self.y = 0
        self.speed = 10
        # 子弹列表
        self.bullets = []
        # 敌军的移动方向
        self.direction = 'right'

    def display(self):
        # 将飞机图片贴到窗口中
        self.screen.blit(self.player, (self.x, self.y))
        #遍历所有子弹
        for bullet in self.bullets:
           #让子弹飞，修改子弹的y坐标
           bullet.auto_move()
           #子弹显示在窗口
           bullet.display()

    def auto_move(self):
        if self.direction == 'right':
            self.x += self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        if self.x > 480 - 57:
            self.direction = 'left'
        elif self.x < 0:
            self.direction = 'right'
    def auto_fire(self):
        random_num=random.randint(1,10)
        if random_num ==1:
            bullet=EnemyBullet(self.screen,self.x,self.y)
            self.bullets.append(bullet)

#子弹类
class Bullet(object):
    def __init__(self,screen,x,y):
        #坐标
        self.x=x+100/2-10/2
        self.y=y-11
        #图片
        self.image=pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\bullet2.png")
        #窗口
        self.screen = screen
        self.speed = 10
    def display(self):
        #显示子弹到窗口
        self.screen.blit(self.image,(self.x, self.y))
    def auto_move(self):
        """让子弹飞"""
        self.y -= self.speed

class EnemyBullet(object):
    def __init__(self,screen,x,y):
        #坐标
        self.x=x+57/2-43/2
        self.y=y-11
        #图片
        self.image=pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\bullet1.png")#5*11
        #窗口
        self.screen = screen
        self.speed = 10
    def display(self):
        #显示子弹到窗口
        self.screen.blit(self.image,(self.x, self.y))
    def auto_move(self):
        """让子弹飞"""
        self.y += self.speed

class GameSound(object):
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer_music.load()#音乐的地址
        pygame.mixer_music.set_volume(0.5)#声音大小
    def playBackgroundMusic(self):
        pygame.mixer.music.play(-1)#循环播放音乐
class
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