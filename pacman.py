import pygame
from settings import *
from sys import exit
import json 
import math 

# Sprite group
pac_group = pygame.sprite.Group()
ghost_group = pygame.sprite.Group()
consumable_group = pygame.sprite.Group()
power_pellet = pygame.sprite.Group()
collide_group = pygame.sprite.Group()
groups = [pac_group,ghost_group,power_pellet,consumable_group,collide_group]

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((895,1280))

class Pacman(pygame.sprite.Sprite):
    def __init__(self,pos,groups=pac_group) -> None:
        super().__init__(groups)
        # Basic animation
        self.animation_1 = create_frames(2,'./assets/pacman/pacman_') 
        # Death animation
        self.death_animation = create_frames(11,'./assets/pacman/dead/frame_')
        self.count = 0 
        self.pos = pos       
        self.sur = pygame.display.get_surface()
        self.image = pygame.image.load(self.animation_1[self.count]).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2(0,0)
        self.old_time = pygame.time.get_ticks()
        self.score = 0 
        self.lives = 3
        self.lives_img = []
        self.status = 'idle'
        self.hs = {'highscore':0}
        self.current_animation = self.animation_1 

    def display_lives(self):
        img = pygame.image.load('./assets/pacman/pacman_1.PNG').convert_alpha()
        rect = img.get_rect(topleft=(10 ,1205))
        for i in range(self.lives):
            self.lives_img.append(img)
            self.sur.blit(self.lives_img[i],(rect.x + i * 50,rect.y))
        
    def animate(self,animation,time):
        curr_time = pygame.time.get_ticks()
        if curr_time - self.old_time >= time:
            self.count += 1
            self.old_time = curr_time
            if self.count >= len(animation):
                self.count = 0
                if self.status == 'dead':
                    pac_group.empty()
            self.image = pygame.image.load(animation[self.count]).convert_alpha()

    def movement(self):
        keys = pygame.key.get_pressed()
        if self.status != 'dead':
            if keys[pygame.K_LEFT]:
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.status = 'right'
            else:
                self.direction.x = 0

            if keys[pygame.K_UP]:
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.status = 'down'
            else:
                self.direction.y =0
        
            if self.status == 'left':
                self.direction.x = -1
            elif self.status == 'right':
                self.direction.x = 1
            elif self.status == 'up':
                self.direction.y = -1
            elif self.status == 'down':
                self.direction.y = 1
        else:
            self.direction.y = 0
            self.direction.x = 0
    
    # Player/Ghost interaction
    def hit_ghost(self):
        for sprite in ghost_group:
            if sprite.rect.colliderect(self.rect):
                if sprite.state == None:
                    self.lives = self.lives - 1
                    self.respawn()
                    # Only checking lives if our ghost is in its normal state 
                    if self.lives <= 0:
                        self.status = 'dead'
                    else:
                        self.lives_img.pop()

                if sprite.state == 'Scared':
                    self.update_score(1000)
                    sprite.state = 'Caught'
                    print('yes')    
                
    def hit_food(self):
        for sprite in consumable_group:
            if sprite.rect.colliderect(self.rect):
                consumable_group.remove(sprite)
                self.update_score(10)
        
        for sprite in power_pellet:
            if sprite.rect.colliderect(self.rect):
                pellet_phase = True
                power_pellet.remove(sprite)
                print('ate power pellet')

                for sprite in ghost_group:
                    sprite.state = 'Scared'
                    timer = 52000
                    curr_time = pygame.time.get_ticks()
                    if curr_time >= timer:
                        sprite.state = None

    def hit_wall(self):
        self.rect.x += self.direction.x * 3
        for sprite in collide_group:
            if sprite.rect.colliderect(self.rect):
                if self.direction.x < 0:
                    self.rect.left = sprite.rect.right 
                elif self.direction.x > 0:
                    self.rect.right = sprite.rect.left

        self.rect.y += self.direction.y * 3
        for sprite in collide_group:
            if sprite.rect.colliderect(self.rect):
                if self.direction.y > 0:
                    self.direction.y = 0
                    self.rect.bottom = sprite.rect.top
                elif self.direction.y < 0:
                    self.direction.y = 0
                    self.rect.top = sprite.rect.bottom

        # Moving through the tunnels 
        if self.rect.x > 895:
            self.rect.x = (self.rect.x * -1) / 20

        if self.rect.x <= -75:
            self.rect.x = 895

    def respawn(self):
        respawn_timer = 1000
        curr_time = pygame.time.get_ticks()
        if curr_time >= respawn_timer:
            self.rect.x = self.pos[0]
            self.rect.y = self.pos[1]
            self.current_animation = self.animation_1

    # DO stuff with highscore 
    def set_highscore(self,score):
        with open('./highscore.json',mode='w') as hs:
            json.dump(score,hs)
    def get_highscore(self):
        new_hs = 0
        with open('./highscore.json', mode='r') as hs:
            new_hs += json.load(hs)
        return new_hs
    def update_score(self,score_amt):
        self.score += score_amt
        if self.score > self.get_highscore():
            self.hs['highscore'] = self.score
            self.set_highscore(self.hs['highscore'])

    def update(self):
        label(f"Current score: {str(self.score)}",(5,1155),45) 
        label(f"Highscore: {str(self.get_highscore())}",(510,1155),45)
        self.display_lives()
        self.hit_food()
        self.hit_wall()
        self.movement()
        self.animate(self.current_animation,300) 
        self.hit_ghost()

class Ghost(pygame.sprite.Sprite):
    def __init__(self,path,groups,img,target_rad,target,speed) -> None:
        super().__init__(groups)
        self.img = img
        self.power_pellet_eaten = './assets/ghosts/can_eat.png'
        self.image = pygame.image.load(self.img).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = path[0]
        self.state =  None
        self.target = None
        self.wall = collide_group
        self.speed = speed
        self.target_rad = target_rad
        self.path = path
        self.waypoint_index = 0
        self.spawn_pnt = (670,450)

    def state_machine(self):
        match self.state:
            case 'Scared':
                self.scared()
            case 'Caught':
                self.caught()
            case _:
                self.image = pygame.image.load(self.img).convert_alpha()

    def scared(self):
        self.image = pygame.image.load(self.power_pellet_eaten).convert()

    def caught(self):
        self.image = pygame.image.load('./assets/ghosts/caught.png').convert_alpha()
        #Teleport to respawn then move back first position in path when we change state back to scared 
        self.rect.center = self.spawn_pnt
        timer = 35000
        present_time = pygame.time.get_ticks()
        if present_time >= timer:
            self.state = None  
    
    def traverse_path(self):
        if (self.state == None) or (self.state == 'Scared'):
            if self.waypoint_index < len(self.path):
                target_pos = self.path[self.waypoint_index]
                dx = target_pos[0] - self.rect.centerx
                dy = target_pos[1] - self.rect.centery 
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance > self.speed:
                    angle = math.atan2(dy,dx)
                    new_x = self.rect.centerx + self.speed * math.cos(angle)
                    new_y = self.rect.centery + self.speed * math.sin(angle)
                    #new_rect = pygame.Rect(new_x,new_y,self.rect.width,self.rect.height)
                    #if not any(new_rect.colliderect(wall.rect) for wall in self.wall):
                    self.rect.centerx = new_x 
                    self.rect.centery = new_y
                
                # If our distance to the target is within the target radius 
               # if self.d_to_target(pacman) >= self.target_rad:
                 #   pass

                else:
                    self.waypoint_index += 1
            else:
                self.waypoint_index = 0 
    
    # Distance to our target
    def d_to_target(self,target):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance 
    
    def update(self):
        self.state_machine()
        self.traverse_path()
        print(self.state)

class Tile(pygame.sprite.Sprite):
    def __init__(self, groups,img,pos) -> None:
        super().__init__(groups)
        self.img = img 
        self.image = pygame.image.load(self.img)
        self.rect = self.image.get_rect(topleft=pos)

class Level:
    def __init__(self,lvl) -> None:
        self.lvl = lvl
        self.clock = pygame.time.Clock()
        self.sur = pygame.display.get_surface()
        self.remove = False
        self.selected = False
        self.game_started = False

    def level_gen(self):
        for row_index,row in enumerate(import_csv(self.lvl)):
            for col_index,col in enumerate(row):
                x = row_index * 32
                y = col_index * 32

                if col == '28':
                    Tile(groups=consumable_group,img='./assets/food.png',pos=(y+10,x+10))
                if col == '11':
                    Tile(groups=collide_group,img='./assets/tile.png',pos=(y,x))
                if col == '31':
                    Tile(groups=power_pellet,img='./assets/power_pellet.png',pos=(y,x))

    def start_game(self):
        run = True 
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.keys = pygame.key.get_pressed()

            self.sur.fill((0,0,0))
            self.draw_level(self.sur)
            pygame.display.update()
            self.clock.tick(60)

    def draw_level(self,sur):
        for i in range(len(groups)):
            groups[i].update()
            groups[i].draw(sur)

    def remove_level(self):
        for i in range(len(groups)):
            groups[i].empty()
            groups[i].update()

# TODO 
# Finish paths for all four ghosts 
# figure out when we want to set a target for the ghost 
# Complete audio

pellet_phase = False
def power_pellet_phase(phase):
    if phase:
        timer = 12000
        curr_time = pygame.time.get_ticks()
        print(curr_time)
        if curr_time > timer:
            curr_time = pygame.time.get_ticks()
            phase = False
            ghost_2.state = None
            print('Balls')

# Blinky path         
path_1 = [(105,465),(100,465),(95,465),(80,465)]
# Pinky path 
path_2 = [ (100,142),(175,142),(245,142),
          (250,142),(400,142),(399,176),
          (470,176),(500,176),(590,176),
          (591,191),(591,271),(497,271),
          (497,401),(305,401),(305,491,),
          (197,491),(197,301),(97,301),  
          ]

ghost_paths = {
        'blinky':path_1,
        }

pacman = Pacman(pos=(800,800),groups=pac_group)
ghost = Ghost(groups=ghost_group,img='./assets/ghosts/ghost_1.PNG',speed=4,target=pacman,target_rad=0,path=path_1)
ghost_2 = Ghost(groups=ghost_group,img='./assets/ghosts/ghost_2.png',speed=2,target=pacman,target_rad=50,path=path_2)

lvl = Level('./map_2.csv')
lvl.level_gen()
lvl.start_game()


