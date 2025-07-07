import random
import time
from turtledemo.clock import current_day

import cv2
import pygame
from pygame.locals import *

class Button:
    def __init__(self,x,y,width,height,text,color,hover_color,action=None):
        self.rect=pygame.Rect(x,y,width,height)
        self.text=text
        self.color=color
        self.hover_color=hover_color
        self.action=action#按钮点击后执行的函数
        self.current_color=color
        self.border_width=2
        self.border_color=(255,255,255)
        self.font=pygame.font.SysFont("SimHei", 30)
    def draw(self,screen):
        #检查鼠标是否悬停在按钮上
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.current_color=self.hover_color
        else:
            self.current_color=self.color
        #绘制按钮背景
        pygame.draw.rect(screen,self.current_color,self.rect,border_radius=15)#圆角是15
        pygame.draw.rect(screen,self.border_color,self.rect,border_radius=15,width=self.border_width)

        #绘制按钮文本
        text_surface=self.font.render(self.text,True,(255,255,255))
        text_rect=text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface,text_rect)
    def handle_event(self,event):
        #处理按钮点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1 and self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False

class VideoPlayer:
    def __init__(self,screen,position=(0,0),size=None):
        self.screen = screen
        self.position = position
        self.size = size
        self.load_failed=False
        self.video_path=r"D:\code_python\plane_game_team_1\素材库\测试视频.mp4"#
        self.video_ended=False#标记视频是否播放完毕
        try:
            self.cap=cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                raise IOError("Cannot open video file")
            self.original_width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.original_height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.size=size or (self.original_width,self.original_height)
            self.playing=False#视频播放器的状态
            self.loop=False
            self.frame_delay=int(1000/self.cap.get(cv2.CAP_PROP_FPS))
            self.last_frame_time=0
        except Exception as e:
            print(f"视频加载失败;{e}")
            self.playing=False
            self.load_failed=True
    def play(self):
        self.playing=True
        self.last_frame_time=pygame.time.get_ticks()#记录当前时间,作为播放开始的基准时间，用于控制视频帧率，确保视频按正常速度播放（避免因游戏帧率波动导致视频播放过快或过慢）
    def update(self):
        if not self.playing:#检查播放器状态
            return
        current_time=pygame.time.get_ticks()
        if current_time-self.last_frame_time<self.frame_delay:#计算与上一帧的时间差，若小于预设的帧延迟则跳过本次更新，保持原有的播放速度
            return
        self.last_frame_time=current_time#更新上一帧的时间为当前时间，为下一帧延迟计算做准备
        ret,frame=self.cap.read()#读取视频帧,frame时OpenCV格式的视频帧（numpy数组，BGR格式）
        if not ret:#是否成功读取到帧，这个是未成功读取帧，说明视频已经播放完毕
            if self.loop:#True表示循环播放
                self.cap.set(cv2.CAP_PROP_POS_FRAMES,0)#将视频指针重置到第一帧
                ret,frame=self.cap.read()
                if not ret:#读取失败，停止播放
                    self.playing=False
                    return
            else:#不循环播放，则停止播放
                self.playing=False
                self.video_ended=True#标记视频结束
                return
        rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)#将BGR转换成RGB格式
        pygame_surface=pygame.surfarray.make_surface(rgb_frame.swapaxes(0,1))#将numpy数组转换成Pygame可渲染的Surface对象，
        # swapaxes交换数组的维度（OpenCV的帧是【高度，宽度，通道】）需转换成【宽度，高度，通道】
        if self.size!=(self.original_width,self.original_height):#若需要调整视频的尺寸，缩放Surface
            pygame_surface=pygame.transform.scale(pygame_surface,self.size)
        self.screen.blit(pygame_surface,self.position)#将处理后的视频帧绘制到Pygame屏幕指定位置(self.position)
    def is_video_ended(self):
        return self.video_ended and not self.playing
class HeroPlane(pygame.sprite.Sprite):
    #存放所有飞机子弹的组
    bullets = pygame.sprite.Group()
    def __init__(self,screen):
        pygame.sprite.Sprite.__init__(self)
        #记录当前窗口对象
        self.screen = screen
        #===创建一个玩家飞机图片，当作真正的飞机
        self.image = pygame.image.load("D:\\code_python\\plane game\\飞机大战素材\\images\\me1.png")
        #根据图片获取矩形对象
        self.rect = self.image.get_rect()
        self.rect.topleft = [Manager.bg_size[0]/2-100/2,500]#x,y
        #飞机速度
        self.speed = 10
        #子弹列表
        self.bullets=pygame.sprite.Group()
        #新增生命值属性
        self.max_hp=8#最大生命值
        self.current_hp=self.max_hp#初始化
        self.score=0
        #新增掩码
        self.mask=pygame.mask.from_surface(self.image)
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

    def update(self):
        self.key_control()
        self.display()
    def display(self):
        # 将飞机图片贴到窗口中
        self.screen.blit(self.image,self.rect)
        #更新子弹坐标
        self.bullets.update()
        #把所有子弹全部添加到屏幕
        self.bullets.draw(self.screen)
    @classmethod
    def clear_bullets(cls):
        #清空子弹
        cls.bullets.empty()

class RandomBullet(pygame.sprite.Sprite):
    def __init__(self,screen):
        #初始化精灵类
        pygame.sprite.Sprite.__init__(self)
        #图片
        self.image_paths=[f"D:\\code_python\\plane_game_team_1\\素材库\\课本图\\1 ({v}).jpg"for v in range(1,6)]#5*11
        random_path=random.choice(self.image_paths)
        try:
            self.image=pygame.image.load(random_path).convert_alpha()
        except FileNotFoundError:
            self.image=pygame.Surface((10,20))
            self.image.fill((255,0,0))
        #获取矩形对象
        self.rect = self.image.get_rect()
        # 屏幕顶部随机位置生成
        self.rect.x = random.randint(0, Manager.bg_size[0] - self.rect.width)
        self.rect.y = -self.rect.height  # 从屏幕外进入
        self.screen = screen
        self.speed = random.randint(3, 8)  # 随机速度
        self.mask = pygame.mask.from_surface(self.image)
        # self.rect.topleft = [x,y]
        # #窗口
        # self.screen = screen
        # self.speed = 10
        # # 新增掩码
        # self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        # 修改子弹坐标
        self.rect.top += self.speed
        # 如果子弹移出屏幕上方，则销毁子弹对象
        if self.rect.top > self.screen.get_height():
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
        elif type=="player":#玩家爆炸的资源要修改
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
    def draw(self,screen):
        if self.mVisible:
            if self.mIndex<len(self.mImage):
                screen.blit(self.mImage[self.mIndex],self.mPos)
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
        self.Image1=pygame.image.load("D:\\code_python\\plane_game_team_1\\素材库\\课本图\\生成地图.png")#地图的地址
        self.Image2=pygame.image.load("D:\\code_python\\plane_game_team_1\\素材库\\课本图\\生成地图.png")
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
class SaveSystem:
    @staticmethod
    def save_endings(unlocked_endings):
        try:
            with open("endings.save", "w") as f:
                f.write(",".join([k for k, v in unlocked_endings.items() if v]))
        except:
            print("存档失败")

    @staticmethod
    def load_endings():
        try:
            with open("endings.save", "r") as f:
                data = f.read().split(",")
                return {ending: True for ending in data}
        except:
            print("读取存档失败")
            return {
                "ending_bad": False,
                "ending_normal": False,
                "ending_good": False,
                "ending_secret": False
            }
class StoryManager:
    def __init__(self,Manager):
        self.manager=Manager
        self.current_story=None
        self.current_line=0
        self.story_progress=0
        self.story_active=False
        self.text_box_rect=pygame.Rect(50,Manager.bg_size[1]-150,Manager.bg_size[0]-100,120)
        self.text_font=pygame.font.SysFont("Arial",20)
        self.name_font=pygame.font.SysFont("Arial",28,bold=True)
        self.unlocked_endings = SaveSystem.load_endings()
        #样例
        # 仅保留结局相关剧情
        self.endings = {
            "bad": {
                "condition": lambda: self.manager.get_player_score() < 200,
                "unlocked": False,
                "lines": [
                    {"name": "系统", "text": "任务失败...城市遭受了严重破坏"},
                    {"name": "系统", "text": "结局评级：D [分数<200]"}
                ]
            },
            "normal": {
                "condition": lambda: 200 <= self.manager.get_player_score() < 500,
                "unlocked": False,
                "lines": [
                    {"name": "系统", "text": "任务完成！基本保护了城市安全"},
                    {"name": "系统", "text": "结局评级：B [200≤分数<500]"}
                ]
            },
            "good": {
                "condition": lambda: self.manager.get_player_score() >= 500,
                "unlocked": False,
                "lines": [
                    {"name": "系统", "text": "杰出表现！完美保护了城市"},
                    {"name": "系统", "text": "结局评级：A [分数≥500]"}
                ]
            },
            "perfect": {
                "condition": lambda: (self.manager.get_player_score() >= 800
                                      and self.manager.get_player_damage_count() == 0),
                "unlocked": False,
                "lines": [
                    {"name": "系统", "text": "完美无缺！创造了新的防御记录"},
                    {"name": "系统", "text": "结局评级：S [分数≥800且零伤亡]"}
                ]
            }
        }

    def check_ending(self):
        """检查并返回达成的结局"""
        for ending_name, ending in self.endings.items():
            if ending["condition"]() and not ending["unlocked"]:
                ending["unlocked"] = True
                return ending_name
        return None

    def start_ending(self, ending_name):
        """开始播放结局剧情"""
        if ending_name in self.endings:
            self.current_story = self.endings[ending_name]["lines"]
            self.current_line = 0
            self.story_active = True
            return True
        return False

    def next_line(self):
        """推进到下一句对话"""
        if self.current_story and self.current_line < len(self.current_story) - 1:
            self.current_line += 1
            return True
        else:
            self.story_active = False
            return False

    def draw_story(self, screen):
        """绘制剧情对话框"""
        if not self.story_active or not self.current_story:
            return

        # 绘制半透明背景框
        s = pygame.Surface((self.text_box_rect.width, self.text_box_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        screen.blit(s, self.text_box_rect.topleft)

        # 绘制当前对话
        line_data = self.current_story[self.current_line]
        name_text = self.name_font.render(line_data["name"], True, (255, 215, 0))
        screen.blit(name_text, (self.text_box_rect.x + 20, self.text_box_rect.y + 10))

        text = line_data["text"]
        text_surface = self.text_font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (self.text_box_rect.x + 20, self.text_box_rect.y + 50))

        # 绘制提示文本
        prompt = self.text_font.render("按空格键继续...", True, (200, 200, 200))
        screen.blit(prompt, (self.text_box_rect.right - 150, self.text_box_rect.bottom - 30))
class Manager(object):
    bg_size=(500,889)#地图的像素
    #创建敌机定时器的id
    create_bullet_id = pygame.USEREVENT + 1
    #游戏结束，倒计时的id
    game_over_id=pygame.USEREVENT+2
    #游戏是否结束
    is_game_over=False
    #倒计时时间,重开游戏的倒计时
    over_time=3
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(Manager.bg_size,0,32)#像素，位深
        self.map=GameBackground(self.screen)
        self.players=pygame.sprite.Group()
        self.random_bullets=pygame.sprite.Group()
        self.player_bomb=Bomb(self.screen,"player")
        self.bullet_bombs=[]
        self.sound=GameSound()
        pygame.font.init()
        self.font=pygame.font.SysFont("SimHei",50)
        self.video_player=VideoPlayer(self.screen,position=(0,0),size=Manager.bg_size)
        #self.video_player.play()
        #游戏状态
        self.game_state="start_menu"
        #创建按钮
        self.buttons=self.create_buttons()
        self.game_over_timer=0
        self.story_manager=StoryManager(self)
    def create_buttons(self):
        button_width = 200
        button_height = 60
        center_x=Manager.bg_size[0]//2-button_width//2
        button_y = Manager.bg_size[1] // 2
        return{
            "start_video":Button(center_x,button_y,button_width,button_height,"开始游戏",(50,150,50),(100,200,100),self.go_to_intro),
            "start_game":Button(center_x,button_y,button_width,button_height,"开始游戏",(50,150,50),(100,200,100),self.start_game),
            "continue_after_video":Button(center_x,button_y,button_width,button_height,"继续前进",(50,150,50),(100,200,100),self.go_to_intro_end),
            "paused":Button(center_x,button_y,button_width,button_height,"暂停游戏",(50,150,50),(100,200,100),self.pause_game),
            "quit":Button(center_x,button_y+80,button_width,button_height,"退出游戏",(50,150,50),(100,200,100),self.quit_game),
            "resume":Button(center_x,button_y,button_width,button_height,"继续游戏",(50,150,50),(100,200,100),self.resume_game),
            "setting":Button(center_x+120,button_y+400,button_width,button_height,"菜单",(50,150,50),(100,200,100),self.pause_game),
            #"game_over":Button(center_x,button_y,button_width,button_height,"退出游戏",(50,150,50),(100,200,100)),
            "restart":Button(center_x,button_y,button_width,button_height,"重新开始",(50,150,50),(100,200,100),self.restart_game),
            "gallery": Button(center_x, button_y + 160, button_width, button_height,
                              "结局画廊", (100, 50, 150), (150, 100, 200), self.show_ending_gallery)
            #"start_video":Button(center_x,button_y,button_width,button_height,"开始游戏",(50,150,50),(100,200,100)),
            }
    #界面一进入视频
    #界面二进入游戏
    #界面三可以进行游戏暂停等功能
    def play_intro_video(self):
        self.game_state="intro"
        self.video_player.play()
        # video_clock=pygame.time.Clock()
        # while  self.game_state=="intro":
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             pygame.quit()
        #             exit()
        #         elif event.type == pygame.KEYDOWN:
        #             if event.key == pygame.K_ESCAPE:
        #                 self.game_state="continue_after_video"
        #                 return
    def go_to_intro(self):
        self.game_state="intro"
        #self.video_player.playing=True
        self.start_video()
    def go_to_intro_end(self):
        self.game_state="continue_after_video"
    def start_video(self):
        self.video_player.play()



    def start_game(self):
        #if self.game_state=="menu":
        self.game_state="playing"
        Manager.is_game_over=False
        #重新开始游戏，有些类属性要清空
        self.players.empty()
        self.random_bullets.empty()
        self.bullet_bombs.clear()
        HeroPlane.clear_bullets()
        self.new_player()
        pygame.time.set_timer(Manager.create_bullet_id,100)
    def restart_game(self):
        self.start_game()
        self.game_over_timer=0
    def pause_game(self):
        #self.game_state="paused"
        if self.game_state=="playing":
            self.game_state = "paused"
            pygame.time.set_timer(Manager.create_bullet_id,0)
        elif self.game_state=="paused":
            self.game_state = "playing"
            pygame.time.set_timer(Manager.create_bullet_id,100)
    def resume_game(self):

        self.game_state="playing"
        pygame.time.set_timer(Manager.create_bullet_id,100)

    def quit_game(self):

        pygame.quit()
        exit()

    def get_player_score(self):
        if self.players.sprites():
            return self.players.sprites()[0].score
        return 0

    def get_player_damage_count(self):
        if self.players.sprites():
            player = self.players.sprites()[0]
            return player.max_hp - player.current_hp
        return 0
    def new_player(self):
        #创建飞机对象。添加到玩家的组
        player=HeroPlane(self.screen)
        player.score=0
        self.players.add(player)
    def create_random_bullet(self):
        if not Manager.is_game_over:
            bullet=RandomBullet(self.screen)
            self.random_bullets.add(bullet)
    # def new_enemy(self):
    #     enemy=EnemyPlane(self.screen)
    #     self.enemies.add(enemy)
    #绘制文字
    def check_collision(self):
        if not self.players or Manager.is_game_over:
            return

        player = self.players.sprites()[0]

        # 优化1：使用更高效的空间键攻击检测
        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            # 获取所有在攻击范围内的子弹
            attack_radius = 100  # 攻击范围半径
            near_objects = [obj for obj in self.random_bullets.sprites()
                            if pygame.sprite.collide_circle_ratio(0.7)(player, obj)]

            for obj in near_objects:
                # 生成爆炸特效
                bomb = Bomb(self.screen, "enemy")
                bomb.action(obj.rect)
                self.bullet_bombs.append(bomb)

                # 加分并销毁子弹
                player.score += 10
                obj.kill()
                self.sound.playBombSound()

        # 优化2：更精确的碰撞检测
        # 使用分组碰撞检测提高效率
        collisions = pygame.sprite.spritecollide(
            player, self.random_bullets, True, pygame.sprite.collide_mask
        )

        if collisions:
            # 优化3：根据碰撞严重程度计算伤害
            damage = min(len(collisions), 3)  # 每次最多受到3点伤害
            player.score = max(0, player.score - damage * 5)

            # 玩家受伤
            if player.take_damage(damage):
                Manager.is_game_over = True
                pygame.time.set_timer(Manager.create_bullet_id, 0)
                self.player_bomb.action(player.rect)
                self.sound.playBombSound()
                self.players.remove(player)

                # 游戏结束时检查结局
                ending = self.story_manager.check_ending()
                if ending:
                    self.game_state = "ending"
                    self.story_manager.start_ending(ending)
                else:
                    self.game_state = "ending"
                    self.story_manager.start_ending("bad")

    def show_ending_gallery(self):
        """显示已解锁的结局"""
        self.screen.fill((0, 0, 0))
        self.drawText("结局画廊", 150, 50, textHeight=60)

        endings = [
            ("bad", "D级结局", "分数<200", (100, 150)),
            ("normal", "B级结局", "200≤分数<500", (100, 220)),
            ("good", "A级结局", "分数≥500", (100, 290)),
            ("perfect", "S级结局", "分数≥800且零伤亡", (100, 360))
        ]

        for ending_id, title, condition, pos in endings:
            # 检查是否已解锁
            unlocked = self.story_manager.endings[ending_id]["unlocked"]
            color = (0, 255, 0) if unlocked else (100, 100, 100)

            # 绘制结局标题和状态
            status = "(已解锁)" if unlocked else "(未解锁)"
            self.drawText(f"{title} {status}", pos[0], pos[1], fontColor=color)

            # 绘制解锁条件
            if not unlocked:
                self.drawText(f"解锁条件: {condition}", pos[0] + 250, pos[1],
                              textHeight=20, fontColor=(150, 150, 150))

        self.drawText("按ESC返回主菜单", 150, Manager.bg_size[1] - 50, textHeight=30)
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
    def handle_events(self):
        #处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "gallery":
                        self.game_state = "start_menu"
                # 处理结局剧情的空格键继续
                if event.key == pygame.K_SPACE and self.game_state == "ending":
                    if not self.story_manager.next_line():
                        self.game_state = "game_over"  # 剧情结束后进入游戏结束界面
            elif event.type == Manager.create_bullet_id:
                self.create_random_bullet()
            #处理按钮
            if self.game_state=="start_menu":#开始界面
                self.buttons["start_video"].handle_event(event)
                self.buttons["quit"].handle_event(event)
            elif self.game_state=="start_video":
                #播放视频
                self.start_video()
            elif self.game_state=="intro":
                self.video_player.update()#更新视频帧
                if event.type == pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                    self.game_state="continue_after_video"
                elif self.video_player.is_video_ended():
                    self.game_state="continue_after_video"
            elif self.game_state=="continue_after_video":
                self.buttons["start_game"].handle_event(event)
                self.buttons["quit"].handle_event(event)
            elif self.game_state=="paused":
                self.buttons["resume"].handle_event(event)
                self.buttons["quit"].handle_event(event)
            elif self.game_state=="playing":
                self.buttons["setting"].handle_event(event)
            elif self.game_state=="game_over":
                self.buttons["restart"].handle_event(event)
                self.buttons["quit"].handle_event(event)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.game_state == "story":
                    if not self.story_manager.next_line():
                        # 如果故事结束，检查是否需要触发特殊事件
                        if self.story_manager.current_story == self.story_manager.stories["intro"]:
                            self.start_game()
    def buttons_draw(self):
        if self.game_state=="start_menu":
            self.screen.fill((0, 0, 0))
            self.drawText("飞机游戏", 150, 200, textHeight=60)
            self.buttons["start_video"].draw(self.screen)
            self.buttons["quit"].draw(self.screen)
        if self.game_state=="intro":
            #视频播放时绘制视频帧
            self.video_player.update()
            skip_font=pygame.font.SysFont("SimHei",50)
            skip_text=skip_font.render("按ESC跳过视频",True,(255,255,255))
            self.screen.blit(skip_text,(Manager.bg_size[0] - 200, Manager.bg_size[1] - 40))
        elif self.game_state=="continue_after_video":
            self.screen.fill((0, 0, 0))
            self.buttons["start_game"].draw(self.screen)
            self.buttons["quit"].draw(self.screen)
        elif self.game_state=="paused":
            #半透明覆盖层
            s=pygame.Surface(Manager.bg_size)
            s.set_alpha(150)
            s.fill((0,0,0))
            self.screen.blit(s,(0,0))
            self.drawText("游戏暂停", 150, 200, textHeight=60)
            self.buttons["resume"].draw(self.screen)
            self.buttons["quit"].draw(self.screen)
        elif self.game_state=="playing":
            self.map.move()
            self.map.draw()
            self.buttons["setting"].draw(self.screen)
            if self.players:
                player=self.players.sprites()[0]
                self.drawText(f'分数：{player.score}', 50, 70)
                self.drawText(f'生命值: {player.current_hp}/{player.max_hp}', 50, 30, fontColor=(0, 255, 0))
        elif self.game_state == "ending":
            # 游戏结束时的结局剧情展示
            self.map.move()
            self.map.draw()
            if self.players:
                self.players.draw(self.screen)
            self.story_manager.draw_story(self.screen)

        elif self.game_state == "game_over":
            # 结局剧情后的统计界面
            s = pygame.Surface(Manager.bg_size)
            s.set_alpha(150)
            s.fill((0, 0, 0))
            self.screen.blit(s, (0, 0))

            self.drawText("游戏结束", 150, 200, textHeight=60)
            if self.players.sprites():
                player = self.players.sprites()[0]
                self.drawText(f'最终分数: {player.score}', 150, 280)

            # 显示重新开始和退出按钮
            self.buttons["restart"].draw(self.screen)
            self.buttons["quit"].draw(self.screen)
    def main(self):
        self.sound.playBackgroundMusic()
        clock=pygame.time.Clock()
        while True:
            self.handle_events()
            # 更新游戏状态
            if Manager.is_game_over and self.game_state == "playing":
                self.game_state = "game_over"
            # 绘制当前状态界面
            self.buttons_draw()
            #游戏逻辑更新

            if self.game_state == "playing":
                if self.players:
                    self.players.update()
                self.random_bullets.update()
                self.random_bullets.draw(self.screen)
                self.check_collision()
            #绘制子弹爆炸特效
            for bomb in self.bullet_bombs[:]:
                bomb.draw(self.screen)
                if not bomb.mVisible:
                    self.bullet_bombs.remove(bomb)
            #绘制玩家爆炸特效
            if self.player_bomb.mVisible:
                self.player_bomb.draw(self.screen)
            # 刷新窗口内容
            pygame.display.update()
            clock.tick_busy_loop(60)  # 使用pygame 1,x


if __name__ == "__main__":
    manager = Manager()
    manager.main()
