#!/usr/bin/python
# -*- coding: utf-8 -*-
# Authors: Emmanuel and Nick
# Description: T-Rex Bot game file, for use with Reinforcement Learning Capstone Project
import os
import random

import pygame

import gym
from gym.spaces import Discrete, Box
import numpy as np

pygame.init()

# Global Constants

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Chrome Dino Runner")

Ico = pygame.image.load("assets/DinoWallpaper.png")
pygame.display.set_icon(Ico)

RUNNING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),
]
JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
DUCKING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),
]

SMALL_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),
]
LARGE_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),
]

BIRD = [
    pygame.image.load(os.path.join("assets/Bird", "Bird1.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird2.png")),
]

CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))

import gym
from gym.spaces import Discrete, Box, Dict
import numpy as np

class DinoEnv(gym.Env):
    def __init__(self):

        global X_POS, Y_POS, Y_POS_DUCK, JUMP_VEL, game_speed, x_pos_bg, y_pos_bg, points, obstacles
        X_POS = 80
        Y_POS = 310
        Y_POS_DUCK = 340
        JUMP_VEL = 8.5
        self.clock = pygame.time.Clock()
        self.player = Dinosaur()
        self.cloud = Cloud()
        game_speed = 20
        x_pos_bg = 0
        y_pos_bg = 380
        points = 0
        obstacles = []

        self.action_space = Discrete(3)
        spaces = {
            'nearest_obs': Box(low = 0, high = 1100, shape = (1,)),
            'obs_height': Box(low = 225, high = 320, shape = (1,)),
            'obs_width': Box(low = 0, high = 200, shape = (1,)),
            'dino_height': Box(low = 0, high = 350, shape = (1,)),
            'high_bird': Discrete(2),
            'gamespeed': Box(low = 15, high = 10000, shape = (1,))
        }
        self.observation_space = Dict(spaces)
        self.state = [1100, 310, 0, 0, 0, 20]
    
    def step(self, action):
        min_distance = 1100
        obs_y = 0
        reward = 0
        done = False
        high_bird = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        self.player.update(action)

        if len(obstacles) == 0:
            rand = random.randint(0, 2)
            if rand == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif rand == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif rand == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            reward = obstacle.update()
            distance = obstacle.rect.x - (self.player.dino_rect.x + self.player.dino_rect.width)
            if self.player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(200)
                reward = -40
                done = True
            if distance < min_distance:
                min_distance = distance
                obs_y = obstacle.rect.y
                obs_width = obstacle.rect.width
                if obstacle.rect.y == 250:
                    high_bird = 1

        if min_distance >= 500 and action == 1:
            reward = -100
        elif 100 <= min_distance <= 130 and action == 1:
            reward = 500
        elif reward == 1 and action == 1:
            reward = -5
        

        self.cloud.update()

        score()

        self.clock.tick(30)
        pygame.display.update()

        self.state = [min_distance, obs_y, obs_width, self.player.dino_rect.y, high_bird, game_speed]
        info = {}
        return self.state, reward, done, info
    
    def render(self):
        SCREEN.fill((255, 255, 255))
        self.player.draw(SCREEN)
        background()
        self.cloud.draw(SCREEN)
        for obstacle in obstacles:
            obstacle.draw(SCREEN)

    def reset(self):
        self.state = [1100, 310, 0, 0, 0, 20]
        self.player.dino_reset()
        global game_speed, x_pos_bg, y_pos_bg, points, obstacles
        clock = pygame.time.Clock()
        cloud = Cloud()
        game_speed = 20
        x_pos_bg = 0
        y_pos_bg = 380
        points = 0
        obstacles = []
        return self.state

def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        font = pygame.font.Font("freesansbold.ttf", 20)
        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

class Dinosaur:
    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.height -= 10
        self.dino_rect.x = X_POS
        self.dino_rect.y = Y_POS

    def update(self, action):
        if self.step_index >= 10:
            self.step_index = 0

        if ((action == 1) and not self.dino_jump) and self.dino_rect.y >= 310:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif action == 2 and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or action == 2):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = X_POS
        self.dino_rect.y = Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = X_POS
        self.dino_rect.y = Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))
    
    def dino_reset(self):
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = X_POS
        self.dino_rect.y = Y_POS

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        reward = 1
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()
            reward = 5000
        return reward

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    BIRD_HEIGHTS = [225, 290, 320]

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1