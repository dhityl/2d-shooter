import pygame, math, sys, random
import numpy as np
import pygame.freetype
from pygame.locals import*


img_hit_marker = pygame.image.load('./resources/hit_marker.png')
img_heart_icon = pygame.image.load('./resources/heart_icon.png')
img_bomb_icon = pygame.image.load('./resources/bomb_icon.png')
img_bomb = pygame.image.load('./resources/bomb.png')

width, height = 1280, 720

pygame.init()
screen = pygame.display.set_mode((width, height))
font_big = pygame.freetype.Font('./resources/Pixeltype.ttf', 100)
font = pygame.freetype.Font('./resources/Pixeltype.ttf', 60)
font_shadow = pygame.freetype.Font('./resources/Pixeltype.ttf', 66)
font_small = pygame.freetype.Font('./resources/Pixeltype.ttf', 30)
pygame.display.set_caption("2D Shooter")
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
        pygame.draw.circle(surface, 'Black', self.center, self.radius+2)
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
        self.speed = speed
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
    for enemy in enemies[:]:
        enemy.chase(player.center)
        enemy.draw()

def get_bomb_pos(player):
    BIrect = pygame.Surface.get_rect(img_bomb)
    return np.subtract(player.center, (BIrect.width, BIrect.height))

def explode_bomb(pos, level, enemies):
    bx,by = pos
    damage_radius = 200
    damage = 50 + 2*level
    for enemy in enemies[:]:
        ex, ey = enemy.center
        dx = abs(ex-bx)
        dy = abs(ey-by)
        dist = math.hypot(dx,dy)
        if dist <= damage_radius:
            enemy.hp -= damage



## MAIN GAME LOOP ##

initialize_var = True
game_over = False
start_game = False
while True:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if not start_game:
                if event.key == pygame.K_RETURN:
                    start_game = True
                    initialize_var = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif game_over:
                if event.key == pygame.K_RETURN:
                        initialize_var = True
                        game_over = False
                if event.key == pygame.K_ESCAPE:
                    start_game = False
                    game_over = False
            else:               
                if event.key == pygame.K_ESCAPE:
                    start_game = False                

    if not start_game:
        screen.fill('Black')
        start_text1 = 'A Simple 2D Shooter'
        t1rect = font_big.get_rect(start_text1)
        start_text2 = 'Just Aim to Shoot'
        start_text3 = 'SHIFT = Move Faster, SPACE = Drop Bomb, ESC = Quit'
        start_text4 = 'Press ENTER to start'
        font_big.render_to(screen, (300, 200), start_text1, 'White')
        font_small.render_to(screen, (300, t1rect.height + 240), start_text2, 'White')
        font_small.render_to(screen, (300, t1rect.height + 340), start_text3, 'White')
        font_small.render_to(screen, (300, t1rect.height + 440), start_text4, 'White')

        if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
            start_game = True


        # level_text = f"Level {level+1}"
        # ltrect = font.get_rect(level_text)
        # font.render_to(screen, (width - ltrect.width - 20, 20), level_text, 'White')

        pygame.display.flip()
        continue

    if game_over:
        screen.fill('Black')
        gorect = font_big.get_rect('GAME OVER')
        rerect = font.get_rect('Press ENTER to restart')
        font_big.render_to(screen, (width/2 - gorect.width/2, 300), 'GAME OVER', 'Red')
        font.render_to(screen, (width/2 - rerect.width/2, 400), 'Press ENTER to restart', 'Red')

        pygame.display.flip()
        continue

    if initialize_var:
        player = Character(color='Green')
        shoot_timer = 0
        shoot_rate = 25 # lower = faster

        bomb_count = 10
        display_bomb = False
        bomb_cooldown = 0
        bomb_delay = 30
        bomb_timer = 0

        enemies = []
        spawn_timer = 0
        spawn_rate = 120 # lower = faster
        kill_count = 0

        cooldown = 30
        boss_summoned=False
        level = 0

        initialize_var = False

    # GAME START

    pygame.mouse.set_cursor(pygame.cursors.diamond)
    screen.fill((50,50,50))


    if level>25: level = 25 # capped level cause bad shoot_rate scaling, TODO: fix ts (cap shoot_rate instead)
    player.damage = 10 + 0.175 * level
    player.draw()

    if keys[pygame.K_LSHIFT]: # faster movement if you press shift
        player.move(speed = 8)
    else:
        player.move(speed = 4)

    shoot_rate = 25 - level
    shoot_timer = handle_bullets(player, shoot_timer, shoot_rate)

    spawn_rate = 120 - level*2
    spawn_timer = handle_enemy_spawn(spawn_timer, spawn_rate, enemies)

    update_enemy(enemies)
    for enemy in enemies[:]:
            if enemy.hp <= 0:
                enemies.remove(enemy)
                kill_count+=1


    # handle collision
    ## bullet vs enemy
    for bullet in player.bullets[:]:
        for enemy in enemies[:]:
            dx = enemy.center[0] - bullet.x
            dy = enemy.center[1] - bullet.y
            dist = math.hypot(dx, dy)
            if dist < enemy.radius + bullet.radius:
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
                    enemy.hp -= player.damage

                    # kill enemy if 0 hp
                    if enemy.check_death():
                        enemies.remove(enemy)
                        kill_count+=1

                        if isinstance(enemy, Boss):
                            level+=1
                            boss_summoned = False
                            player.hp += 10
                            bomb_count+=1

                    # display hit marker
                    hit_marker_pos = np.array(enemy.center) + np.array([0, -20])
                    screen.blit(img_hit_marker, hit_marker_pos)

    ## player vs enemy
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
                cooldown = 30 # 30 frame damage immunity
    

    # summon boss every 10 kills
    if kill_count % 10 == 0 and kill_count != 0:
        spawn_boss(kill_count, enemies)
        kill_count += 1


    # bomb logic
    bomb_cooldown-=1
    if keys[pygame.K_SPACE] and not display_bomb and bomb_cooldown<=0 and bomb_count>0:
        bomb_drop_pos = get_bomb_pos(player)
        bomb_display_pos = bomb_drop_pos[0] +  30,  bomb_drop_pos[1] + 30
        display_bomb = True
        bomb_timer = bomb_delay
        bomb_cooldown = 60
        bomb_count-=1

    if display_bomb:
        screen.blit(img_bomb, (bomb_display_pos))
        bomb_timer -= 1
        if bomb_timer <= 0:
            explode_bomb(bomb_drop_pos, level, enemies)
            display_bomb = False
            bomb_pos = None


    # overlay text
    font.render_to(screen, (20, 20), str(kill_count), 'White')

    level_text = f"Level {level+1}"
    ltrect = font.get_rect(level_text)
    font.render_to(screen, (width - ltrect.width - 20, 20), level_text, 'White')

    hp_icon_pos = (10, height - 45)
    hp_text = str(int(player.hp))
    screen.blit(img_heart_icon, hp_icon_pos)
    if cooldown>0: font.render_to(screen, (60, height-40), hp_text, 'Red')
    else: font.render_to(screen, (60, height-40), hp_text, 'White')

    bomb_text = str(int(bomb_count))
    btrect = font.get_rect(bomb_text)
    birect = pygame.Surface.get_rect(img_bomb_icon)
    bomb_icon_pos = width-birect.width-btrect.width-30, height-birect.height-15
    screen.blit(img_bomb_icon, bomb_icon_pos)
    font.render_to(screen, (width-btrect.width-20,  height-btrect.height-20), bomb_text, 'White')

    if player.hp <=0: game_over = True

    pygame.display.update()
    clock.tick(60)