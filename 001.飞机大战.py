import time
import pygame

from pygame import *


def main():
    """完成整个程序的控制"""
    #创建一个窗口
    screen=pygame.display.set_mode((480,700),0,32)
    #创建一个图片当作背景
    background=pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\background.png")
    #创建一个图片当作玩家飞机
    player=pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\me1.png")

    x=480/2-100/2
    y=500
    speed=10
    while True:
        # 背景图片贴到窗口中
        screen.blit(background, (0, 0))
        # 将飞机图片贴到窗口中
        screen.blit(player, (x, y))
        #获取事件
        for event in pygame.event.get():
            #判断事件类型
            if event.type==QUIT:
                #执行Pygame退出
                pygame.quit()
                #python程序退出
                exit()
        #监听键盘事件
        key_pressed=pygame.key.get_pressed()
        if key_pressed[K_w] or key_pressed[pygame.K_UP]:
            print("上")
            y-=speed
        if key_pressed[K_a] or key_pressed[pygame.K_LEFT]:
            print("左")
            x-=speed
        if key_pressed[K_s] or key_pressed[pygame.K_DOWN]:
            print("下")
            y+=speed
        if key_pressed[K_d] or key_pressed[pygame.K_RIGHT]:
            print("右")
            x+=speed
        if key_pressed[K_SPACE]:
            print("空格")
        #显示窗口中的内容
        pygame.display.update()
        pygame.time.delay(100)


if __name__=='__main__':
    main()