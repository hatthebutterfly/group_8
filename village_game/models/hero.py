# models/hero.py
import pygame
import random
from models.villager import Villager
from models.resource import Resource

# --- 基礎菁英類別 ---
class HeroVillager(Villager):
    def __init__(self, game_engine, name, color, job_title):
        super().__init__(game_engine, name, color, job_title)
        self.max_health = 150
        self.health = 150
        self.hunger_rate = 0.05 

    def draw(self, surface):
        if not self.is_alive:
            super().draw(surface)
            return
        x, y = int(self.pos.x), int(self.pos.y)
        
        # 光環特效
        if self.game.frame_count % 30 < 15:
            aura = (min(255, self.color[0]+50), min(255, self.color[1]+50), min(255, self.color[2]+50))
            pygame.draw.circle(surface, aura, (x, y), 12, 1)

        pygame.draw.circle(surface, self.color, (x, y), 9)
        # 顯示職業首字
        font_surf = self.game.font.render(self.job[0], True, (255,255,255))
        surface.blit(font_surf, (x-4, y-6))
        # 菁英血條
        pygame.draw.rect(surface, (0, 0, 0), (x-12, y-15, 24, 4))
        pygame.draw.rect(surface, self.color, (x-12, y-15, 24 * (self.health/self.max_health), 4))

# --- 1. 迅捷斥侯 (Sonic) ---
class SonicHero(HeroVillager):
    def __init__(self, game_engine, name):
        super().__init__(game_engine, name, (0, 191, 255), "Sonic") 
        self.speed = 3.5

# --- 2. 聖職者 (Healer) ---
class HealerHero(HeroVillager):
    def __init__(self, game_engine, name):
        super().__init__(game_engine, name, (255, 105, 180), "Healer")
        self.speed = 0.8
        self.heal_cooldown = 0

    def update(self):
        super().update()
        if not self.is_alive: return
        self.heal_cooldown += 1
        if self.heal_cooldown >= 60:
            self.heal_nearby()
            self.heal_cooldown = 0

    def heal_nearby(self):
        for v in self.game.villagers:
            if v.is_alive and v != self and v.health < 90:
                if self.pos.distance_to(v.pos) < 100:
                    v.health += 10
                    pygame.draw.line(self.game.screen, (0, 255, 0), 
                                     (self.pos.x, self.pos.y), (v.pos.x, v.pos.y), 1)

# --- 3. 大富豪 (Tycoon) ---
class TycoonHero(HeroVillager):
    def __init__(self, game_engine, name):
        super().__init__(game_engine, name, (255, 215, 0), "Tycoon")
        self.speed = 1.2
        self.money_timer = 0

    def update(self):
        super().update()
        if not self.is_alive: return
        self.money_timer += 1
        if self.money_timer >= 300: # 5秒一次
            # 隨機生成 1~2 個資源
            for _ in range(random.randint(1,2)):
                 self.game.resources.append(Resource(self.pos.x + random.randint(-20,20), self.pos.y + random.randint(-20,20)))
            self.money_timer = 0 
