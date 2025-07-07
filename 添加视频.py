import pygame
import cv2
from pygame.locals import *
import random
import time
class VideoPlayer:
    def __init__(self,screen,position=(0,0),size=None):
        self.screen = screen
        self.position = position
        self.size = size
        self.video_path=""#
        try:
            self.cap=cv2.VideoCapture(self.video_path)
            self.original_width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.original_height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.size=size or (self.original_width,self.original_height)
            self.playing=False
            self.loop=True
            self.frame_delay=int(1000/self.cap.get(cv2.CAP_PROP_FPS))
            self.last_frame_time=0
        except Exception as e:
            print(f"视频加载失败;{e}")
            self.playing=False

