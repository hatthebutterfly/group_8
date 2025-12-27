import pygame
import random
import math
import config

class Villager:
    def __init__(self, engine, name, color, role):
        self.engine = engine
        self.name = name
        self.color = color
        self.role = role
        
        self.pos = pygame.math.Vector2(
            random.randint(50, engine.map_width - 50),
            random.randint(50, engine.map_height - 50)
        )
        
        # 職業差異設定
        if self.role == "Hunter":
            self.speed = 1.5   # 獵人跑得快
        else:
            self.speed = 0.8   # 農夫走得慢
            
        self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.speed
        
        self.is_alive = True
        self.hunger = 0

    def update(self):
        if not self.is_alive:
            return

        # --- 1. 基礎生理機制 ---
        self.hunger += config.HUNGER_RATE
        if self.hunger >= 100:
            self.is_alive = False
            print(f"💀 {self.name} 餓死了！")
            return

        if self.hunger > 80 and self.engine.food > 0:
            self.engine.food -= 1
            self.hunger -= config.FOOD_NUTRITION
            if self.hunger < 0: self.hunger = 0

        # --- 2. AI 移動邏輯 (包含求生本能) ---
        
        found_target = False # 用來標記是否正在前往食物
        
        # [新增] 求生本能：如果飢餓 > 50，優先找最近的食物
        if self.hunger > 50:
            nearest_food = None
            min_dist = 99999
            
            # 搜尋所有資源
            for r in self.engine.resources:
                if r.active and getattr(r, 'type', 'Food') == 'Food':
                    # 取得資源座標
                    rx, ry = r.x, r.y
                    # 計算距離
                    dist = self.pos.distance_to(pygame.math.Vector2(rx, ry))
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_food = r
            
            # 如果有找到食物，就往那邊走
            if nearest_food:
                target_vec = pygame.math.Vector2(nearest_food.x, nearest_food.y) - self.pos
                if target_vec.length() > 0: # 避免除以 0
                    self.vel = target_vec.normalize() * self.speed
                    found_target = True

        # 如果不餓，或者地圖上根本沒食物 -> 執行原本的隨機移動
        if not found_target:
            # 隨機轉向 (閒逛)
            if random.random() < 0.005:
                self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.speed

            # 邊界反彈
            if self.pos.x < 0 or self.pos.x > self.engine.map_width:
                self.vel.x *= -1
            if self.pos.y < 0 or self.pos.y > self.engine.map_height:
                self.vel.y *= -1

        # 更新位置
        self.pos += self.vel

        # --- 3. 採集與碰撞判定 ---
        for r in self.engine.resources:
            if r.active:
                target_x, target_y = None, None
                if hasattr(r, 'rect'): target_x, target_y = r.rect.centerx, r.rect.centery
                elif hasattr(r, 'pos'):
                    try: target_x, target_y = r.pos.x, r.pos.y
                    except: pass
                elif hasattr(r, 'x'): target_x, target_y = r.x, r.y

                if target_x is None: continue

                dx = self.pos.x - target_x
                dy = self.pos.y - target_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 30:
                    r.active = False
                    
                    r_type = getattr(r, 'type', 'Food')
                    
                    if r_type == 'Food': 
                        # 農夫特權：食物加倍
                        amount = 1
                        if self.role == "Farmer":
                            amount = 2
                            print(f"🌾 {self.name} 收穫了 {amount} 食物 (飢餓:{int(self.hunger)})")
                        else:
                            print(f"{self.name} 撿到了 1 食物")
                            
                        self.engine.food += amount
                        
                        # [新增] 吃到東西後，如果原本很餓，會稍微降低一點點飢餓度作為獎勵
                        # (模擬現場偷吃一口，讓他不會馬上餓死)
                        if self.hunger > 50:
                            self.hunger -= 5 

                    elif r_type == 'Wood': 
                        self.engine.wood += 1
                        print(f"🌲 {self.name} 收集了木頭")
                    elif r_type == 'Gold': 
                        self.engine.gold += 1
                        print(f"💎 {self.name} 收集了黃金")
                    else: 
                        self.engine.food += 1

    def draw(self, screen):
        x = int(self.pos.x)
        y = int(self.pos.y)

        if not self.is_alive:
            pygame.draw.line(screen, (100, 100, 100), (x-10, y), (x+10, y), 2)
            pygame.draw.line(screen, (100, 100, 100), (x, y-5), (x, y+5), 2)
            screen.blit(self.engine.font.render("R.I.P", True, (150, 150, 150)), (x - 15, y - 30))
            return

        swing = math.sin(self.engine.frame_count * 0.2) * 8
        head_pos = (x, y - 25)
        neck_pos = (x, y - 20)
        hip_pos = (x, y - 10)

        pygame.draw.circle(screen, self.color, head_pos, 5)
        pygame.draw.line(screen, self.color, neck_pos, hip_pos, 2)
        
        # 畫手
        arm_len = 8
        if self.role == "Hunter": arm_len = 10
        
        pygame.draw.line(screen, self.color, (x, y - 18), (x - arm_len, y - 12 + swing), 2)
        pygame.draw.line(screen, self.color, (x, y - 18), (x + arm_len, y - 12 - swing), 2)
        
        pygame.draw.line(screen, self.color, hip_pos, (x - 4 - swing, y), 2)
        pygame.draw.line(screen, self.color, hip_pos, (x + 4 + swing, y), 2)

        tc = (255, 255, 255)
        if self.hunger > 80: tc = (255, 50, 50)
        screen.blit(self.engine.font.render(f"{int(self.hunger)}", True, tc), (x - 10, y - 45))