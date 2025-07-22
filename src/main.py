import pygame, math, sys, random
import numpy as np
import pygame.freetype
from pygame.locals import*


img = pygame.image.load('./resources/hit_marker.png')
width, height = 1280, 720

pygame.init()
screen = pygame.display.set_mode((width, height))
font = pygame.freetype.Font('./resources/Pixeltype.ttf', 60)
pygame.display.set_caption("Gaem")
clock = pygame.time.Clock()


class Bullet:
    def __init__(self, pos, target, speed = 5, radius = 5, color='White', damage = 1):
        self.x,self.y = pos
        self.target = target
        self.speed = speed
        self.radius = radius
        self.color = color
        self.damage = damage

        dx = target[0] - self.x
        dy = target[1] - self.y
        diff = math.hypot(dx, dy) # get hypotenus (distance from pos to target)

        self.xinc = dx/diff * speed
        self.yinc = dy/diff * speed

    def move(self):
        self.x += self.xinc
        self.y += self.yinc

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def off_screen(self):
        return self.x<0 or self.y<0 or self.x>width or self.y>height

class Character:
    def __init__(self, radius=15, center=(width/2, height/2), color='White', hp = 100, damage = 10):
        self.color=color
        self.radius=radius
        self.center=center
        self.speed=8
        self.toggle=1
        self.bullets = []
        self.hp = hp
        self.damage = damage

    def draw(self, surface = screen):
        pygame.draw.circle(surface, self.color, self.center, self.radius)

    def move(self, speed = None):
        if speed == None:
            speed = self.speed

        keys = pygame.key.get_pressed()
        x,y=self.center

        if keys[pygame.K_w]: y -= speed
        if keys[pygame.K_a]: x -= speed
        if keys[pygame.K_s]: y += speed
        if keys[pygame.K_d]: x += speed

        if x<0 or y<0 or x>width or y>height: return
        self.center=x,y

    def shoot(self):
        target = pygame.mouse.get_pos() 
        bullet = Bullet(self.center, target)
        self.bullets.append(bullet)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.off_screen():
                self.bullets.remove(bullet)



class Enemy(Character):
    def __init__(self, center, speed=2, radius=20, color='Red', damage=10):
        super().__init__(radius=radius, center=center, color=color)
        self.speed = speed  # Override player's speed if needed
        self.hp = 20
        self.damage = damage

    def chase(self, target_pos):
        x, y = self.center
        tx, ty = target_pos
        dx, dy = tx - x, ty - y
        dist = math.hypot(dx, dy)

        if dist != 0:
            dx /= dist
            dy /= dist
            x += dx * self.speed
            y += dy * self.speed
            self.center = (x, y)

    def check_death(self):
        return self.hp <= 0
    
class Boss(Enemy):
    def __init__(self, center, radius=30, hp=100, speed=1.5, **kwargs):
        super().__init__(center=center, radius=radius, color='Purple', **kwargs)
        self.hp = hp
        self.speed = speed
        self.damage = 20

    

def handle_bullets(player, timer, rate):
    timer+=1
    if timer>=rate:
        player.shoot()
        timer=0

    player.update_bullets()
    return timer

def handle_enemy_spawn(timer, rate, enemies):
    timer += 1
    if timer > rate:
        rand_x = random.choice([random.randint(-100, -40), random.randint(width+40, width+100)])
        rand_y = random.randint(0, height)
        enemy = Enemy(center=(rand_x, rand_y))
        enemies.append(enemy)
        timer = 0
    return timer

def spawn_boss(kills, enemies):
    rand_x = random.choice([random.randint(-100, -40), random.randint(width+40, width+100)])
    rand_y = random.randint(0, height)
    enemy = Boss(hp=(kills/2)*10 ,center=(rand_x, rand_y), damage=2)
    enemies.append(enemy)

def update_enemy(enemies):
    for enemy in enemies:
        enemy.chase(player.center)
        enemy.draw()



player = Character(color='Green')
shoot_timer = 0
shoot_rate = 25 # lower = faster

enemies = []
spawn_timer = 0
spawn_rate = 120 # lower = faster
kill_count = 7

cooldown = 30
level = 1
boss_summoned=False



# main game loop
while True:
    #exit handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()


    pygame.mouse.set_cursor(pygame.cursors.diamond)
    screen.fill((50,50,50))

    player.draw()

    if pygame.key.get_pressed()[pygame.K_LSHIFT]: # more precise/slower movement if you press shift
        player.move(speed = 4)
    else:
        player.move()

    shoot_rate = 25-level
    shoot_timer = handle_bullets(player, shoot_timer, shoot_rate)

    spawn_rate = 120- level*2
    spawn_timer = handle_enemy_spawn(spawn_timer, spawn_rate, enemies)

    update_enemy(enemies)


    # handle collision
    # bullet vs enemy
    for bullet in player.bullets[:]:
        for enemy in enemies[:]:
            dx = enemy.center[0] - bullet.x
            dy = enemy.center[1] - bullet.y
            dist = math.hypot(dx, dy)
            if dist < enemy.radius + bullet.radius: # enemy + bullet radius
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
                    enemy.hp -= player.damage

                    # kill enemy if 0 hp
                    if enemy.check_death():
                        enemies.remove(enemy)
                        kill_count+=1

                        if isinstance(enemy, Boss): 
                            boss_summoned = False
                            level += 1
                            player.hp += 20
                            if level>10: level=10

                    # display hit marker
                    hit_marker_pos = np.array(enemy.center) + np.array([0, -20])
                    screen.blit(img, hit_marker_pos)

    #player vs enemy
    cooldown-=1
    if cooldown <=0:
        for enemy in enemies[:]:
            dx = enemy.center[0] - player.center[0]
            dy = enemy.center[1] - player.center[1]
            dist = math.hypot(dx,dy)

            took_damage = False
            if dist < enemy.radius + player.radius:
                took_damage = True
                player.hp -= enemy.damage
                print(player.hp)
                cooldown = 30 # 30 frame immunity
    
    # summond boss every 10 kills
    if kill_count % 10 == 0 and kill_count != 0:
        if not boss_summoned:
            spawn_boss(kill_count, enemies)
            boss_summoned = True

    # overlay text
    font.render_to(screen, (20, 20), str(kill_count), 'White')

    if cooldown>0: font.render_to(screen, (20, height-40), 'HP: '+str(int(player.hp)), 'Red')
    else: font.render_to(screen, (20, height-40), 'HP: '+str(int(player.hp)), 'White')

    pygame.display.update()
    clock.tick(60)