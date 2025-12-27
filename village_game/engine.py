import pygame
import random
import os
import config
from models.resource import Resource
from models.villager import Villager
from models.hero import SonicHero, HealerHero, TycoonHero
from models.event_system import EventManager

class GameEngine:
    def __init__(self):
        pygame.init()
        self.map_width = config.INITIAL_MAP_WIDTH
        self.map_height = config.INITIAL_MAP_HEIGHT
        self.screen = pygame.display.set_mode((self.map_width + config.UI_WIDTH, self.map_height))
        
        # 設定視窗標題
        pygame.display.set_caption("Village Sim: 15 Days Challenge")
        
        self.clock = pygame.time.Clock()
        
        # 字體設定
        if os.path.exists(config.FONT_FILE):
            print(f"成功載入字體: {config.FONT_FILE}")
            self.font = pygame.font.Font(config.FONT_FILE, 20)
            self.title_font = pygame.font.Font(config.FONT_FILE, 30)
            self.large_font = pygame.font.Font(config.FONT_FILE, 50)
        else:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 60)

        self.villagers = []
        self.resources = []
        self.logs = ["系統啟動..."]
        self.day = 1
        self.frame_count = 0
        
        self.last_pop_milestone = 5
        self.prosperity = 0
        
        # 資源庫存
        self.food = 0
        self.wood = 0
        self.gold = 0
        self.wall_hp = 0  # 牆壁耐久度
        
        # 通知系統變數
        self.notification_text = ""
        self.notification_timer = 0
        self.notification_color = (255, 50, 50)
        
        self.heroes_spawned = 0
        self.event_manager = EventManager(self)
        self.is_paused = False
        self.init_world()

    def init_world(self):
        for i in range(5):
            self.villagers.append(Villager(self, f"獵人{i}", (255, 100, 100), "Hunter"))
        for i in range(5):
            self.villagers.append(Villager(self, f"農夫{i}", (100, 100, 255), "Farmer"))
        self.spawn_resources(30)

    def spawn_resources(self, count):
        for _ in range(count):
            x = random.randint(20, self.map_width - 20)
            y = random.randint(20, self.map_height - 20)
            self.resources.append(Resource(x, y))

    def spawn_hero(self):
        self.heroes_spawned += 1
        hero_type = random.choice(["Sonic", "Healer", "Tycoon"])
        name = f"{hero_type}-{self.heroes_spawned}"
        
        hero = None
        if hero_type == "Sonic": hero = SonicHero(self, name)
        elif hero_type == "Healer": hero = HealerHero(self, name)
        elif hero_type == "Tycoon": hero = TycoonHero(self, name)
        
        hero.pos.x = random.randint(50, self.map_width-50)
        hero.pos.y = random.randint(50, self.map_height-50)
        self.villagers.append(hero)
        self.log_event(f"傳說英雄 {name} 加入村莊！")
        config.PROSPERITY_THRESHOLD += 300

    def expand_village(self):
        if self.map_width >= config.MAX_MAP_WIDTH: return
        old_w = self.map_width
        self.map_width = min(self.map_width + 250, config.MAX_MAP_WIDTH)
        self.map_height = min(self.map_height + 150, config.MAX_MAP_HEIGHT)
        self.screen = pygame.display.set_mode((self.map_width + config.UI_WIDTH, self.map_height))
        self.log_event(f"村莊大擴建！({self.map_width}x{self.map_height})")
        for _ in range(20):
            self.resources.append(Resource(random.randint(old_w, self.map_width), random.randint(0, self.map_height)))

    def log_event(self, text):
        self.logs.insert(0, f"[D{self.day}] {text}")
        if len(self.logs) > 20: self.logs.pop()

    def show_notification(self, text, color=(255, 50, 50)):
        self.notification_text = text
        self.notification_color = color
        self.notification_timer = 180  # 顯示約 3 秒

    def update(self):
        if self.is_paused: return
        self.frame_count += 1
        
        # 通知計時器倒數
        if self.notification_timer > 0:
            self.notification_timer -= 1
        
        if self.frame_count >= config.DAY_LENGTH:
            self.day += 1
            self.frame_count = 0
            self.log_event("--- 新的一天 ---")
            
            # --- 夜襲系統 ---
            attack_damage = random.randint(15, 40)
            
            if self.wall_hp > 0:
                actual_dmg = min(self.wall_hp, attack_damage)
                self.wall_hp -= actual_dmg
                self.log_event(f"昨晚野獸來襲！牆壁擋下了 {actual_dmg} 傷害")
                self.show_notification(f"⚠️ 敵襲！牆壁受損 -{actual_dmg}", (255, 100, 0))
                
                if self.wall_hp == 0:
                    self.log_event("⚠️ 警告：牆壁被野獸摧毀了！")
                    self.show_notification("⚠️ 牆壁被摧毀了！", (255, 0, 0))
            else:
                living = [v for v in self.villagers if v.is_alive]
                if len(living) > 0 and random.random() < 0.4:
                    victim = random.choice(living)
                    victim.is_alive = False
                    self.log_event(f"😱 慘劇：{victim.name} 被咬死了！")
                    self.show_notification(f"😱 慘劇！{victim.name} 死亡", (200, 0, 0))
                else:
                    self.log_event("昨晚運氣好，野獸沒有發現村民")
                    self.show_notification("昨晚平安無事", (100, 255, 100))
            # ----------------

            self.spawn_resources(15)
            
            pop = sum(1 for v in self.villagers if v.is_alive)
            if pop > self.last_pop_milestone:
                self.expand_village()
                self.last_pop_milestone += 2

        if self.frame_count % 60 == 0:
            pop = sum(1 for v in self.villagers if v.is_alive)
            self.prosperity += pop * 0.2

        if self.event_manager.check_trigger():
            self.is_paused = True
            return

        if (self.prosperity >= config.PROSPERITY_THRESHOLD and 
            self.heroes_spawned < config.MAX_HEROES and random.random() < 0.02):
            self.spawn_hero()

        for v in self.villagers: v.update()
        self.resources = [r for r in self.resources if r.active]

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            
            if self.is_paused:
                if event.type == pygame.KEYDOWN:
                    if self.event_manager.handle_input(event.key):
                        self.is_paused = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mx < self.map_width:
                    self.resources.append(Resource(mx, my))
        return True

    def draw_ui(self):
        ui_x = self.map_width
        
        # UI 背景
        pygame.draw.rect(self.screen, config.COLOR_UI, (ui_x, 0, config.UI_WIDTH, self.map_height))
        pygame.draw.line(self.screen, (100,100,100), (ui_x, 0), (ui_x, self.map_height), 2)
        
        icon_y = 25
        text_y = 18
        
        # 資源顯示
        pygame.draw.circle(self.screen, config.COLOR_FOOD, (ui_x + 20, icon_y), 8)
        self.screen.blit(self.font.render(f"{int(self.food)}", True, config.COLOR_TEXT), (ui_x + 35, text_y))
        pygame.draw.circle(self.screen, config.COLOR_WOOD, (ui_x + 90, icon_y), 8)
        self.screen.blit(self.font.render(f"{int(self.wood)}", True, config.COLOR_TEXT), (ui_x + 105, text_y))
        pygame.draw.circle(self.screen, config.COLOR_GOLD, (ui_x + 160, icon_y), 8)
        self.screen.blit(self.font.render(f"{int(self.gold)}", True, config.COLOR_TEXT), (ui_x + 175, text_y))
        
        # 牆壁血量
        wall_y = 55
        wall_color = (100, 200, 255) if self.wall_hp > 0 else (255, 100, 100)
        wall_txt = f"Wall HP: {self.wall_hp}"
        self.screen.blit(self.font.render(wall_txt, True, wall_color), (ui_x + 20, wall_y))
        
        pygame.draw.line(self.screen, (80,80,80), (ui_x + 10, 80), (ui_x + config.UI_WIDTH - 10, 80), 1)

        # 遊戲進度資訊
        base_y = 95 
        # 顯示目標天數
        self.screen.blit(self.title_font.render(f"Day: {self.day} / 15", True, config.COLOR_TEXT), (ui_x+10, base_y))
        
        pop = sum(1 for v in self.villagers if v.is_alive)
        self.screen.blit(self.font.render(f"Pop: {pop}", True, config.COLOR_TEXT), (ui_x+10, base_y + 35))
        
        p_str = f"Prosperity: {int(self.prosperity)}"
        self.screen.blit(self.font.render(p_str, True, (200, 100, 255)), (ui_x+10, base_y + 70))
        
        bar_w = 200 * min(1.0, self.prosperity/config.PROSPERITY_THRESHOLD)
        pygame.draw.rect(self.screen, (50,50,50), (ui_x+10, base_y + 90, 200, 10))
        pygame.draw.rect(self.screen, (138,43,226), (ui_x+10, base_y + 90, bar_w, 10))

        # Logs
        log_y = base_y + 120
        pygame.draw.line(self.screen, (100,100,100), (ui_x, log_y - 10), (ui_x+config.UI_WIDTH, log_y - 10), 1)
        for l in self.logs:
            self.screen.blit(self.font.render(l, True, (200,200,200)), (ui_x+10, log_y))
            log_y += 20

    def draw(self):
        self.screen.fill(config.COLOR_MAP)
        pygame.draw.rect(self.screen, config.COLOR_BORDER, (0,0,self.map_width, self.map_height), 2)
        
        for r in self.resources: r.draw(self.screen)
        for v in self.villagers: v.draw(self.screen)
        
        if self.is_paused: 
            self.event_manager.draw(self.screen)
        else: 
            self.draw_ui()
            # 繪製紅色警報通知
            if self.notification_timer > 0:
                cx, cy = self.map_width // 2, self.map_height // 2
                text_surf = self.large_font.render(self.notification_text, True, self.notification_color)
                padding = 20
                rect = pygame.Rect(
                    cx - text_surf.get_width() // 2 - padding,
                    cy - text_surf.get_height() // 2 - padding,
                    text_surf.get_width() + padding * 2,
                    text_surf.get_height() + padding * 2
                )
                s = pygame.Surface((rect.width, rect.height))
                s.set_alpha(200)
                s.fill((0, 0, 0))
                self.screen.blit(s, (rect.x, rect.y))
                pygame.draw.rect(self.screen, self.notification_color, rect, 3)
                self.screen.blit(text_surf, (cx - text_surf.get_width() // 2, cy - text_surf.get_height() // 2))
        
        pygame.display.flip()

    # --- 開始畫面 ---
    def start_screen(self):
        waiting = True
        while waiting:
            self.screen.fill((20, 20, 30))
            
            # 標題
            title = self.large_font.render("Village Sim: 15 Days Challenge", True, (255, 215, 0))
            self.screen.blit(title, (self.map_width//2 - title.get_width()//2 + 100, 100))

            # 說明文字
            instructions = [
                "【生存挑戰】目標：活到第 15 天",
                "-----------------------------",
                "1. 前三天充滿未知：只會發生隨機的幸運或厄運事件。",
                "2. 第四天起：商人會出現，開放資源交易與修牆。",
                "3. 資源管理：木頭可用於修牆，黃金可用於購買糧食。",
                "4. 小心夜襲：沒有圍牆的村莊，村民隨時會死亡。",
                "5. 只要看到 [Day 15] 出現，即視為勝利！",
                "-----------------------------",
                "按 [任意鍵] 開始挑戰"
            ]
            
            y = 200
            for line in instructions:
                text = self.font.render(line, True, (200, 200, 200))
                self.screen.blit(text, (self.map_width//2 - text.get_width()//2 + 100, y))
                y += 40

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    waiting = False
        return True

    # --- 失敗畫面 ---
    def game_over_screen(self):
        while True:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            title = self.large_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 200))
            
            score_text = self.title_font.render(f"存活天數: {self.day} 天 | 失敗...", True, (255, 255, 255))
            self.screen.blit(score_text, (self.screen.get_width()//2 - score_text.get_width()//2, 300))
            
            hint = self.font.render("按 [ESC] 離開遊戲", True, (200, 200, 200))
            self.screen.blit(hint, (self.screen.get_width()//2 - hint.get_width()//2, 400))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

    # --- 勝利畫面 ---
    def game_won_screen(self):
        while True:
            # 金色勝利背景
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            title = self.large_font.render("VICTORY!", True, (255, 215, 0))
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 200))
            
            sub = self.title_font.render("你成功生存了 15 天！", True, (255, 255, 255))
            self.screen.blit(sub, (self.screen.get_width()//2 - sub.get_width()//2, 260))
            
            pop = len([v for v in self.villagers if v.is_alive])
            score_text = self.font.render(f"最終繁榮度: {int(self.prosperity)} | 倖存人口: {pop}", True, (200, 200, 255))
            self.screen.blit(score_text, (self.screen.get_width()//2 - score_text.get_width()//2, 320))
            
            hint = self.font.render("按 [ESC] 離開遊戲", True, (200, 200, 200))
            self.screen.blit(hint, (self.screen.get_width()//2 - hint.get_width()//2, 400))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

    def run(self):
        # 1. 顯示開始畫面
        if not self.start_screen():
            return

        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            
            # 2. 檢查失敗條件 (全滅)
            living_villagers = [v for v in self.villagers if v.is_alive]
            if len(living_villagers) == 0:
                self.log_event("村莊已滅亡...")
                self.draw()
                pygame.time.delay(1000)
                self.game_over_screen()
                running = False
            
            # 3. 檢查勝利條件 (第15天)
            if self.day >= 15:
                self.log_event("目標達成！遊戲勝利！")
                self.draw()
                pygame.time.delay(1000)
                self.game_won_screen()
                running = False
            
            self.clock.tick(config.FPS)