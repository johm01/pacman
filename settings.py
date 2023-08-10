from csv import reader 
from os import walk
import pygame

def import_csv(path):
    map = []
    with open(path) as m:
        layout = reader(m,delimiter=',')
        for l in layout:
            map.append(list(l))
    return map 
    
def label(text,pos: tuple,size):
    sur = pygame.display.get_surface()
    font = pygame.font.SysFont("Arial",size)
    label = font.render(text,1,(255,0,255)) 
    return sur.blit(label,pos) 
    
def start_button(txt: str,size: int,pos: tuple,selected: bool,remove: bool):
    sur = pygame.display.get_surface()
    font = pygame.font.SysFont("Arial",size)
    button = font.render(txt,1,(0,0,255))
    return sur.blit(button,pos)

def create_frames(frames,img):
    sprite = []
    for i in range(0,frames + 1):
        sprite.append(f'{img}{i}.png')
    return sprite

def timer(time,action):
    curr_time = pygame.time.get_ticks()
    if curr_time >= time:
        action
