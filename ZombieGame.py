import pygame
import random 
pygame.init()


pygame.display.set_caption("first game")
 
screen_width = 500
screen_height = 500
tick_time = 10 #ms
#fonts
font1 = pygame.font.SysFont('comicsans',20)
font2 = pygame.font.SysFont('comicsans',30,True)
#colors
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)
blue = (100,100,240)
white = (255,255,255)
run = True

class Game:
    def __init__(self,number_of_enemies = 5):
        self.tick_time = tick_time
        self.number_of_enemies = number_of_enemies
        self.dimensions = (40,40)
        self.spawn = (100,50)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.win = pygame.display.set_mode((self.screen_width,self.screen_height))
        self.game_reset()
    
    def game_reset(self):
        self.run = True
        self.player = Player(*self.dimensions,*self.spawn)
        self.enemies = [enemy]*self.number_of_enemies
        for i in range(self.number_of_enemies):
            x = random.randint(100,300)
            y = random.randint(100,300)
            self.enemies[i] = enemy(30,30,x,y)
        self.score = 0
        self.projectiles = []

    def drawWin(self):
        txt = font2.render("YOU WIN",1,white)
        self.win.blit(txt,(100,150))
        pygame.display.update()
        pygame.time.delay(3000)

    def end_conditions(self):
        ta = [i.hit for i in self.enemies]
        b = all(ta)
        if b:
            self.run = False

    @staticmethod
    def player_enemy_collide(player,enemy):
        x1,y1 = player.getPos()
        h1,w1 = player.height,player.width
        x2,y2 = enemy.getPos()
        h2,w2 = enemy.height,enemy.width
        if all([x2<x1+w1, x1<x2+w2,y2<y1+h1,y1<y2+h2]):
            return True
        return False

    @staticmethod
    def bullet_collide(bullet,enemy):
        x1,y1 = bullet.getPos()
        r = bullet.radius
        x2,y2 = enemy.getPos()
        h,w =enemy.height,enemy.width
        if all([x2<x1+r, x1-r<x2+w,y2+r<y1,y1-r<y2+h]):
            return True
        return False
    
    def check_collisions(self):
        p = self.projectiles
        e = self.enemies
        for i in p:
            for j in e:
                b = self.bullet_collide(i,j)
                if b:
                    if not j.hit:
                        self.score += 10
                    j.got_hit()
                    self.projectiles.remove(i)
                    i.remover()
                    
        for i in e:
            if self.player.z :
                continue
            b = self.player_enemy_collide(self.player,i)
            if b:
                i.color = yellow 
                if not self.player.hit_cooldown:
                    self.score -= 20
                    i.hit_player()
                    self.player.got_hit()

    def key_press(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
                pygame.quit()

        keys = pygame.key.get_pressed()
        # Handle horizontal movement
        if keys[pygame.K_LEFT]:
            if self.player.x_acc > 0:
                self.player.x_acc -= self.player.vel
            self.player.direction = -1
        if keys[pygame.K_RIGHT]:
            if self.player.x_acc + self.player.width < self.screen_width:
                self.player.x_acc += self.player.vel
            self.player.direction = 1

        # Handle vertical movement
        if keys[pygame.K_DOWN]:
            if self.player.x_acc+self.player.height<self.screen_height:
                self.player.y_acc += self.player.vel
            
        if keys[pygame.K_UP]:
            if self.player.y_acc>0 :
                self.player.y_acc -= self.player.vel
        
        # Handle jumping
        if keys[pygame.K_SPACE]:
            self.player.start_jump()
       
        if keys[pygame.K_a] and self.player.shoot_cooldown == 0:
            bullet  = self.player.shoot()
            self.projectiles.append(bullet)
    
    def frame_updates(self):
        pygame.time.delay(self.tick_time)
        self.player.cooldown()
        self.player.jump()
        if self.enemies:
            for i in self.enemies:
                i.automover()
        if self.projectiles:
            for i in self.projectiles:
                i.increment()
                if not i.inBounds():
                    self.projectiles.remove(i)
                    i.remover()
        self.check_collisions()
        self.end_conditions()

    def redraw(self):
        self.win.fill((0,0,0))
        for i in self.enemies:
            pygame.draw.rect(self.win,i.color,(*i.getPos(),i.width,i.height))
        for i in self.projectiles:
            pygame.draw.circle(self.win,i.color,i.getPos(),i.radius)
        i = self.player
        pygame.draw.rect(self.win,i.color,(*i.getPos(),i.width,i.height))
        txt = font1.render('Score:'+str(self.score),1,white)
        self.win.blit(txt,(400,20))
        pygame.display.update()


class projectiles():
    def __init__(self,x,y,radius,color,facing):
        self.x = x 
        self.y = y 
        self.radius = radius 
        self.color = color 
        self.facing = facing
        self.vel = int(4*tick_time/10)
    
    def increment(self):
        self.x += self.facing * self.vel
        
    def inBounds(self):
        x,y = self.getPos()    
        if x<0 or x>screen_width:
            return False 
        return True

    def remover(self):
        del self

    def getPos(self):
        return self.x,self.y
        

class Player:
    def __init__(self, height, width, x_acc, y_acc):
        self.height = height
        self.width = width
        self.vel = 2*tick_time/10
        self.x_acc = x_acc
        self.y_acc = y_acc
        self.z = 0
        self.isJump = False
        self.jumpCount = int(0.21/tick_time*1000)
        self.jump_i = 0
        self.jump_scale = (0.12/tick_time*1000)**3
        self.direction = 1
        self.shoot_cooldown = 0
        self.hit_cooldown = 0
        self.max_shoot_cooldown = int(1000/tick_time)
        self.max_hit_cooldown = int(2000/tick_time)
        self.color = red

    def getPos(self):
        return int(self.x_acc), int(self.y_acc)
    
    def got_hit(self):
        self.hit_cooldown = self.max_hit_cooldown

    def jump(self):
        if self.isJump:
            self.height += self.jump_i ** 3 / self.jump_scale*2
            self.width += self.jump_i ** 3  / self.jump_scale*2
            self.x_acc -= self.jump_i ** 3 / self.jump_scale
            self.y_acc -= self.jump_i ** 3 / self.jump_scale
            self.jump_i -= 1
            if self.jump_i < -self.jumpCount:
                self.isJump = False
                self.z = 0

    def start_jump(self):
        if not self.isJump:
            self.jump_i = self.jumpCount
            self.isJump = True
            self.z = 1
            
    def cooldown(self):
        if self.shoot_cooldown:
            self.shoot_cooldown -= 1
        if self.hit_cooldown:
            self.hit_cooldown -= 1

    def shoot(self):
        x,y = self.getPos()
        if self.direction>0:
            x += self.width
        y += self.height//2
        p_obj = projectiles(x,y,3,green,self.direction)
        self.shoot_cooldown = self.max_shoot_cooldown
        return p_obj

    def x_teleport(self):
        if self.x_acc > screen_width:
            self.x_acc = -self.width
        if self.x_acc + self.width < 0:
            self.x_acc = screen_width

    def y_teleport(self):
        if self.y_acc > screen_height:
            self.y_acc = -self.height
        if self.y_acc + self.height < 0:
            self.y_acc = screen_height


class enemy(Player):
    def __init__(self,height,width,x_acc,y_acc):
        Player.__init__(self,height,width,x_acc,y_acc)
        self.color = yellow
        self.hit = False
        self.vel = 0.7*tick_time/10
        self.m = random.random()*4-2

    def got_hit(self):
        if not self.hit:
            self.color_switch(blue)
            self.hit  = True 

    def hit_player(self):
        if self.hit:
            self.color_switch(yellow)
            self.hit = False
    
    def automover(self):
        x_v =  random.random() * (self.vel*2)-self.vel
        y_v = random.random() * (self.vel*2)-self.vel
        self.x_acc += self.vel + x_v * 2
        self.y_acc += self.vel*self.m + y_v * 2
        self.y_teleport()
        self.x_teleport()

    def color_switch(self,new_color):
        self.color = new_color



game = Game(10)
while game.run:
    game.key_press()
    game.frame_updates()
    game.redraw()
game.drawWin()

