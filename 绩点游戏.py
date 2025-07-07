import random
import time
import cv2
import pygame
from pygame.locals import *
# 调试模式开关
DEBUG_MODE = False


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
        self.last_frame=None#保留上一帧
        self.last_frame_surface = None  # 保存转换后的Pygame Surface
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
        self.video_ended = False
        self.last_frame_time=pygame.time.get_ticks()#记录当前时间,作为播放开始的基准时间，用于控制视频帧率，确保视频按正常速度播放（避免因游戏帧率波动导致视频播放过快或过慢）
        # 预加载第一帧
        self._read_next_frame()

    def _read_next_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            if self.loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    self.playing = False
                    return False
            else:
                self.playing = False
                self.video_ended = True
                return False

        # 转换和缩放帧
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pygame_surface = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))

        if self.size != (self.original_width, self.original_height):
            pygame_surface = pygame.transform.scale(pygame_surface, self.size)

        self.last_frame = frame
        self.last_frame_surface = pygame_surface
        return True
    def update(self):
        if not self.playing:#检查播放器状态
            return self.last_frame_surface#返回最后一帧
        current_time=pygame.time.get_ticks()
        if current_time-self.last_frame_time<self.frame_delay:#计算与上一帧的时间差，若小于预设的帧延迟则跳过本次更新，保持原有的播放速度
            return self.last_frame_surface
        self.last_frame_time=current_time#更新上一帧的时间为当前时间，为下一帧延迟计算做准备
        if not self._read_next_frame():
            return self.last_frame_surface

        return self.last_frame_surface
        #self.screen.blit(pygame_surface,self.position)#将处理后的视频帧绘制到Pygame屏幕指定位置(self.position)
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
        self.max_hp=10#最大生命值
        self.current_hp=self.max_hp#初始化
        self.score=0
        #新增掩码
        self.mask=pygame.mask.from_surface(self.image)
        self.invincible=False#新增无敌状态
        self.last_hit_time=0#新增受伤时间记录
        self.attack_cooldown=0
        self.attack_cooldown_max=10#攻击最大冷却时间
        self.normal_image=self.image.copy()#正常状态图像
##
        self.hit_image=self.image.copy()#受伤状态图像
        self.hit_image.set_alpha(100)#设置受伤半透明效果

    def take_damage(self, damage=1):
        if self.invincible:
            return False
        self.current_hp -= damage
        self.last_hit_time = pygame.time.get_ticks()
        self.invincible = True
        self.image=self.hit_image  # 切换成受伤图像
        return self.current_hp <= 0
    def update(self):
        self.key_control()
        # 新增无敌状态更新
        current_time = pygame.time.get_ticks()
        if self.invincible and current_time - self.last_hit_time > 500:
            self.invincible = False
            self.image = self.normal_image
        # 新增攻击冷却更新
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        self.display()
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
        pygame.sprite.Sprite.__init__(self)
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
        self.mask = pygame.mask.from_surface(self.image)
        self.bullet_type = random.randint(1, 3)  # 1-3种类型
        self.damage = self.bullet_type  # 类型越高伤害越大
        self.speed = random.randint(3, 5) + self.bullet_type
##修改成我要的图片        # 修改为程序化生成子弹图像
        self.image = pygame.Surface((15, 25), pygame.SRCALPHA)
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]
        pygame.draw.rect(self.image, colors[self.bullet_type - 1], (0, 0, 15, 25))
    def update(self):
        # 修改子弹坐标
        self.rect.top += self.speed
        # 如果子弹移出屏幕上方，则销毁子弹对象
        if self.rect.top > self.screen.get_height():
            self.kill()


# 新版（多音效管理系统）：
class EnhancedSoundSystem:
    def __init__(self):
        self.sounds = {
            'attack': [pygame.mixer.Sound(f"attack{i}.wav") for i in range(3)],
            'hit': pygame.mixer.Sound("hit.wav"),
            'explosion': pygame.mixer.Sound("explosion.wav")
        }

    def play_attack_sound(self, count):
        index = min(count, 3) - 1
        self.sounds['attack'][index].play()
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
class CollisionSystem:
    def __init__(self, game_manager):
        self.manager = game_manager
        self.quadtree = Quadtree(0, pygame.Rect(0, 0, *Manager.bg_size))

    def update_quadtree(self):
        """更新四叉树空间分区"""
        self.quadtree.clear()
        for bullet in self.manager.random_bullets:
            self.quadtree.insert(bullet)

    def precise_collision_check(self, player, objects):
        """精确碰撞检测"""
        colliding_objects = []
        for obj in objects:
            # 使用圆形碰撞检测快速筛选
            dx = player.rect.centerx - obj.rect.centerx
            dy = player.rect.centery - obj.rect.centery
            distance_sq = dx * dx + dy * dy

            # 基于半径的快速预判
            min_distance = player.rect.width // 2 + obj.rect.width // 2
            if distance_sq < min_distance * min_distance:
                # 精确像素级碰撞检测
                if pygame.sprite.collide_mask(player, obj):
                    colliding_objects.append(obj)
        return colliding_objects

    def check_all_collisions(self):
        player = self.manager.players.sprites()[0] if self.manager.players else None
        if not player:
            return

        # 更新空间分区
        self.update_quadtree()

        # 获取玩家附近的子弹
        nearby_bullets = self.quadtree.retrieve(player.rect)

        # 处理攻击检测
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and player.attack_cooldown <= 0:
            # 精确检测攻击范围内的子弹
            attackable = self.precise_collision_check(player, nearby_bullets)

            for bullet in attackable:
                self.manager.handle_bullet_destruction(bullet)
                player.score += 10 * bullet.damage  # 根据子弹类型给分

            if attackable:
                player.attack_cooldown = player.attack_cooldown_max
                self.manager.sound.play_attack_sound(len(attackable))

        # 处理受伤检测
        collisions = self.precise_collision_check(player, nearby_bullets)
        if collisions:
            total_damage = sum(bullet.damage for bullet in collisions)
            self.manager.handle_player_damage(player, total_damage, collisions)
class Quadtree:
    def __init__(self, level, bounds, max_objects=10, max_levels=5):
        self.level = level
        self.bounds = bounds
        self.max_objects = max_objects
        self.max_levels = max_levels
        self.objects = []
        self.nodes = []

    def clear(self):
        self.objects.clear()
        for node in self.nodes:
            node.clear()
        self.nodes.clear()

    def split(self):
        sub_width = self.bounds.width // 2
        sub_height = self.bounds.height // 2
        x, y = self.bounds.x, self.bounds.y

        self.nodes = [
            Quadtree(self.level + 1, pygame.Rect(x, y, sub_width, sub_height)),
            Quadtree(self.level + 1, pygame.Rect(x + sub_width, y, sub_width, sub_height)),
            Quadtree(self.level + 1, pygame.Rect(x, y + sub_height, sub_width, sub_height)),
            Quadtree(self.level + 1, pygame.Rect(x + sub_width, y + sub_height, sub_width, sub_height))
        ]

    def get_index(self, rect):
        indexes = []
        vertical_midpoint = self.bounds.x + (self.bounds.width // 2)
        horizontal_midpoint = self.bounds.y + (self.bounds.height // 2)

        top = rect.y < horizontal_midpoint and rect.y + rect.height < horizontal_midpoint
        bottom = rect.y > horizontal_midpoint

        if rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top:
                return 0
            elif bottom:
                return 2
        elif rect.x > vertical_midpoint:
            if top:
                return 1
            elif bottom:
                return 3

        return -1  # 跨多个区域

    def insert(self, obj):
        if self.nodes:
            index = self.get_index(obj.rect)
            if index != -1:
                self.nodes[index].insert(obj)
                return

        self.objects.append(obj)

        if len(self.objects) > self.max_objects and self.level < self.max_levels:
            if not self.nodes:
                self.split()

            i = 0
            while i < len(self.objects):
                index = self.get_index(self.objects[i].rect)
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1

    def retrieve(self, rect):
        indexes = []
        if self.nodes:
            index = self.get_index(rect)
            if index != -1:
                indexes.extend(self.nodes[index].retrieve(rect))
            else:
                for node in self.nodes:
                    indexes.extend(node.retrieve(rect))

        indexes.extend(self.objects)
        return indexes


class VisualEffects:
    def __init__(self):
        self.effects = []

    def add_attack_wave(self, center, radius):
        surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 255, 150), (radius, radius), radius)
        pygame.draw.circle(surface, (255, 200, 0, 200), (radius, radius), radius - 10, 2)

        self.effects.append({
            'type': 'wave',
            'surface': surface,
            'rect': surface.get_rect(center=center),
            'radius': radius,
            'max_radius': radius * 1.5,
            'growth_rate': 5,
            'alpha': 150
        })

    def update(self):
        i = 0
        while i < len(self.effects):
            effect = self.effects[i]
            if effect['type'] == 'wave':
                effect['radius'] += effect['growth_rate']
                effect['alpha'] -= 5

                if effect['radius'] >= effect['max_radius'] or effect['alpha'] <= 0:
                    self.effects.pop(i)
                    continue

                # 更新surface
                new_surface = pygame.Surface((effect['radius'] * 2, effect['radius'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(new_surface, (255, 255, 255, effect['alpha']),
                                   (effect['radius'], effect['radius']), effect['radius'])
                pygame.draw.circle(new_surface, (255, 200, 0, effect['alpha'] + 50),
                                   (effect['radius'], effect['radius']), effect['radius'] - 10, 2)
                effect['surface'] = new_surface
                effect['rect'] = new_surface.get_rect(center=effect['rect'].center)
            i += 1

    def draw(self, screen):
        for effect in self.effects:
            if effect['type'] == 'wave':
                screen.blit(effect['surface'], effect['rect'], special_flags=BLEND_ADD)
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
        #self.sound=GameSound()
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
        self.collision_system=CollisionSystem(self)
        self.visual_effects=VisualEffects()
        self.clock=pygame.time.Clock()#游戏时钟
        self.delta_time=0#新增帧时间
    def handle_bullet_destruction(self,bullet):
        bomb = Bomb(self.screen, "enemy")
        bomb.action(bullet.rect)
        self.bullet_bombs.append(bomb)
        bullet.kill()
        self.sound.playBombSound()
        self.visual_effects.add_attack_wave(bullet.rect.center, 50)  # 新增特效
    def handle_player_damage(self, player, total_damage, bullets):
        """处理玩家受伤"""
        # 闪烁效果
        player.image.set_alpha(100)
        pygame.time.set_timer(pygame.USEREVENT + 3, 500, True)  # 0.5秒后恢复

        # 计算伤害
        damage = min(total_damage, 3)  # 每次最多3点伤害
        player.score = max(0, player.score - damage * 5)
        self.sound.play_hit_sound()#新增音效
        # 应用伤害
        if player.take_damage(damage):
            self.game_over_sequence(player)
        # 销毁造成伤害的子弹
        for bullet in bullets:
            self.handle_bullet_destruction(bullet)
    def game_over_sequence(self, player):
        """游戏结束处理"""
        Manager.is_game_over = True
        pygame.time.set_timer(Manager.create_bullet_id, 0)
        self.player_bomb.action(player.rect)
        self.sound.playBombSound()
        self.players.remove(player)
        # 结局判定
        ending = self.story_manager.check_ending()
        self.game_state = "ending"
        self.story_manager.start_ending(ending if ending else "bad")
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
        if self.game_state == "start_menu":
            self.screen.fill((0, 0, 0))
            self.drawText("时空游戏", 150, 200, textHeight=60)
            self.buttons["start_video"].draw(self.screen)
            self.buttons["quit"].draw(self.screen)
        elif self.game_state == "intro":
            # 清除屏幕
            self.screen.fill((0, 0, 0))
            # 更新并绘制视频帧
            video_surface = self.video_player.update()
            if video_surface is not None:
                self.video_player.draw(self.screen)

            skip_font = pygame.font.SysFont("SimHei", 50)
            skip_text = skip_font.render("按ESC跳过视频", True, (255, 255, 255))
            self.screen.blit(skip_text, (Manager.bg_size[0] - 200, Manager.bg_size[1] - 40))
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
            # 初始化游戏时钟和性能计数器
            clock = pygame.time.Clock()
            fps_counter = 0
            last_fps_time = time.time()
            delta_time = 0

            # 主游戏循环
            while True:
                # === 1. 帧率控制 ===
                delta_time = clock.tick(60) / 1000.0  # 转换为秒
                fps_counter += 1

                # 每秒输出帧率（调试用）
                if time.time() - last_fps_time >= 1:
                    print(f"FPS: {fps_counter}", end='\r')
                    fps_counter = 0
                    last_fps_time = time.time()

                # === 2. 事件处理 ===
                self.handle_events()

                # === 3. 游戏状态更新 ===
                if self.game_state == "playing":
                    # 更新背景滚动（保留原逻辑）
                    self.map.move()

                    # 更新玩家和子弹（使用delta_time保证帧率无关）
                    if self.players:
                        self.players.update(delta_time)

                    # 使用四叉树优化的碰撞检测
                    self.collision_system.check_all_collisions()

                    # 更新随机子弹位置（考虑delta_time）
                    for bullet in self.random_bullets:
                        bullet.rect.y += bullet.speed * 60 * delta_time
                        if bullet.rect.top > Manager.bg_size[1]:
                            bullet.kill()

                    # 更新视觉特效（冲击波等）
                    self.update_visual_effects()

                    # 自动生成新子弹（频率控制）
                    if pygame.time.get_ticks() % 1000 < delta_time * 1000:
                        self.create_random_bullet()

                # === 4. 渲染流程 ===
                # 绘制背景
                if self.game_state != "intro":
                    self.map.draw()
                # 状态特异性渲染
                if self.game_state == "playing":
                    # 绘制玩家和子弹
                    self.players.draw(self.screen)
                    self.random_bullets.draw(self.screen)

                    # 绘制爆炸特效
                    for bomb in self.bullet_bombs[:]:
                        bomb.draw(self.screen)
                        if not bomb.mVisible:
                            self.bullet_bombs.remove(bomb)

                    # 绘制玩家爆炸（如果存在）
                    if self.player_bomb.mVisible:
                        self.player_bomb.draw(self.screen)

                    # 绘制视觉特效（覆盖在实体上方）
                    self.draw_visual_effects(self.screen)

                    # 显示游戏信息
                    if self.players:
                        player = self.players.sprites()[0]
                        self.drawText(f'分数: {player.score}', 20, 20)
                        hp_color = (255, 0, 0) if player.invincible else (0, 255, 0)
                        self.drawText(f'生命: {player.current_hp}/{player.max_hp}',
                                      20, 60, fontColor=hp_color)

                        # 显示攻击冷却进度条
                        if player.attack_cooldown > 0:
                            cooldown_width = 100 * (1 - player.attack_cooldown / player.attack_cooldown_max)
                            pygame.draw.rect(self.screen, (255, 255, 0),
                                             (20, 100, cooldown_width, 10))
                elif self.game_state == "intro":
                    pass
                elif self.game_state == "ending":
                    # 结局剧情特殊渲染
                    self.story_manager.draw_story(self.screen)

                # === 5. 通用UI渲染 ===
                # 绘制当前状态的按钮（所有界面）
                self.buttons_draw()

                # === 6. 调试信息（可选）===
                # if DEBUG_MODE:
                #     self.drawText(f"Entities: {len(self.random_bullets)}",
                #                   Manager.bg_size[0] - 150, 20,
                #                   textHeight=20, fontColor=(255, 255, 255))
                #     self.collision_system.quadtree.draw_debug(self.screen)

                # === 7. 刷新显示 ===
                pygame.display.flip()

                # === 8. 游戏状态检查 ===
                if Manager.is_game_over and self.game_state == "playing":
                    self.handle_game_over()


if __name__ == "__main__":
    manager = Manager()
    manager.main()
