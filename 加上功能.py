import random
import time
import pygame
from pygame.locals import *
# screen：游戏窗口对象
# player：玩家飞机图片
# rect：飞机位置和尺寸的矩形对象
# speed：飞机移动速度
# bullets：玩家子弹精灵组
# key_control()：处理键盘事件（WASD 或方向键移动，空格发射子弹）
# update()：更新飞机状态并显示
# display()：绘制飞机和子弹
# clear_bullets()：清空所有子弹（类方法）
class HeroPlane(pygame.sprite.Sprite):
    #存放所有飞机子弹的组
    bullets = pygame.sprite.Group()#实现子弹打敌机爆炸的功能
    def __init__(self,screen):
        pygame.sprite.Sprite.__init__(self)
        #记录当前窗口对象
        self.screen = screen
        #===创建一个玩家飞机图片，当作真正的飞机
        self.player = pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\me1.png")
        #根据图片获取矩形对象
        self.rect = self.player.get_rect()
        self.rect.topleft = [Manager.bg_size[0]/2-100/2,500]#x,y
        #飞机速度
        self.speed = 10
        #子弹列表
        self.bullets=pygame.sprite.Group()
        #新增生命值属性
        self.max_hp=8#最大生命值
        self.current_hp=self.max_hp#初始化
        #新增掩码
        self.mask=pygame.mask.from_surface(self.player)
    #新增受伤方法
    def take_damage(self,damage=1):
        """玩家受伤，减少生命值"""
        self.current_hp-=damage
        #播放受伤音效
        #self.sound.play_hurtsound()
        return self.current_hp<=0#返回是否死亡
    # 监听键盘事件
    def key_control(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_w] or key_pressed[pygame.K_UP]:
            self.rect.top -= self.speed
            if self.rect.top<0:#顶部超过窗口上边缘
                self.rect.top=0
        if key_pressed[K_a] or key_pressed[pygame.K_LEFT]:
            self.rect.left -= self.speed
            if self.rect.left<0:
                self.rect.left=0
        if key_pressed[K_s] or key_pressed[pygame.K_DOWN]:
            self.rect.top += self.speed
            if self.rect.bottom>Manager.bg_size[1]:#窗口高度是Manager.bg_size[1]
                self.rect.bottom=Manager.bg_size[1]
        if key_pressed[K_d] or key_pressed[pygame.K_RIGHT]:
            self.rect.right += self.speed
            if self.rect.right>Manager.bg_size[0]:
                self.rect.right=Manager.bg_size[0]
        if key_pressed[K_SPACE]:
            #按下空格发射子弹
            bullet=Bullet(self.screen,self.rect.left,self.rect.top)
            #把子弹放到列表里
            self.bullets.add(bullet)
            #存放所有飞机的子弹的组
            HeroPlane.bullets.add(bullet)
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
    @classmethod
    def clear_bullets(cls):
        #清空子弹
        cls.bullets.empty()
# 类似玩家飞机的基础属性
# direction：敌机移动方向（左右移动）
# enemy_bullets：敌机子弹精灵组
# 主要方法：
# auto_move()：敌机自动移动逻辑（左右往返 + 向下移动）
# auto_fire()：随机发射子弹
# update()：更新敌机状态
class EnemyPlane(pygame.sprite.Sprite):
    # 存放子弹的精灵组
    enemy_bullets = pygame.sprite.Group()
    def __init__(self, screen):
        #修正，调用父类初始化
        pygame.sprite.Sprite.__init__(self)
        # 记录当前窗口对象
        self.screen = screen
        self.player = pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\enemy1.png")  # 57*43
        self.rect = self.player.get_rect()#获取矩形对象
        x=random.randrange(1,Manager.bg_size[0],50)#让敌机生成位置随机，开始位置，结束位置，步长
        self.rect.topleft = [x,0]  # x,y
        # 飞机速度
        self.speed = random.randint(3,8)
        # 子弹列表
        self.bullets = pygame.sprite.Group()
        # 敌军的移动方向
        self.direction = 'right'
        # 新增掩码
        self.mask = pygame.mask.from_surface(self.player)
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
            self.rect.left += self.speed
        elif self.direction == 'left':
            self.rect.left -= self.speed
        if self.rect.right > Manager.bg_size[0]:
            self.direction = 'left'
        elif self.rect.left < 0:
            self.direction = 'right'
        self.rect.bottom+=self.speed#敌机子弹发射的位置随敌机改变
    def auto_fire(self):
        random_num=random.randint(1,10)
        if random_num ==1:
            #计算子弹x坐标：敌机左侧x+敌机宽度的一半-子弹宽度的一半
            #子弹y坐标：敌机顶部y+敌机高度
            bullet_x=self.rect.left+(self.rect.width/2)-(5//2)
            bullet_y=self.rect.top+self.rect.height
            bullet=EnemyBullet(self.screen,bullet_x,bullet_y)
            self.bullets.add(bullet)
            #把子弹添加到类属性的子弹组里
            EnemyPlane.enemy_bullets.add(bullet)

    @classmethod
    def clear_bullets(cls):
        # 清空子弹
        cls.enemy_bullets.empty()
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
        # 新增掩码
        self.mask = pygame.mask.from_surface(self.image)
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
        self.rect.topleft = [x+57/2-5/2, y+43]
        #窗口
        self.screen = screen
        self.speed = 10
        # 新增掩码
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        # 修改子弹坐标
        self.rect.top += self.speed
        # 如果子弹移出屏幕上方，则销毁子弹对象
        if self.rect.top > Manager.bg_size[1]:
            self.kill()

class GameSound(object):
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer_music.load("D:\\code_python\\plane_game_team_1\\素材库\\cYsmix - Peer Gynt.mp3")#音乐的地址
        pygame.mixer_music.set_volume(0.5)#声音大小
        pygame.mixer_music.play()
        self._bomb=pygame.mixer.Sound("D:\\code_python\\plane_game_team_1\\素材库\\get_bomb.wav")#爆炸音效地址
    def playBackgroundMusic(self):
        pygame.mixer.music.play(-1)#循环播放音乐
    def playBombSound(self):
        pygame.mixer.Sound.play(self._bomb)
class Bomb(object):
    def __init__(self,screen,type):
        self.screen = screen
        if type=="enemy":
            #加载爆炸资源
            self.mImage=[pygame.image.load(f"D:\\code_python\\plane_game_team_1\\素材库\\image\\enemy1_down{v}.png")for v in range(1,5)]
        else:#玩家爆炸的资源要修改
            self.mImage=[pygame.image.load(f"D:\\code_python\\plane_game_team_1\\素材库\\image\\enemy1_down{v}.png")for v in range(1,5)]
        #设置当前爆炸索引
        self.mIndex=0
        #爆炸设置
        #是否可见
        self.mPos=[0,0]
        self.mVisible=False
    def action(self,rect):
        #触发爆炸的方法
        #爆炸的坐标
        self.mPos[0]=rect.left
        self.mPos[1]=rect.top
        #打开爆炸的开关
        self.mVisible=True
    def draw(self):
        if self.mVisible:
            if self.mIndex<len(self.mImage):
                self.screen.blit(self.mImage[self.mIndex],self.mPos)
                self.mIndex+=1
            else:
                self.mVisible=False
                self.mIndex=0
class GameBackground(object):
    #初始化地图
    def __init__(self,screen):
        #窗口
        self.screen = screen
        #地图背景图
        self.Image1=pygame.image.load("D:\\code_python\\plane_game_team_1\\素材库\\绘制游戏结束提示.png")#地图的地址
        self.Image2=pygame.image.load("D:\\code_python\\plane_game_team_1\\素材库\\绘制游戏结束提示.png")
        #辅助移动地图
        self.y1=0
        self.y2=-Manager.bg_size[1]#衔接在第一张图片的上面
    #绘制地图
    def draw(self):
        self.screen.blit(self.Image1,(0,self.y1))
        self.screen.blit(self.Image2,(0,self.y2))
    #移动地图
    def move(self):
        self.y1+=2
        self.y2+=2#向下移动
        if self.y1>=Manager.bg_size[1]:#第一张照片移到窗口底部
            self.y1=0
        if self.y2>=0:#第二张照片移到窗口开始的地方
            self.y2=-Manager.bg_size[1]
# 初始化：创建游戏窗口、背景、精灵组等
# 事件处理：
# 监听窗口关闭事件
# 处理敌机创建定时器（每隔 1 秒生成一架敌机）
# 游戏结束倒计时
# 碰撞检测：
# 玩家子弹与敌机碰撞
# 敌机子弹与玩家碰撞
# 玩家飞机与敌机直接碰撞
# 游戏状态管理：
# 游戏结束判定与处理
# 重新开始游戏逻辑
# 分数显示（目前仅显示文字框架，未实现计分逻辑）
class Manager(object):
    bg_size=(512,786)#地图的像素
    #创建敌机定时器的id
    create_enemy_id = pygame.USEREVENT + 1
    #游戏结束，倒计时的id
    game_over_id=11#可以随便取1-32中的数字
    #游戏是否结束
    is_game_over=False
    #倒计时时间,重开游戏的倒计时
    over_time=3

    def __init__(self):
        pygame.init()
        #创建窗口
        self.screen = pygame.display.set_mode(Manager.bg_size,0,32)#像素，位深
        #创建背景图片
        #self.background = pygame.image.load()
        self.map=GameBackground(self.screen)
        #初始化一个装玩家精灵的group
        self.players=pygame.sprite.Group()
        #初始化一个装敌机精灵的group
        self.enemies=pygame.sprite.Group()
        #初始化一个玩家爆炸的对象
        self.player_bomb=Bomb(self.screen,"player")
        #初始化一个敌机爆炸的对象
        self.enemy_bomb=Bomb(self.screen,"enemy")
        #初始化一个声音播放的对象
        self.sound=GameSound()

    def exit(self):
        print("退出")
        pygame.quit()
        exit()
    def show_over_text(self):
        #游戏结束，倒计时后重新开始
        self.drawText('game over %d'%Manager.over_time,100,Manager.bg_size[0]/2,textHeight=50,fontColor=[255,0,0])
    def game_over_timer(self):
        self.show_over_text()
        #倒计时-1
        Manager.over_time-=1
        if Manager.over_time==0:
            #参数2改为0，定时间停止
            pygame.time.set_timer(Manager.game_over_id,0)
            #倒计时后重新开始
            Manager.over_time=3
            Manager.is_game_over=False
            self.start_game()
    def start_game(self):
        #重新开始游戏，有些类属性要清空
        self.players.empty()
        self.enemies.empty()
        EnemyPlane.clear_bullets()
        HeroPlane.clear_bullets()
        #重新创建玩家
        self.new_player()
        Manager.is_game_over=False
    def new_player(self):
        #创建飞机对象。添加到玩家的组
        player=HeroPlane(self.screen)
        self.players.add(player)
    def new_enemy(self):
        enemy=EnemyPlane(self.screen)
        self.enemies.add(enemy)
    #绘制文字
    def drawText(self,text,x,y,textHeight=30,fontColor=(255,255,0),backgroudColor=None):
        #通过字体文件获取字体对象
        font_obj=pygame.font.SysFont("SimHei",textHeight)
        #配置要显示的文字
        text_obj=font_obj.render(text,True,fontColor,backgroudColor)
        #获取要显示的对象的 rect
        text_rect=text_obj.get_rect()
        #设置显示对象的坐标
        text_rect.topleft=(x,y)
        #绘制字到指定的区域
        self.screen.blit(text_obj,text_rect)
    def main(self):
        #播放背景音乐
        self.sound.playBackgroundMusic()
        #创建一个玩家
        self.new_player()
        #开启创建敌机的定时器
        pygame.time.set_timer(Manager.create_enemy_id,1000)
        #创建时钟对象
        clock=pygame.time.Clock()
        while True:
            #把背景图片贴到窗口
            #self.screen.blit(self.background, (0, 0))
            #移动地图
            self.map.move()
            #把地图贴到窗口上
            self.map.draw()
            #绘制文字
            self.drawText('分数：',50,0)#文字的内容，坐标
            if Manager.is_game_over:
                #判断游戏结束才显示结束文字
                self.show_over_text()
            #遍历所有的事件
            for event in pygame.event.get():
                # 判断事件类型
                if event.type == Manager.create_enemy_id:
                    print("触发敌机创建定时器")
                    self.new_enemy()
                elif event.type == QUIT:
                    self.exit()
                elif event.type == Manager.create_enemy_id:
                    #创建一个敌机
                    self.new_enemy()
                elif event.type==Manager.game_over_id:
                    #电定时器触发的事件
                    self.game_over_timer()
            if self.players:  # 玩家存在时才显示
                player = self.players.sprites()[0]
                # 显示格式：HP: 3/3
                self.drawText(
                    f'生命值: {player.current_hp}/{player.max_hp}',
                    x=50, y=30,  # 位置（可调整）
                    textHeight=30,
                    fontColor=[0, 255, 0]  # 绿色文字
                )
            #调用爆炸的对象
            self.player_bomb.draw()
            self.enemy_bomb.draw()
            #敌机子弹和玩家飞机的碰撞判断
            # if self.players:
            #     player = self.players.sprites()[0]
            #     isover = pygame.sprite.spritecollide(
            #         player,
            #         EnemyPlane.enemy_bullets,
            #         True,  # 碰撞后子弹消失
            #         pygame.sprite.collide_mask  # 使用掩码检测
            #     )
            #     if isover and not Manager.is_game_over:#避免重复触发
            #         #调用玩家受伤方法，判断是否死亡
            #         is_dead=player.take_damage()
            #         self.player_bomb.action(self.players.sprites()[0].rect)#显示受伤特效
            #         self.sound.playBombSound()
            #         if is_dead:#生命值归零时游戏结束
            #             Manager.is_game_over=True#标志着游戏结束
            #             pygame.time.set_timer(Manager.game_over_id,1000)#开始游戏倒计时
            #             #print("中弹")#在控制台输出
            #             self.player_bomb.action(self.players.sprites()[0].rect)#显示爆炸特效
            #             #把玩家飞机从精灵组移除
            #             self.players.remove(self.players.sprites()[0])
            #             #爆炸的声音
            #             self.sound.playBombSound()
            # #玩家和敌机的碰撞检测(使用掩码）
            # iscollide = pygame.sprite.groupcollide(
            #     self.players,
            #     self.enemies,
            #     True,  # 玩家碰撞后消失（但我们在take_damage中处理）
            #     True,  # 敌机碰撞后消失
            #     pygame.sprite.collide_mask  # 使用掩码检测
            # )
            # if iscollide and not Manager.is_game_over:
            #     # player=list(iscollide.keys())[0]#获取玩家
            #     # enemy=list(iscollide.values())[0][0]#获取敌机
            #     #碰撞造成2点伤害
            #     is_dead=player.take_damage(damage=2)
            #     #显示双方爆炸特效
            #     # self.player_bomb.action(player.rect)
            #     # self.enemy_bomb.action(enemy.rect)
            #     # self.sound.playBombSound()
            #     # if is_dead:
            #     #     Manager.is_game_over=True#标志着游戏结束
            #     #     pygame.time.set_timer(Manager.game_over_id,1000)#开启游戏倒计时
            #
            # #玩家子弹和所有敌机的碰撞判断
            # is_enemy = pygame.sprite.groupcollide(
            #     HeroPlane.bullets,
            #     self.enemies,
            #     True,  # 子弹碰撞后消失
            #     True,  # 敌机碰撞后消失
            #     pygame.sprite.collide_mask  # 使用掩码检测
            # )
            # if is_enemy:
            #     items=list(is_enemy.items())[0]#生成一个字典
            #     y=items[1][0]
            #     #敌机爆炸图片
            #     self.enemy_bomb.action(y.rect)
            #     #爆炸的声音
            #     self.sound.playBombSound()
            #修改
            # 敌机子弹与玩家的碰撞检测
            if self.players:
                player = self.players.sprites()[0]
                isover = pygame.sprite.spritecollide(
                    player,
                    EnemyPlane.enemy_bullets,
                    True,  # 碰撞后子弹消失
                    pygame.sprite.collide_mask  # 使用掩码检测
                )
                if isover and not Manager.is_game_over:
                    is_dead = player.take_damage()
                    self.player_bomb.action(player.rect)
                    self.sound.playBombSound()
                    if is_dead:
                        Manager.is_game_over = True
                        pygame.time.set_timer(Manager.game_over_id, 1000)

            # 玩家与敌机的碰撞检测
            iscollide = pygame.sprite.groupcollide(
                self.players,
                self.enemies,
                False,  # 玩家碰撞后自动移除（有生命值逻辑控制）
                True,  # 敌机碰撞后消失
                pygame.sprite.collide_mask  # 使用掩码检测
            )
            if iscollide and not Manager.is_game_over:
                player = list(iscollide.keys())[0]
                enemy = list(iscollide.values())[0][0]
                is_dead = player.take_damage(damage=2)
                self.player_bomb.action(player.rect)
                self.enemy_bomb.action(enemy.rect)
                self.sound.playBombSound()
                if is_dead:
                    Manager.is_game_over = True
                    pygame.time.set_timer(Manager.game_over_id, 1000)

            # 玩家子弹与敌机的碰撞检测
            is_enemy = pygame.sprite.groupcollide(
                HeroPlane.bullets,
                self.enemies,
                True,  # 子弹碰撞后消失
                True,  # 敌机碰撞后消失
                pygame.sprite.collide_mask  # 使用掩码检测
            )
            if is_enemy:
                for bullet, enemies_hit in is_enemy.items():
                    for enemy in enemies_hit:
                        self.enemy_bomb.action(enemy.rect)
                        self.sound.playBombSound()
            # 游戏结束时清空所有敌机
            if Manager.is_game_over and self.players.sprites() == []:
                # 玩家已清除，且游戏处于结束状态时，清空敌机
                self.enemies.empty()
                EnemyPlane.enemy_bullets.empty()
            #玩家和子弹的显示
            self.players.update()
            #敌机和子弹的显示
            self.enemies.update()
            #刷新窗口内容
            pygame.display.update()

            clock.tick_busy_loop(60)#使用pygame 1,x

if __name__ == "__main__":
    manager = Manager()
    manager.main()
