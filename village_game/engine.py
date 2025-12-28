import pygame
import random
import os
import config
from models.resource import Resource
from models.villager import Villager
from models.hero import SonicHero, HealerHero, TycoonHero, BuilderHero, OracleHero
from models.event_system import EventManager
from achievement_system import AchievementManager
from shop_system import Shop

# --- 浮動文字特效類別 ---    
class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 60 # 顯示 1 秒
        self.y_offset = 0

    def update(self):
        self.y_offset -= 0.5 
        self.timer -= 1

    def draw(self, screen, font):
        if self.timer > 0:
            alpha = min(255, self.timer * 5)
            surf = font.render(self.text, True, self.color)
            surf.set_alpha(alpha)
            screen.blit(surf, (self.x - surf.get_width()//2, self.y + self.y_offset - 20))

class GameEngine:
    def __init__(self):
        pygame.init()
        self.map_width = config.INITIAL_MAP_WIDTH
        self.map_height = config.INITIAL_MAP_HEIGHT
        self.screen = pygame.display.set_mode((self.map_width + config.UI_WIDTH, self.map_height))
        
        pygame.display.set_caption("Village Sim: 15 Days Challenge")
        self.clock = pygame.time.Clock()
        
        if os.path.exists(config.FONT_FILE):
            self.font = pygame.font.Font(config.FONT_FILE, 18)
            self.title_font = pygame.font.Font(config.FONT_FILE, 28)
            self.large_font = pygame.font.Font(config.FONT_FILE, 48)
        else:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 60)

        self.assets = {}
        self.load_assets()
        self.reset_game_state()

    def load_assets(self):
        def load_img(filename):
            path = os.path.join(config.IMG_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(img, (32, 32))
                except: return None
            return None

        self.assets['hero'] = load_img(config.IMG_HERO)
        self.assets['villager'] = load_img(config.IMG_VILLAGER)
        self.assets['food'] = load_img(config.IMG_FOOD)
        self.assets['wood'] = load_img(config.IMG_WOOD)
        self.assets['gold'] = load_img(config.IMG_GOLD)
        wall_img = load_img(config.IMG_WALL)
        if wall_img:
            self.assets['wall'] = pygame.transform.scale(wall_img, (32, 32))

    def reset_game_state(self):
        self.villagers = []
        self.resources = []
        self.floating_texts = []
        self.logs = ["歡迎來到荒野...", "按 [ESC] 可隨時退出"]
        self.day = 1
        self.frame_count = 0

        self.in_transition = False
        self.transition_alpha = 0
        self.showing_summary = False
        self.daily_deaths = []
        self.event_warning_timer = 0
        self.night_overlay = pygame.Surface((self.map_width, self.map_height))
        
        self.last_pop_milestone = 5
        self.prosperity = 0
        
        self.food = 50
        self.wood = 0
        self.gold = 0
        self.wall_hp = 100 
        
        self.notification_text = ""
        self.notification_timer = 0
        self.notification_color = (255, 50, 50)
        
        self.event_manager = EventManager(self)
        self.is_paused = False
        
        # 成就系統（只在第一次初始化）
        if not hasattr(self, 'achievement_manager'):
            self.achievement_manager = AchievementManager(self)
        
        # 商店系統（只在第一次初始化）
        if not hasattr(self, 'shop'):
            self.shop = Shop(self)
        
        # 鑽石貨幣（跨遊戲保存）
        if not hasattr(self, 'diamonds'):
            self.diamonds = 0  # 初始鑽石
            self.load_diamonds()  # 讀取保存的鑽石
        
        self.difficulty = "Normal"
        self.spawn_interval = 60 
        self.spawn_timer = 0
        self.is_hell_mode = False
        
        # === 評分系統追蹤 ===
        self.total_deaths = 0              # 總死亡人數
        self.beast_attacks = 0             # 野獸襲擊次數
        self.total_wall_damage = 0         # 累積牆壁傷害
        self.total_resources_collected = 0 # 累積收集資源數
        self.max_population = 5            # 最高人口數
        self.events_completed = 0          # 完成的事件數 

    def apply_difficulty_settings(self, level):
        self.difficulty = level
        if level == "Normal":
            config.HUNGER_RATE = 0.05
            self.spawn_interval = 45 
        elif level == "Hard":
            config.HUNGER_RATE = 0.1 
            self.spawn_interval = 70 
        elif level == "Hell":
            config.HUNGER_RATE = 0.15  
            self.spawn_interval = 100 
            self.is_hell_mode = True
        elif level == "Endless":
            # 無盡模式初始設定（類似Normal）
            config.HUNGER_RATE = 0.05
            self.spawn_interval = 45
            self.is_endless_mode = True
            self.endless_high_score = self.load_endless_high_score()  

    def init_world(self, hero_choice):
        self.villagers = [] 
        for i in range(5):
            self.villagers.append(Villager(self, f"村民{i}", (100, 100, 255), "Farmer"))
            
        hero = None
        if hero_choice == 1: hero = SonicHero(self, "艾里奧")
        elif hero_choice == 2: hero = TycoonHero(self, "摩根")
        elif hero_choice == 3: hero = HealerHero(self, "芙蕾雅")
        elif hero_choice == 4: hero = BuilderHero(self, "泰坦")
        elif hero_choice == 5: hero = OracleHero(self, "瑟蕾絲")
            
        if hero:
            hero.pos.x = self.map_width // 2
            hero.pos.y = self.map_height // 2
            self.villagers.append(hero)

        self.spawn_resources(15)

    def spawn_resources(self, count):
        for _ in range(count):
            x = random.randint(20, self.map_width - 20)
            y = random.randint(20, self.map_height - 20)
            self.resources.append(Resource(x, y))

    def add_floating_text(self, pos, text, color):
        offset_x = random.randint(-10, 10)
        self.floating_texts.append(FloatingText(pos.x + offset_x, pos.y, text, color))

    def log_event(self, text):
        self.logs.insert(0, f"[Day {self.day}] {text}")
        if len(self.logs) > 15: self.logs.pop()

    def show_notification(self, text, color=(255, 50, 50)):
        self.notification_text = text
        self.notification_color = color
        self.notification_timer = 180
    
    def show_achievement_notification(self, achievement):
        """顯示成就解鎖通知"""
        rarity_colors = {
            "common": (200, 200, 200),
            "rare": (100, 150, 255),
            "epic": (200, 100, 255),
            "legendary": (255, 215, 0)
        }
        color = rarity_colors.get(achievement.rarity, (255, 255, 255))
        self.show_notification(f"🏆 成就解鎖: {achievement.name}", color)

    def process_night_phase(self):
        self.daily_deaths = []
        growth = int((self.day ** 2) * 0.8)
        base_dmg = 20 + (self.day * 5) + growth
        attack_damage = random.randint(base_dmg, base_dmg + 30)
        
        if self.difficulty == "Hard": attack_damage = int(attack_damage * 1.3)
        if self.difficulty == "Hell": attack_damage = int(attack_damage * 1.5)
        
        # 無盡模式：難度隨天數增加
        if self.difficulty == "Endless":
            # 每5天提升一次難度
            if self.day <= 15:
                attack_damage = int(attack_damage * 1.0)  # 前15天正常
            elif self.day <= 30:
                attack_damage = int(attack_damage * 1.2)  # 16-30天 +20%
            elif self.day <= 50:
                attack_damage = int(attack_damage * 1.5)  # 31-50天 +50%
            elif self.day <= 75:
                attack_damage = int(attack_damage * 2.0)  # 51-75天 +100%
            else:
                attack_damage = int(attack_damage * 3.0)  # 75天+ 極限難度
            
            # 動態調整飢餓速度
            if self.day > 15:
                config.HUNGER_RATE = min(0.15, 0.05 + (self.day - 15) * 0.002)
            
            # 動態調整資源生成
            if self.day > 20:
                self.spawn_interval = min(120, 45 + (self.day - 20) * 2)

        # 記錄野獸襲擊
        self.beast_attacks += 1

        if self.wall_hp > 0:
            actual_dmg = min(self.wall_hp, attack_damage)
            self.wall_hp -= actual_dmg
            self.total_wall_damage += actual_dmg  # 追蹤累積傷害
            self.log_event(f"夜襲！牆壁受損 -{actual_dmg}")
            if self.wall_hp == 0: self.show_notification("牆壁被摧毀！", (255, 0, 0))
        else:
            living = [v for v in self.villagers if v.is_alive]
            if len(living) > 0:
                if random.random() < 0.6:
                    victim = random.choice(living)
                    victim.is_alive = False
                    self.total_deaths += 1  # 追蹤死亡
                    reason = "被野獸咬死"
                    self.log_event(f"慘劇：{victim.name} {reason}！")
                    self.daily_deaths.append(f"{victim.name} ({reason})")
                    if self.is_hell_mode:
                        self.log_event("地獄模式：一人死亡，全體陣亡！")
                        for v in self.villagers: 
                            if v.is_alive:
                                v.is_alive = False
                                self.total_deaths += 1  # 追蹤所有死亡
                        self.showing_summary = True
                        return 
            else:
                self.log_event("奇蹟！野獸沒發現我們")

        living = [v for v in self.villagers if v.is_alive]
        food_needed = 5
        oracle = next((v for v in living if v.role == "Hero" and isinstance(v, OracleHero)), None)
        if oracle: food_needed = 3

        for v in living:
            if self.food >= food_needed:
                self.food -= food_needed
            else:
                death_chance = 0.5 if self.difficulty == "Hard" else 0.3
                if random.random() < death_chance:
                    v.is_alive = False
                    reason = "飢荒餓死"
                    self.log_event(f"{v.name} {reason}...")
                    self.daily_deaths.append(f"{v.name} ({reason})")
                    if self.is_hell_mode:
                        for vil in self.villagers: vil.is_alive = False
                        self.showing_summary = True    
                        return

        self.showing_summary = True

    def get_repair_cost(self):
        return 10 + (self.day * 5)

    def update(self):
        if self.is_paused or self.showing_summary: return
        
        if self.in_transition:
            if self.transition_alpha > 0: self.transition_alpha -= 5
            else: self.in_transition = False
            return

        if self.event_warning_timer > 0:
            self.event_warning_timer -= 1
            if self.event_warning_timer == 0: self.is_paused = True
            return

        self.frame_count += 1
        if self.notification_timer > 0: self.notification_timer -= 1
        
        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_interval:
            self.spawn_resources(1)
            self.spawn_timer = 0
            if self.prosperity > 50 and random.random() < 0.3:
                self.spawn_resources(1)

        for ft in self.floating_texts: ft.update()
        self.floating_texts = [ft for ft in self.floating_texts if ft.timer > 0]

        if self.frame_count >= config.DAY_LENGTH:
            self.process_night_phase()
            return 

        if self.frame_count % 60 == 0:
            pop = sum(1 for v in self.villagers if v.is_alive)
            self.prosperity += pop * 0.2

        if self.event_manager.check_trigger():
            self.event_warning_timer = 60
            return

        for v in self.villagers: v.update()
        
        # 檢查成就（每半秒一次）
        if self.frame_count % 30 == 0:
            self.achievement_manager.check_achievements()
        
        hero = next((v for v in self.villagers if v.role == "Hero"), None)
        if hero and hero.is_alive:
            for r in self.resources:
                if r.active and hero.pos.distance_to(r.pos) < 30:
                    r.active = False
                    if r.type == "Food": 
                        self.food += 5
                        self.add_floating_text(hero.pos, "+5 Food", config.COLOR_FOOD)
                    elif r.type == "Wood": 
                        self.wood += 5
                        self.add_floating_text(hero.pos, "+5 Wood", config.COLOR_WOOD)
                    elif r.type == "Gold": 
                        self.gold += 5
                        self.add_floating_text(hero.pos, "+5 Gold", config.COLOR_GOLD)

        self.resources = [r for r in self.resources if r.active]

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Tab 鍵打開商店（非結算時）
                if event.key == pygame.K_TAB and not self.showing_summary:
                    self.is_paused = True
                    if not self.shop.show_shop_screen(self.screen, self.font, self.title_font):
                        return False
                    self.is_paused = False

            if self.showing_summary:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        cost = self.get_repair_cost()
                        if self.wood >= cost:
                            self.wood -= cost
                            self.wall_hp += 150
                            print(f"修復成功 -{cost} Wood")
                    
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if not any(v.is_alive for v in self.villagers): pass
                        self.showing_summary = False
                        self.day += 1
                        self.frame_count = 0
                        self.in_transition = True
                        self.transition_alpha = 255
                        
                        # --- [修改重點] 隨機重分配村民位置 ---
                        # 讓他們新的一天從不同地方醒來，避免全部疊在營火
                        for v in self.villagers:
                            if v.is_alive and v.role != "Hero":
                                v.pos.x = random.randint(50, self.map_width - 50)
                                v.pos.y = random.randint(50, self.map_height - 50)
                                # 重置他們的尋路方向，避免還記著昨晚的營火    
                                v.dir = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()

                        if self.day % 5 == 0 and self.day < 15:
                            self.event_manager.trigger_special_shop()
                            self.event_warning_timer = 60

                        pop = sum(1 for v in self.villagers if v.is_alive)
                        if pop > self.last_pop_milestone:
                            self.log_event("人口增長！")
                            self.spawn_resources(10) 
                            self.last_pop_milestone += 3
                return True

            if self.is_paused:
                if event.type == pygame.KEYDOWN:
                    if self.event_manager.handle_input(event.key): self.is_paused = False    
                continue
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mx < self.map_width: self.resources.append(Resource(mx, my))
        return True

    def draw_text_centered(self, surface, text, font, color, center_x, center_y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(center_x, center_y))    
        surface.blit(surf, rect)

    def draw_text_with_shadow(self, surface, text, font, color, x, y):
        shadow = font.render(text, True, (0, 0, 0))
        surface.blit(shadow, (x+1, y+1))
        main = font.render(text, True, color)    
        surface.blit(main, (x, y))

    def draw_panel(self, rect, color, border_color):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((*color, 230))
        self.screen.blit(s, (rect.x, rect.y))
        pygame.draw.rect(self.screen, border_color, rect, 2)
    
    def draw_campfire(self):
        cx, cy = self.map_width // 2, self.map_height // 2
        radius = 40 + int(random.random() * 5)
        glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 150, 50, 50), (radius, radius), radius)
        pygame.draw.circle(glow_surf, (255, 100, 0, 80), (radius, radius), radius - 10)    
        pygame.draw.circle(glow_surf, (255, 50, 0, 150), (radius, radius), radius - 20)
        self.screen.blit(glow_surf, (cx - radius, cy - radius))
        pygame.draw.rect(self.screen, (100, 50, 20), (cx-10, cy-5, 20, 6))
        pygame.draw.rect(self.screen, (100, 50, 20), (cx-10, cy+2, 20, 6))
        pygame.draw.rect(self.screen, (100, 50, 20), (cx-5, cy-10, 6, 20))

    def draw_night_overlay(self):
        progress = self.frame_count / config.DAY_LENGTH
        if progress < 0.6: return
        alpha = 0
        color = (0, 0, 50)
        if progress < 0.8:
            factor = (progress - 0.6) / 0.2
            alpha = int(factor * 100)
            color = (50, 20, 0)
        else:
            factor = (progress - 0.8) / 0.2
            alpha = 100 + int(factor * 100)
            color = (0, 0, 40)
        self.night_overlay.fill(color)  
        self.night_overlay.set_alpha(alpha)
        self.screen.blit(self.night_overlay, (0, 0))

    def draw_summary_screen(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(220)
        self.screen.blit(overlay, (0, 0))
        
        cx, cy = self.screen.get_width() // 2, self.screen.get_height() // 2
        w, h = 600, 550
        
        pygame.draw.rect(self.screen, (30, 30, 40), (cx - w//2, cy - h//2, w, h), 0, 10)
        pygame.draw.rect(self.screen, (100, 100, 120), (cx - w//2, cy - h//2, w, h), 3, 10)
        
        self.draw_text_centered(self.screen, f"Day {self.day} Summary", self.large_font, (255, 215, 0), cx, cy - h//2 + 50)
        
        res_y = cy - h//2 + 110
        self.draw_text_centered(self.screen, f"Food: {int(self.food)}", self.title_font, config.COLOR_FOOD, cx - 150, res_y)
        self.draw_text_centered(self.screen, f"Wood: {int(self.wood)}", self.title_font, config.COLOR_WOOD, cx, res_y)
        self.draw_text_centered(self.screen, f"Gold: {int(self.gold)}", self.title_font, config.COLOR_GOLD, cx + 150, res_y)

        wall_y = res_y + 60
        wall_color = (100, 255, 100) if self.wall_hp > 200 else (255, 50, 50)
        self.draw_text_centered(self.screen, f"Wall Integrity: {self.wall_hp}", self.title_font, wall_color, cx, wall_y)

        death_y = wall_y + 60
        pygame.draw.line(self.screen, (80, 80, 80), (cx-200, death_y-20), (cx+200, death_y-20), 1)
        self.draw_text_centered(self.screen, "傷亡報告", self.font, (200, 200, 200), cx, death_y)
        
        if not self.daily_deaths:
            self.draw_text_centered(self.screen, "今日平安無事", self.font, (100, 255, 100), cx, death_y + 30)
        else:
            for i, d in enumerate(self.daily_deaths[:3]):
                self.draw_text_centered(self.screen, d, self.font, (255, 80, 80), cx, death_y + 30 + i*25)
            if len(self.daily_deaths) > 3:
                 self.draw_text_centered(self.screen, f"...還有 {len(self.daily_deaths)-3} 人", self.font, (200, 200, 200), cx, death_y + 105)

        repair_y = cy + 120
        repair_cost = self.get_repair_cost()     
        can_afford = self.wood >= repair_cost
        repair_color = (100, 255, 255) if can_afford else (100, 100, 100)
        repair_txt = f"[R] 修復城牆 (+150 HP) - 消耗 {repair_cost} 木頭"
        
        pygame.draw.rect(self.screen, (40, 40, 50), (cx - 250, repair_y - 15, 500, 40), 0, 5)
        if can_afford:
             pygame.draw.rect(self.screen, (0, 200, 200), (cx - 250, repair_y - 15, 500, 40), 2, 5)
        
        self.draw_text_centered(self.screen, repair_txt, self.font, repair_color, cx, repair_y + 5)
        if not can_afford:
             self.draw_text_centered(self.screen, "(木頭不足)", self.font, (255, 50, 50), cx, repair_y + 35)

        hint_y = cy + h//2 - 40
        hint = self.font.render("按 [SPACE] 或 [ENTER] 開始新的一天", True, (255, 255, 255))
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            self.screen.blit(hint, hint.get_rect(center=(cx, hint_y)))

    def draw_ui(self):
        ui_x = self.map_width
        self.draw_panel(pygame.Rect(ui_x, 0, config.UI_WIDTH, self.map_height), config.COLOR_UI_BG, config.COLOR_UI_BORDER)
        padding = 20
        start_x = ui_x + padding
        icon_y = 30
        res_bg_h = 40
        gap = 50
        resources = [("food", self.food, config.COLOR_FOOD, "Food"), ("wood", self.wood, config.COLOR_WOOD, "Wood"), ("gold", self.gold, config.COLOR_GOLD, "Gold")]
        for i, (key, val, col, label) in enumerate(resources):
            y = icon_y + i * gap
            pygame.draw.rect(self.screen, (30, 30, 35), (start_x, y, config.UI_WIDTH - padding*2, res_bg_h), 0, 5)
            pygame.draw.rect(self.screen, (60, 60, 65), (start_x, y, config.UI_WIDTH - padding*2, res_bg_h), 1, 5)
            img = self.assets.get(key)
            if img: self.screen.blit(img, (start_x + 5, y + 4))
            else: pygame.draw.circle(self.screen, col, (start_x + 20, y + 20), 8)
            self.draw_text_with_shadow(self.screen, f"{int(val)}", self.title_font, config.COLOR_TEXT, start_x + 50, y + 8)

        status_y = 200
        wall_pct = min(1.0, self.wall_hp / 1000)
        wall_color = (100, 200, 255) if self.wall_hp > 200 else (255, 80, 80)
        self.draw_text_with_shadow(self.screen, f"Wall HP: {self.wall_hp}", self.font, wall_color, start_x, status_y)
        pygame.draw.rect(self.screen, (20, 20, 20), (start_x, status_y + 25, 200, 8))
        pygame.draw.rect(self.screen, wall_color, (start_x, status_y + 25, 200 * wall_pct, 8))
        
        day_y = status_y + 50
        if self.difficulty == "Endless":
            # 無盡模式顯示當前難度階段
            if self.day <= 15:
                stage = "階段1: 正常"
                stage_color = (100, 255, 100)
            elif self.day <= 30:
                stage = "階段2: 困難"
                stage_color = (255, 165, 0)
            elif self.day <= 50:
                stage = "階段3: 地獄"
                stage_color = (255, 100, 100)
            elif self.day <= 75:
                stage = "階段4: 煉獄"
                stage_color = (200, 50, 50)
            else:
                stage = "階段5: 極限"
                stage_color = (138, 43, 226)
            
            self.draw_text_with_shadow(self.screen, f"Day: {self.day}", self.title_font, (255, 255, 200), start_x, day_y)
            self.draw_text_with_shadow(self.screen, stage, self.font, stage_color, start_x, day_y + 30)
        else:
            self.draw_text_with_shadow(self.screen, f"Day: {self.day} / 15", self.title_font, (255, 255, 200), start_x, day_y)
        
        time_pct = self.frame_count / config.DAY_LENGTH
        pygame.draw.rect(self.screen, (20, 20, 20), (start_x, day_y + 55, 200, 6))
        bar_color = (255, 255, 100)
        if time_pct > 0.7: bar_color = (150, 100, 255)
        pygame.draw.rect(self.screen, bar_color, (start_x, day_y + 55, 200 * time_pct, 6))
        
        log_bg_y = self.map_height - 250
        log_h = 230
        self.draw_text_with_shadow(self.screen, "Activity Log", self.font, (180, 180, 180), start_x, log_bg_y - 25)
        pygame.draw.rect(self.screen, (25, 25, 30), (start_x, log_bg_y, config.UI_WIDTH - padding*2, log_h), 0, 5)
        pygame.draw.rect(self.screen, (50, 50, 60), (start_x, log_bg_y, config.UI_WIDTH - padding*2, log_h), 1, 5)
        
        log_y = log_bg_y + 10
        for l in self.logs[:10]:
            self.screen.blit(self.font.render(l, True, (200, 200, 200)), (start_x + 8, log_y))
            log_y += 20

    def draw(self):
        # 根據購買的地圖主題改變顏色
        theme = self.shop_items_owned.get('map_theme', 'default')
        theme_colors = {
            'default': config.COLOR_MAP,
            'desert': (255, 215, 100),
            'snow': (240, 248, 255),
            'forest': (34, 100, 34),
            'lava': (200, 50, 50)
        }
        map_color = theme_colors.get(theme, config.COLOR_MAP)
        
        self.screen.fill(map_color)
        pygame.draw.rect(self.screen, (20, 60, 20), (0,0,self.map_width, self.map_height), 10)
        
        self.draw_campfire()
        
        if self.wall_hp > 0:
            wall_rects = [(0, 0, self.map_width, 20), (0, self.map_height-20, self.map_width, 20), (0, 0, 20, self.map_height), (self.map_width-20, 0, 20, self.map_height)]
            for r in wall_rects:
                if self.assets.get('wall'):
                    for x in range(r[0], r[0]+r[2], 32):
                        for y in range(r[1], r[1]+r[3], 32):
                            self.screen.blit(self.assets['wall'], (x, y))
                else: pygame.draw.rect(self.screen, (100, 100, 100), r)
        for r in self.resources: r.draw_with_assets(self.screen, self.assets)
        for v in self.villagers: v.draw(self.screen)
        
        for ft in self.floating_texts: ft.draw(self.screen, self.font)
            
        self.draw_night_overlay()
        if self.event_warning_timer > 0:
            if (self.event_warning_timer // 10) % 2 == 0:
                hero = next((v for v in self.villagers if v.role == "Hero"), None)
                warn_pos = (hero.pos.x, hero.pos.y - 60) if hero else (self.map_width//2, self.map_height//2)
                txt = self.large_font.render("!", True, (255, 50, 50))
                pygame.draw.circle(self.screen, (255, 255, 0, 100), (int(warn_pos[0]+10), int(warn_pos[1]+20)), 25)
                self.screen.blit(txt, warn_pos)
        if self.in_transition and self.transition_alpha > 0:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.fill((0, 0, 0))    
            overlay.set_alpha(self.transition_alpha)
            self.screen.blit(overlay, (0, 0))
            if self.transition_alpha > 100:
                self.draw_text_centered(self.screen, f"DAY {self.day}", self.large_font, (255, 255, 255), self.screen.get_width()//2, self.screen.get_height()//2)
        if self.showing_summary:
            self.draw_summary_screen()
        elif self.is_paused: self.event_manager.draw(self.screen)
        else: 
            self.draw_ui()
            if self.notification_timer > 0:
                self.draw_text_centered(self.screen, self.notification_text, self.large_font, self.notification_color, self.map_width//2, self.map_height//2 - 100)
        pygame.display.flip()

    def game_over_screen(self):
        # 無盡模式顯示特殊評分畫面
        if self.difficulty == "Endless":
            self.show_endless_score_screen()
        else:
            # 一般模式顯示評分畫面
            self.show_score_screen(victory=False)
        
        while True:
            self.screen.fill((0, 0, 0))
            cx, cy = (self.map_width + config.UI_WIDTH) // 2, self.map_height // 2
            
            if self.difficulty == "Endless":
                t = self.large_font.render("無盡模式結束", True, (138, 43, 226))
                self.screen.blit(t, (cx - t.get_width()//2, cy - 100))
                
                sub = self.title_font.render(f"你存活了 {self.day} 天！", True, (255, 215, 0))
                self.screen.blit(sub, (cx - sub.get_width()//2, cy - 30))
                
                # 顯示最高紀錄
                if self.day > self.endless_high_score:
                    record_text = self.title_font.render("🏆 新紀錄！", True, (255, 215, 0))
                    self.screen.blit(record_text, (cx - record_text.get_width()//2, cy + 20))
                else:
                    record_text = self.font.render(f"最高紀錄: {self.endless_high_score} 天", True, (200, 200, 200))
                    self.screen.blit(record_text, (cx - record_text.get_width()//2, cy + 20))
            else:
                t = self.large_font.render("GAME OVER", True, (255, 0, 0))
                self.screen.blit(t, (cx - t.get_width()//2, cy - 80))
                
                sub = self.title_font.render(f"你存活了 {self.day} 天", True, (200, 200, 200))
                self.screen.blit(sub, (cx - sub.get_width()//2, cy))
            
            hint = self.font.render("按 [R] 重新開始  /  按 [ESC] 離開", True, (150, 150, 150))
            self.screen.blit(hint, (cx - hint.get_width()//2, cy + 80))
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return False 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: return True 
                    if event.key == pygame.K_ESCAPE: return False 

    def game_won_screen(self):
        # 先顯示評分畫面
        self.show_score_screen(victory=True)
        
        while True:
            self.screen.fill((50, 50, 0))
            cx, cy = (self.map_width + config.UI_WIDTH) // 2, self.map_height // 2
            
            t = self.large_font.render("VICTORY!", True, (255, 215, 0))
            self.screen.blit(t, (cx - t.get_width()//2, cy - 80))
            
            sub = self.title_font.render("恭喜！你成功存活了 15 天！", True, (255, 255, 255))
            self.screen.blit(sub, (cx - sub.get_width()//2, cy))
            
            hint = self.font.render("按 [R] 重新開始  /  按 [ESC] 離開", True, (200, 200, 200))
            self.screen.blit(hint, (cx - hint.get_width()//2, cy + 80))
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: return True
                    if event.key == pygame.K_ESCAPE: return False

    def start_screen(self):    
        waiting = True
        while waiting:
            self.screen.fill((20, 20, 30))
            cx = (self.map_width + config.UI_WIDTH) // 2
            title = self.large_font.render("Village Sim: 15 Days Challenge", True, (255, 215, 0))
            self.screen.blit(title, (cx - title.get_width()//2, 100))
            instructions = ["【生存挑戰】目標：活到第 15 天", "-----------------------------", "1. 資源管理：綠色=糧食，褐色=木材，金色=貨幣。", "2. 英雄操控：WASD/方向鍵 移動，靠近資源自動撿取。", "3. 夜晚威脅：野獸會攻擊牆壁，無牆壁則咬死村民。", "4. 每日結算：檢視傷亡與消耗資源。", "-----------------------------", "按 [空白鍵] 開始遊戲  |  按 [A] 成就  |  按 [S] 商店"]
            y = 200
            for line in instructions:
                text = self.font.render(line, True, (200, 200, 200))
                self.screen.blit(text, (cx - text.get_width()//2, y))
                y += 40
            
            # 成就解鎖率顯示
            unlocked, total, rate = self.achievement_manager.get_unlock_rate()
            ach_text = self.font.render(f"🏆 成就解鎖: {unlocked}/{total} ({rate:.1f}%)", True, (255, 215, 0))
            self.screen.blit(ach_text, (cx - ach_text.get_width()//2, y + 20))
            
            # 鑽石餘額顯示
            diamond_text = self.font.render(f"💎 鑽石: {self.diamonds}", True, (100, 200, 255))
            self.screen.blit(diamond_text, (cx - diamond_text.get_width()//2, y + 50))
            
            pygame.display.flip()    
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return False
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_ESCAPE: return False
                    elif event.key == pygame.K_a:
                        # 打開成就畫面
                        if not self.achievement_screen():
                            return False
                    elif event.key == pygame.K_s:
                        # 打開商店畫面
                        if not self.shop.show_shop_screen(self.screen, self.font, self.title_font):
                            return False
                    elif event.key == pygame.K_SPACE:
                        waiting = False
        return True

    def hero_selection_screen(self):
        selected_hero = None
        while selected_hero is None:
            self.screen.fill((15, 15, 25))
            cx = (self.map_width + config.UI_WIDTH) // 2
            title = self.title_font.render("STEP 1: 選擇你的英雄", True, (255, 255, 255))
            self.screen.blit(title, (cx - title.get_width()//2, 40))
            options = [
                {"key": "[1]", "color": (100, 255, 100), "name": "艾里奧 (Speed)", "desc": "移動速度極快，適合快速掃蕩地圖資源。"},
                {"key": "[2]", "color": (255, 215, 0), "name": "摩根 (Tycoon)", "desc": "被動產出黃金，適合購買黑市與商人道具。"},
                {"key": "[3]", "color": (255, 100, 255), "name": "芙蕾雅 (Healer)", "desc": "自動治療飢餓與受傷的村民。"},
                {"key": "[4]", "color": (150, 150, 150), "name": "泰坦 (Builder)", "desc": "自動修復受損的城牆，防禦流首選。"},
                {"key": "[5]", "color": (255, 140, 0), "name": "瑟蕾絲 (Oracle)", "desc": "施展豐收祝福，大幅降低全體飢餓度。"}
            ]
            y = 100
            for opt in options:
                rect_w = 700    
                rect_h = 85
                rect_x = cx - rect_w // 2
                pygame.draw.rect(self.screen, (30, 30, 40), (rect_x, y, rect_w, rect_h))
                pygame.draw.rect(self.screen, opt["color"], (rect_x, y, rect_w, rect_h), 2)
                key_txt = self.large_font.render(opt["key"], True, opt["color"])
                self.screen.blit(key_txt, (rect_x + 20, y + 20))
                name_txt = self.title_font.render(opt["name"], True, (255, 255, 255))
                self.screen.blit(name_txt, (rect_x + 100, y + 10))
                desc_txt = self.font.render(opt["desc"], True, (200, 200, 200))
                self.screen.blit(desc_txt, (rect_x + 100, y + 50))
                y += 100    
            hint = self.font.render("按鍵盤 [1] ~ [5] 選擇", True, (150, 150, 150))
            self.screen.blit(hint, (cx - hint.get_width()//2, 620))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return None
                    if event.key == pygame.K_1: selected_hero = 1
                    if event.key == pygame.K_2: selected_hero = 2
                    if event.key == pygame.K_3: selected_hero = 3
                    if event.key == pygame.K_4: selected_hero = 4
                    if event.key == pygame.K_5: selected_hero = 5
        return selected_hero

    def calculate_score(self, victory=False):
        """計算最終評分"""
        score = 0
        breakdown = {}
        
        # 1. 存活天數評分 (0-300分)
        survival_score = min(300, self.day * 20)
        if victory:  # 勝利額外獎勵
            survival_score = 300
        breakdown['存活天數'] = (survival_score, f"{self.day} 天")
        score += survival_score
        
        # 2. 資源評分 (0-200分)
        total_resources = self.food + self.wood + self.gold * 5  # 黃金價值更高
        resource_score = min(200, total_resources // 2)
        breakdown['資源儲備'] = (resource_score, f"糧{self.food} 木{self.wood} 金{self.gold}")
        score += resource_score
        
        # 3. 人口存活評分 (0-150分)
        living_count = len([v for v in self.villagers if v.is_alive])
        population_score = living_count * 25
        breakdown['倖存人口'] = (population_score, f"{living_count} 人")
        score += population_score
        
        # 4. 死亡懲罰 (-10分/人)
        death_penalty = self.total_deaths * -10
        breakdown['死亡懲罰'] = (death_penalty, f"{self.total_deaths} 人犧牲")
        score += death_penalty
        
        # 5. 防禦評分 (0-100分)
        defense_score = min(100, self.wall_hp // 5)
        breakdown['城牆防禦'] = (defense_score, f"{self.wall_hp} HP")
        score += defense_score
        
        # 6. 野獸襲擊應對 (-5分/次攻擊，但總傷害低則減免)
        if self.total_wall_damage < 500:  # 防禦成功
            beast_score = max(-50, -self.beast_attacks * 2)
        else:
            beast_score = max(-100, -self.beast_attacks * 5)
        breakdown['野獸應對'] = (beast_score, f"受襲 {self.beast_attacks} 次")
        score += beast_score
        
        # 7. 事件參與獎勵 (5分/事件)
        event_score = self.events_completed * 5
        breakdown['事件參與'] = (event_score, f"{self.events_completed} 個")
        score += event_score
        
        # 8. 難度加成
        difficulty_mult = 1.0
        if self.difficulty == "Hard":
            difficulty_mult = 1.5
        elif self.difficulty == "Hell":
            difficulty_mult = 2.0
        
        final_score = int(score * difficulty_mult)
        
        # 9. 勝利獎勵
        if victory:
            final_score += 500
            breakdown['勝利獎勵'] = (500, "完成挑戰")
        
        return final_score, breakdown, difficulty_mult
    
    def get_rank(self, score):
        """根據分數返回評級"""
        if score >= 2000:
            return "S", (255, 215, 0), "傳奇村長"
        elif score >= 1500:
            return "A", (100, 255, 100), "卓越領袖"
        elif score >= 1000:
            return "B", (100, 200, 255), "稱職村長"
        elif score >= 600:
            return "C", (255, 165, 0), "努力生存"
        elif score >= 300:
            return "D", (200, 200, 200), "勉強及格"
        else:
            return "F", (255, 100, 100), "慘不忍睹"
    
    def calculate_diamond_reward(self, rank, score, victory):
        """根據評級計算鑽石獎勵"""
        # 基礎獎勵（根據評級）
        rank_rewards = {
            "S": 50,   # 傳說級
            "A": 30,   # 優秀
            "B": 20,   # 良好
            "C": 10,   # 及格
            "D": 5,    # 勉強
            "F": 2     # 安慰獎
        }
        base_reward = rank_rewards.get(rank, 0)
        
        # 勝利獎勵
        victory_bonus = 10 if victory else 0
        
        # 難度獎勵
        difficulty_bonus = 0
        if self.difficulty == "Hard":
            difficulty_bonus = 5
        elif self.difficulty == "Hell":
            difficulty_bonus = 15
        
        # 完美通關額外獎勵
        perfect_bonus = 0
        if victory and self.total_deaths == 0:
            perfect_bonus = 20  # 零死亡額外獎勵
        
        total_reward = base_reward + victory_bonus + difficulty_bonus + perfect_bonus
        return total_reward
    
    def save_diamonds(self):
        """保存鑽石到文件"""
        import json
        try:
            with open("player_data.json", 'w', encoding='utf-8') as f:
                json.dump({"diamonds": self.diamonds}, f)
        except Exception as e:
            print(f"保存鑽石失敗: {e}")
    
    def load_diamonds(self):
        """讀取鑽石"""
        import json
        import os
        if os.path.exists("player_data.json"):
            try:
                with open("player_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.diamonds = data.get("diamonds", 0)
            except Exception as e:
                print(f"讀取鑽石失敗: {e}")
                self.diamonds = 0
    
    def load_endless_high_score(self):
        """讀取無盡模式最高紀錄"""
        import json
        import os
        if os.path.exists("endless_records.json"):
            try:
                with open("endless_records.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except Exception as e:
                print(f"讀取無盡紀錄失敗: {e}")
        return 0
    
    def save_endless_high_score(self, days):
        """保存無盡模式最高紀錄"""
        import json
        if days > self.endless_high_score:
            self.endless_high_score = days
            try:
                with open("endless_records.json", 'w', encoding='utf-8') as f:
                    json.dump({"high_score": days}, f)
            except Exception as e:
                print(f"保存無盡紀錄失敗: {e}")
    
    def calculate_endless_score(self):
        """計算無盡模式評分"""
        score_breakdown = {}
        total_score = 0
        
        # 1. 存活天數（主要分數）每天20分
        survival_score = self.day * 20
        score_breakdown['存活天數'] = (survival_score, f"{self.day} 天")
        total_score += survival_score
        
        # 2. 人口獎勵（每人10分）
        living_count = len([v for v in self.villagers if v.is_alive])
        population_score = living_count * 10
        score_breakdown['倖存人口'] = (population_score, f"{living_count} 人")
        total_score += population_score
        
        # 3. 資源獎勵
        resource_score = (self.food + self.wood + self.gold * 5) // 3
        score_breakdown['資源儲備'] = (resource_score, f"糧{self.food}木{self.wood}金{self.gold}")
        total_score += resource_score
        
        # 4. 城牆獎勵
        wall_score = self.wall_hp // 10
        score_breakdown['城牆防禦'] = (wall_score, f"{self.wall_hp} HP")
        total_score += wall_score
        
        # 5. 死亡懲罰
        death_penalty = -self.total_deaths * 5
        score_breakdown['死亡懲罰'] = (death_penalty, f"{self.total_deaths} 人")
        total_score += death_penalty
        
        # 6. 里程碑獎勵
        milestone_bonus = 0
        if self.day >= 20: milestone_bonus += 100
        if self.day >= 30: milestone_bonus += 200
        if self.day >= 50: milestone_bonus += 300
        if self.day >= 75: milestone_bonus += 500
        if self.day >= 100: milestone_bonus += 1000
        if milestone_bonus > 0:
            score_breakdown['里程碑獎勵'] = (milestone_bonus, f"{self.day}天達成")
            total_score += milestone_bonus
        
        return total_score, score_breakdown
    
    def get_endless_rank(self, days):
        """根據存活天數返回評級"""
        if days >= 100:
            return "傳說", (255, 215, 0), "🏆"
        elif days >= 75:
            return "史詩", (200, 100, 255), "⭐"
        elif days >= 50:
            return "精英", (100, 200, 255), "💎"
        elif days >= 30:
            return "老兵", (100, 255, 100), "🛡️"
        elif days >= 20:
            return "戰士", (255, 165, 0), "⚔️"
        elif days >= 15:
            return "倖存者", (200, 200, 200), "🎖️"
        else:
            return "新手", (150, 150, 150), "🔰"
    
    def show_endless_score_screen(self):
        """顯示無盡模式評分畫面"""
        total_score, breakdown = self.calculate_endless_score()
        rank_name, rank_color, rank_icon = self.get_endless_rank(self.day)
        
        # 保存最高紀錄
        self.save_endless_high_score(self.day)
        
        waiting = True
        while waiting:
            self.screen.fill((10, 10, 20))
            cx = (self.map_width + config.UI_WIDTH) // 2
            
            # 標題
            y = 30
            title = self.large_font.render("無盡模式評分", True, (138, 43, 226))
            self.screen.blit(title, (cx - title.get_width()//2, y))
            
            # 評級顯示
            y += 70
            rank_bg = pygame.Surface((180, 180), pygame.SRCALPHA)
            pygame.draw.circle(rank_bg, (*rank_color, 80), (90, 90), 85)
            self.screen.blit(rank_bg, (cx - 90, y))
            
            rank_icon_text = pygame.font.Font(None, 100).render(rank_icon, True, rank_color)
            self.screen.blit(rank_icon_text, (cx - rank_icon_text.get_width()//2, y + 35))
            
            rank_text = self.title_font.render(rank_name, True, rank_color)
            self.screen.blit(rank_text, (cx - rank_text.get_width()//2, y + 140))
            
            # 存活天數（大字）
            y += 200
            days_text = self.large_font.render(f"{self.day} 天", True, (255, 215, 0))
            self.screen.blit(days_text, (cx - days_text.get_width()//2, y))
            
            # 最高紀錄
            y += 60
            if self.day > self.endless_high_score or self.endless_high_score == 0:
                record_text = self.title_font.render("🏆 新紀錄！", True, (255, 215, 0))
            else:
                record_text = self.font.render(f"最高紀錄: {self.endless_high_score} 天", True, (150, 150, 150))
            self.screen.blit(record_text, (cx - record_text.get_width()//2, y))
            
            # 總分
            y += 60
            score_text = self.title_font.render(f"總分: {total_score}", True, (255, 255, 255))
            self.screen.blit(score_text, (cx - score_text.get_width()//2, y))
            
            # 評分明細
            y += 60
            detail_title = self.font.render("--- 評分明細 ---", True, (150, 150, 150))
            self.screen.blit(detail_title, (cx - detail_title.get_width()//2, y))
            y += 30
            
            for key, (points, desc) in breakdown.items():
                color = (100, 255, 100) if points > 0 else (255, 100, 100) if points < 0 else (200, 200, 200)
                sign = "+" if points > 0 else ""
                item_text = self.font.render(f"{key}: {sign}{points}  ({desc})", True, color)
                self.screen.blit(item_text, (cx - item_text.get_width()//2, y))
                y += 25
            
            # 提示
            hint = self.font.render("按 [任意鍵] 繼續", True, (150, 150, 150))
            self.screen.blit(hint, (cx - hint.get_width()//2, self.map_height - 40))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    waiting = False
    
    def show_score_screen(self, victory=False):
        """顯示詳細評分畫面"""
        final_score, breakdown, difficulty_mult = self.calculate_score(victory)
        rank, rank_color, rank_title = self.get_rank(final_score)
        
        # 記錄最終評級（用於成就）
        self.final_rank = rank
        
        # 計算鑽石獎勵
        diamond_reward = self.calculate_diamond_reward(rank, final_score, victory)
        
        waiting = True
        while waiting:
            self.screen.fill((10, 10, 15))
            cx = (self.map_width + config.UI_WIDTH) // 2
            
            # 標題
            y = 30
            if victory:
                title = self.large_font.render("🎉 勝利評分 🎉", True, (255, 215, 0))
            else:
                title = self.large_font.render("遊戲結算", True, (200, 200, 200))
            self.screen.blit(title, (cx - title.get_width()//2, y))
            
            # 評級顯示
            y += 80
            rank_bg = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(rank_bg, (*rank_color, 100), (100, 100), 90)
            self.screen.blit(rank_bg, (cx - 100, y))
            
            rank_text = pygame.font.Font(self.font.name if hasattr(self.font, 'name') else None, 120).render(rank, True, rank_color)
            self.screen.blit(rank_text, (cx - rank_text.get_width()//2, y + 30))
            
            rank_desc = self.title_font.render(rank_title, True, rank_color)
            self.screen.blit(rank_desc, (cx - rank_desc.get_width()//2, y + 160))
            
            # 總分
            y += 220
            score_text = self.large_font.render(f"總分: {final_score}", True, (255, 255, 255))
            self.screen.blit(score_text, (cx - score_text.get_width()//2, y))
            
            if difficulty_mult > 1.0:
                mult_text = self.font.render(f"({self.difficulty} 難度 x{difficulty_mult})", True, (255, 165, 0))
                self.screen.blit(mult_text, (cx - mult_text.get_width()//2, y + 45))
                y += 35
            
            # 詳細評分
            y += 80
            detail_title = self.title_font.render("--- 評分明細 ---", True, (150, 150, 150))
            self.screen.blit(detail_title, (cx - detail_title.get_width()//2, y))
            y += 45
            
            for category, (points, detail) in breakdown.items():
                color = (100, 255, 100) if points >= 0 else (255, 100, 100)
                sign = "+" if points >= 0 else ""
                
                # 類別名稱
                cat_text = self.font.render(f"{category}:", True, (200, 200, 200))
                self.screen.blit(cat_text, (cx - 300, y))
                
                # 詳情
                detail_text = self.font.render(detail, True, (180, 180, 180))
                self.screen.blit(detail_text, (cx - 100, y))
                
                # 分數
                point_text = self.font.render(f"{sign}{points}", True, color)
                self.screen.blit(point_text, (cx + 180, y))
                
                y += 30
            
            # 鑽石獎勵顯示
            y += 40
            diamond_title = self.title_font.render("💎 鑽石獎勵 💎", True, (100, 200, 255))
            self.screen.blit(diamond_title, (cx - diamond_title.get_width()//2, y))
            y += 40
            
            diamond_text = self.large_font.render(f"+{diamond_reward} 💎", True, (100, 200, 255))
            self.screen.blit(diamond_text, (cx - diamond_text.get_width()//2, y))
            y += 40
            
            total_diamonds = self.title_font.render(f"總鑽石: {self.diamonds} → {self.diamonds + diamond_reward}", True, (200, 200, 200))
            self.screen.blit(total_diamonds, (cx - total_diamonds.get_width()//2, y))
            
            # 提示
            y = self.map_height - 40
            hint = self.font.render("按 [任意鍵] 繼續", True, (150, 150, 150))
            self.screen.blit(hint, (cx - hint.get_width()//2, y))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    # 發放鑽石獎勵
                    self.diamonds += diamond_reward
                    self.save_diamonds()
                    waiting = False
    
    
    def achievement_screen(self):
        """成就查看畫面"""
        selected_category = "全部"
        categories = ["全部", "生存", "戰鬥", "收集", "人口", "事件", "特殊"]
        category_index = 0
        scroll_offset = 0
        
        while True:
            self.screen.fill((15, 15, 20))
            cx = (self.map_width + config.UI_WIDTH) // 2
            
            # 標題
            title = self.large_font.render("🏆 成就系統", True, (255, 215, 0))
            self.screen.blit(title, (cx - title.get_width()//2, 20))
            
            # 解鎖率
            unlocked, total, rate = self.achievement_manager.get_unlock_rate()
            rate_text = self.title_font.render(f"解鎖進度: {unlocked}/{total} ({rate:.1f}%)", True, (200, 200, 200))
            self.screen.blit(rate_text, (cx - rate_text.get_width()//2, 70))
            
            # 類別選擇
            y = 120
            cat_text = self.font.render(f"類別: {selected_category}", True, (255, 255, 255))
            self.screen.blit(cat_text, (50, y))
            hint = self.font.render("[左右鍵切換]", True, (150, 150, 150))
            self.screen.blit(hint, (250, y))
            
            # 獲取當前類別的成就
            if selected_category == "全部":
                achievements = self.achievement_manager.achievements
            else:
                achievements = self.achievement_manager.get_achievements_by_category(selected_category)
            
            # 顯示成就列表
            y = 170
            max_display = 8
            start_idx = scroll_offset
            end_idx = min(start_idx + max_display, len(achievements))
            
            for i in range(start_idx, end_idx):
                ach = achievements[i]
                
                # 成就框
                box_y = y + (i - start_idx) * 70
                box_height = 65
                
                # 背景
                if ach.unlocked:
                    bg_color = (30, 40, 30)
                    border_color = ach.icon_color
                else:
                    bg_color = (20, 20, 25)
                    border_color = (80, 80, 80)
                
                pygame.draw.rect(self.screen, bg_color, (50, box_y, self.map_width + config.UI_WIDTH - 100, box_height), 0, 5)
                pygame.draw.rect(self.screen, border_color, (50, box_y, self.map_width + config.UI_WIDTH - 100, box_height), 2, 5)
                
                # 圖標
                icon_size = 50
                pygame.draw.circle(self.screen, ach.icon_color if ach.unlocked else (60, 60, 60), 
                                 (85, box_y + box_height//2), icon_size//2)
                
                # 成就名稱
                name_color = (255, 255, 255) if ach.unlocked else (120, 120, 120)
                name = self.title_font.render(ach.name, True, name_color)
                self.screen.blit(name, (130, box_y + 5))
                
                # 描述
                desc_color = (200, 200, 200) if ach.unlocked else (100, 100, 100)
                desc = self.font.render(ach.description, True, desc_color)
                self.screen.blit(desc, (130, box_y + 35))
                
                # 稀有度標籤
                rarity_colors = {
                    "common": (200, 200, 200),
                    "rare": (100, 150, 255),
                    "epic": (200, 100, 255),
                    "legendary": (255, 215, 0)
                }
                rarity_names = {
                    "common": "普通",
                    "rare": "稀有",
                    "epic": "史詩",
                    "legendary": "傳說"
                }
                rarity_text = self.font.render(rarity_names[ach.rarity], True, rarity_colors[ach.rarity])
                self.screen.blit(rarity_text, (self.map_width + config.UI_WIDTH - 150, box_y + 10))
                
                # 解鎖時間
                if ach.unlocked and ach.unlock_time:
                    time_text = self.font.render(ach.unlock_time, True, (150, 150, 150))
                    self.screen.blit(time_text, (self.map_width + config.UI_WIDTH - 250, box_y + 40))
            
            # 滾動提示
            if len(achievements) > max_display:
                scroll_hint = self.font.render(f"[上下鍵滾動] {start_idx + 1}-{end_idx}/{len(achievements)}", True, (150, 150, 150))
                self.screen.blit(scroll_hint, (cx - scroll_hint.get_width()//2, self.map_height - 80))
            
            # 返回提示
            back_hint = self.font.render("按 [ESC] 返回", True, (150, 150, 150))
            self.screen.blit(back_hint, (cx - back_hint.get_width()//2, self.map_height - 40))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    elif event.key == pygame.K_LEFT:
                        category_index = (category_index - 1) % len(categories)
                        selected_category = categories[category_index]
                        scroll_offset = 0
                    elif event.key == pygame.K_RIGHT:
                        category_index = (category_index + 1) % len(categories)
                        selected_category = categories[category_index]
                        scroll_offset = 0
                    elif event.key == pygame.K_UP:
                        scroll_offset = max(0, scroll_offset - 1)
                    elif event.key == pygame.K_DOWN:
                        scroll_offset = min(len(achievements) - max_display, scroll_offset + 1) if len(achievements) > max_display else 0
    
    def difficulty_selection_screen(self):
        selected_diff = None
        while selected_diff is None:
            self.screen.fill((20, 10, 10))
            cx = (self.map_width + config.UI_WIDTH) // 2
            title = self.title_font.render("STEP 2: 選擇挑戰難度", True, (255, 200, 200))
            self.screen.blit(title, (cx - title.get_width()//2, 60))
            options = [
                {"key": "[1]", "name": "Normal (一般)", "color": (100, 255, 100), "desc": "標準體驗。資源生成正常，野獸傷害適中。"},
                {"key": "[2]", "name": "Hard (困難)", "color": (255, 165, 0), "desc": "資源生成 -30%，飢餓速度加快，夜襲傷害加倍。"},
                {"key": "[3]", "name": "Hell (地獄)", "color": (255, 0, 0), "desc": "極限挑戰。資源極少，且只要死亡一人即遊戲結束 (Permadeath)。"},
                {"key": "[4]", "name": "Endless (無盡)", "color": (138, 43, 226), "desc": "無盡模式！難度隨天數增加，挑戰你的極限，看能活幾天！"}
            ]
            y = 150    
            for opt in options:
                rect_w = 600
                rect_h = 120
                rect_x = cx - rect_w // 2
                pygame.draw.rect(self.screen, (40, 20, 20), (rect_x, y, rect_w, rect_h))
                pygame.draw.rect(self.screen, opt["color"], (rect_x, y, rect_w, rect_h), 2)
                key_txt = self.large_font.render(opt["key"], True, opt["color"])
                self.screen.blit(key_txt, (rect_x + 30, y + 35))
                name_txt = self.title_font.render(opt["name"], True, (255, 255, 255))
                self.screen.blit(name_txt, (rect_x + 120, y + 25))
                desc_txt = self.font.render(opt["desc"], True, (200, 200, 200))
                self.screen.blit(desc_txt, (rect_x + 120, y + 70))
                y += 140
            hint = self.font.render("按鍵盤 [1] [2] [3] [4] 確認", True, (150, 150, 150))
            self.screen.blit(hint, (cx - hint.get_width()//2, 600))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:  
                    if event.key == pygame.K_ESCAPE: return None
                    if event.key == pygame.K_1: selected_diff = "Normal"
                    if event.key == pygame.K_2: selected_diff = "Hard"
                    if event.key == pygame.K_3: selected_diff = "Hell"
                    if event.key == pygame.K_4: selected_diff = "Endless"  
        return selected_diff

    def run(self):  
        while True:
            self.reset_game_state()
            if not self.start_screen(): break
            hero = self.hero_selection_screen()
            if not hero: break
            diff = self.difficulty_selection_screen()
            if not diff: break
            
            self.apply_difficulty_settings(diff)
            self.init_world(hero)  
            
            running = True
            should_restart = False    
            
            while running:
                running = self.handle_input()
                self.update()
                self.draw()
                
                # 檢查死亡
                if not any(v.is_alive for v in self.villagers):
                    pygame.time.delay(1000)
                    if self.game_over_screen():
                        should_restart = True
                        running = False
                    else:
                        return # 離開        
                
                # 檢查勝利（無盡模式沒有15天限制）
                if self.day >= 15 and self.difficulty != "Endless":
                    pygame.time.delay(1000)
                    if self.game_won_screen():
                        should_restart = True
                        running = False
                    else:
                        return
                    
                self.clock.tick(config.FPS)
            
            if not should_restart: break  