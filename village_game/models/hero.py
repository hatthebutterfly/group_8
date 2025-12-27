import pygame
import random
import config
from models.villager import Villager

# 1. 速度型 - 艾里奧
class SonicHero(Villager):
    def __init__(self, engine, name):
        super().__init__(engine, name, (50, 255, 50), "Hero") # 亮綠色
        self.speed = 2.5  # 超級快
        
    def update(self):
        super().update()
        # 特效：走路會有殘影 (簡單用畫圓表示)
        if self.engine.frame_count % 10 == 0:
            pygame.draw.circle(self.engine.screen, (200, 255, 200), (int(self.pos.x), int(self.pos.y)), 6, 1)

# 2. 治療型 - 芙蕾雅
class HealerHero(Villager):
    def __init__(self, engine, name):
        super().__init__(engine, name, (255, 100, 255), "Hero") # 粉紫色
        self.speed = 1.0
        
    def update(self):
        super().update()
        # 技能：每 2 秒治療一個受傷的村民
        if self.engine.frame_count % 120 == 0:
            for v in self.engine.villagers:
                if v.is_alive and v != self:
                    # 這裡假設以後有血量系統，目前先降低飢餓度作為治療代替
                    # 或者如果有受傷狀態可以移除
                    if v.hunger > 50:
                        v.hunger -= 20
                        print(f"❤️ {self.name} 治療了 {v.name}")
                        break

# 3. 經濟型 - 摩根
class TycoonHero(Villager):
    def __init__(self, engine, name):
        super().__init__(engine, name, (255, 215, 0), "Hero") # 金色
        self.speed = 0.9
        
    def update(self):
        super().update()
        # 技能：每 3 秒自動產生 1 黃金
        if self.engine.frame_count % 180 == 0:
            self.engine.gold += 1
            # print(f"💰 {self.name} 的投資獲得了回報")

# --- [新增] 4. 防禦型 - 泰坦 ---
class BuilderHero(Villager):
    def __init__(self, engine, name):
        super().__init__(engine, name, (100, 100, 100), "Hero") # 鐵灰色
        self.speed = 0.8 # 比較笨重
        
    def update(self):
        super().update()
        # 技能：每秒自動修牆 +2 HP (免費)
        if self.engine.frame_count % 60 == 0:
            if self.engine.wall_hp < 500: # 設一個修復上限，避免無限刷
                self.engine.wall_hp += 2
                # 視覺特效：頭上冒出修復符號
                # (這裡簡單用 print，實際遊戲中 UI 會更新)
                # print(f"🛡️ {self.name} 加固了城牆")

# --- [新增] 5. 糧食型 - 瑟蕾絲 ---
class OracleHero(Villager):
    def __init__(self, engine, name):
        super().__init__(engine, name, (255, 140, 0), "Hero") # 橘色
        self.speed = 1.0
        
    def update(self):
        super().update()
        # 技能：每 5 秒發動一次「豐收祝福」，全體飢餓度 -5
        if self.engine.frame_count % 300 == 0:
            for v in self.engine.villagers:
                if v.is_alive:
                    v.hunger = max(0, v.hunger - 5)
            self.engine.log_event(f"🌾 {self.name} 施展了豐收祝福！全體抗餓")