import pygame
import random
import config

class Resource:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = pygame.math.Vector2(x, y)
        self.active = True
        
        # --- [關鍵] 隨機決定這顆資源是什麼 ---
        rand_val = random.random()
        
        # 70% 是食物 (綠色)
        if rand_val < 0.7:
            self.type = "Food"
            self.color = config.COLOR_FOOD
            
        # 20% 是木頭 (褐色)
        elif rand_val < 0.9:
            self.type = "Wood"
            self.color = config.COLOR_WOOD
            
        # 10% 是黃金 (金色)
        else:
            self.type = "Gold"
            self.color = config.COLOR_GOLD

    def draw(self, screen):
        if self.active:
            # 根據類型畫不同形狀
            if self.type == "Food":
                # 圓形
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)
                
            elif self.type == "Wood":
                # 方形
                pygame.draw.rect(screen, self.color, (int(self.x)-4, int(self.y)-4, 8, 8))
                
            elif self.type == "Gold":
                # 菱形
                points = [
                    (self.x, self.y - 5),
                    (self.x + 4, self.y),
                    (self.x, self.y + 5),
                    (self.x - 4, self.y)
                ]
                pygame.draw.polygon(screen, self.color, points)