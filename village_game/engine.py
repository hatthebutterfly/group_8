import pygame
import random
import os
import config
from models.resource import Resource
from models.villager import Villager
# 引入所有 5 位英雄
from models.hero import SonicHero, HealerHero, TycoonHero, BuilderHero, OracleHero
from models.event_system import EventManager

class GameEngine:
    def __init__(self):
        pygame.init()
        self.map_width = config.INITIAL_MAP_WIDTH
        self.map_height = config.INITIAL_MAP_HEIGHT
        self.screen = pygame.display.set_mode((self.map_width + config.UI_WIDTH, self.map_height))
        
        pygame.display.set_caption("Village Sim: 15 Days Challenge")
        
        self.clock = pygame.time.Clock()
        
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
        
        self.food = 0
        self.wood = 0
        self.gold = 0
        self.wall_hp = 0
        
        self.notification_text = ""
        self.notification_timer = 0
        self.notification_color = (255, 50, 50)
        
        self.event_manager = EventManager(self)
        self.is_paused = False
        
        # --- 難度參數 ---
        self.difficulty = "Normal"
        self.spawn_rate = 15      
        self.night_dmg_min = 15   
        self.night_dmg_max = 40   
        self.is_hell_mode = False 

    def apply_difficulty_settings(self, level):
        """根據選擇的難度調整遊戲參數"""
        self.difficulty = level
        
        if level == "Normal":
            config.HUNGER_RATE = 0.1
            self.spawn_rate = 15
            self.night_dmg_min = 15
            self.night_dmg_max = 40
            self.is_hell_mode = False
            self.log_event("難度設定：一般。祝你好運！")

        elif level == "Hard":
            config.HUNGER_RATE = 0.15 
            self.spawn_rate = 10      
            self.night_dmg_min = 30
            self.night_dmg_max = 60
            self.is_hell_mode = False
            self.log_event("難度設定：困難。資源稀缺，夜襲更強！")

        elif level == "Hell":
            config.HUNGER_RATE = 0.2  
            self.spawn_rate = 8       
            self.night_dmg_min = 50   
            self.night_dmg_max = 100
            self.is_hell_mode = True  
            self.log_event("難度設定：地獄。只要死一人即結束！")

    def init_world(self, hero_choice):
        # 1. 生成普通村民
        for i in range(5):
            self.villagers.append(Villager(self, f"獵人{i}", (255, 100, 100), "Hunter"))
        for i in range(5):
            self.villagers.append(Villager(self, f"農夫{i}", (100, 100, 255), "Farmer"))
            
        # 2. 生成玩家選擇的英雄
        hero = None
        if hero_choice == 1:
            hero = SonicHero(self, "艾里奧")
            self.log_event("【迅捷之風】艾里奧 加入！")
        elif hero_choice == 2:
            hero = TycoonHero(self, "摩根")
            self.log_event("【黃金之手】摩根 加入！")
        elif hero_choice == 3:
            hero = HealerHero(self, "芙蕾雅")
            self.log_event("【守護者】芙蕾雅 加入！")
        elif hero_choice == 4:
            hero = BuilderHero(self, "泰坦")
            self.log_event("【堅毅之盾】泰坦 加入！")
        elif hero_choice == 5:
            hero = OracleHero(self, "瑟蕾絲")
            self.log_event("【豐收女神】瑟蕾絲 加入！")
            
        if hero:
            hero.pos.x = self.map_width // 2
            hero.pos.y = self.map_height // 2
            self.villagers.append(hero)

        # 3. 生成初始資源 (根據難度)
        initial_res = 30
        if self.difficulty == "Hard": initial_res = 20
        if self.difficulty == "Hell": initial_res = 10
        self.spawn_resources(initial_res)

    def spawn_resources(self, count):
        for _ in range(count):
            x = random.randint(20, self.map_width - 20)
            y = random.randint(20, self.map_height - 20)
            self.resources.append(Resource(x, y))

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
        self.notification_timer = 180

    def update(self):
        if self.is_paused: return
        self.frame_count += 1
        
        if self.notification_timer > 0:
            self.notification_timer -= 1
        
        if self.frame_count >= config.DAY_LENGTH:
            self.day += 1
            self.frame_count = 0
            self.log_event("--- 新的一天 ---")
            
            # --- [新增] 每 5 天 (Day 5, 10) 觸發黑市商店 ---
            if self.day % 5 == 0 and self.day < 15:
                self.event_manager.trigger_special_shop()
                self.is_paused = True # 強制暫停進入商店
            # -------------------------------------------
            
            # 夜襲系統 (依難度)
            attack_damage = random.randint(self.night_dmg_min, self.night_dmg_max)
            
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
                    
                    # 地獄模式：死人即結束
                    if self.is_hell_mode:
                        self.log_event("地獄模式規則：有人死亡，遊戲結束！")
                        for v in self.villagers: v.is_alive = False
                else:
                    self.log_event("昨晚運氣好，野獸沒有發現村民")
                    self.show_notification("昨晚平安無事", (100, 255, 100))

            # 資源生成 (依難度)
            self.spawn_resources(self.spawn_rate)
            
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
        pygame.draw.rect(self.screen, config.COLOR_UI, (ui_x, 0, config.UI_WIDTH, self.map_height))
        pygame.draw.line(self.screen, (100,100,100), (ui_x, 0), (ui_x, self.map_height), 2)
        
        icon_y = 25
        text_y = 18
        
        pygame.draw.circle(self.screen, config.COLOR_FOOD, (ui_x + 20, icon_y), 8)
        self.screen.blit(self.font.render(f"{int(self.food)}", True, config.COLOR_TEXT), (ui_x + 35, text_y))
        pygame.draw.circle(self.screen, config.COLOR_WOOD, (ui_x + 90, icon_y), 8)
        self.screen.blit(self.font.render(f"{int(self.wood)}", True, config.COLOR_TEXT), (ui_x + 105, text_y))
        pygame.draw.circle(self.screen, config.COLOR_GOLD, (ui_x + 160, icon_y), 8)
        self.screen.blit(self.font.render(f"{int(self.gold)}", True, config.COLOR_TEXT), (ui_x + 175, text_y))
        
        wall_y = 55
        wall_color = (100, 200, 255) if self.wall_hp > 0 else (255, 100, 100)
        wall_txt = f"Wall HP: {self.wall_hp}"
        self.screen.blit(self.font.render(wall_txt, True, wall_color), (ui_x + 20, wall_y))
        
        pygame.draw.line(self.screen, (80,80,80), (ui_x + 10, 80), (ui_x + config.UI_WIDTH - 10, 80), 1)

        base_y = 95 
        self.screen.blit(self.title_font.render(f"Day: {self.day} / 15", True, config.COLOR_TEXT), (ui_x+10, base_y))
        
        # 顯示當前難度
        diff_color = (200, 200, 200)
        if self.difficulty == "Hard": diff_color = (255, 100, 100)
        if self.difficulty == "Hell": diff_color = (255, 0, 0)
        self.screen.blit(self.font.render(f"Mode: {self.difficulty}", True, diff_color), (ui_x+10, base_y + 35))

        pop = sum(1 for v in self.villagers if v.is_alive)
        self.screen.blit(self.font.render(f"Pop: {pop}", True, config.COLOR_TEXT), (ui_x+10, base_y + 70))
        
        p_str = f"Prosperity: {int(self.prosperity)}"
        self.screen.blit(self.font.render(p_str, True, (200, 100, 255)), (ui_x+10, base_y + 105))
        
        bar_w = 200 * min(1.0, self.prosperity/2000)
        pygame.draw.rect(self.screen, (50,50,50), (ui_x+10, base_y + 125, 200, 10))
        pygame.draw.rect(self.screen, (138,43,226), (ui_x+10, base_y + 125, bar_w, 10))

        log_y = base_y + 155
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

    def start_screen(self):
        waiting = True
        while waiting:
            self.screen.fill((20, 20, 30))
            title = self.large_font.render("Village Sim: 15 Days Challenge", True, (255, 215, 0))
            self.screen.blit(title, (self.map_width//2 - title.get_width()//2 + 100, 100))

            instructions = [
                "【生存挑戰】目標：活到第 15 天",
                "-----------------------------",
                "1. 選擇你的領袖英雄，這將決定你的生存策略。",
                "2. 選擇遊戲難度：挑戰你的極限。",
                "3. 前三天充滿未知風險，第四天起開放交易。",
                "4. 資源管理：木頭修牆，黃金買糧。",
                "5. 只要看到 [Day 15] 出現，即視為勝利！",
                "-----------------------------",
                "按 [任意鍵] 繼續"
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

    # --- 英雄選擇 (緊湊版) ---
    def hero_selection_screen(self):
        selected_hero = None
        while selected_hero is None:
            self.screen.fill((15, 15, 25))
            
            title = self.title_font.render("STEP 1: 選擇一位開局領袖", True, (255, 255, 255))
            self.screen.blit(title, (self.map_width//2 - title.get_width()//2 + 100, 40))
            
            options = [
                {"key": "[1]", "color": (100, 255, 100), "name": "迅捷之風 - 艾里奧", "desc": "極致速度(Spd 2.5)。掃蕩全圖資源，適合擴張流。"},
                {"key": "[2]", "color": (255, 215, 0), "name": "黃金之手 - 摩根", "desc": "煉金術。隨時間自動產出黃金，適合貿易流。"},
                {"key": "[3]", "color": (255, 100, 255), "name": "守護者 - 芙蕾雅", "desc": "治癒光環。自動治療受傷村民，降低死亡率。"},
                {"key": "[4]", "color": (180, 180, 180), "name": "堅毅之盾 - 泰坦", "desc": "工程修復。每秒自動免費修補城牆，防禦流必備。"},
                {"key": "[5]", "color": (255, 140, 0), "name": "豐收女神 - 瑟蕾絲", "desc": "神之恩惠。定期降低全員飢餓度，養活大量人口。"}
            ]
            
            y = 100
            cx = self.map_width // 2 + 100 
            
            for opt in options:
                rect_x = cx - 350
                rect_w = 700
                rect_h = 75
                pygame.draw.rect(self.screen, (30, 30, 40), (rect_x, y, rect_w, rect_h))
                pygame.draw.rect(self.screen, opt["color"], (rect_x, y, rect_w, rect_h), 2)
                
                key_text = self.large_font.render(opt["key"], True, opt["color"])
                self.screen.blit(key_text, (rect_x + 20, y + 15))
                name_text = self.title_font.render(opt["name"], True, (255, 255, 255))
                self.screen.blit(name_text, (rect_x + 100, y + 10))
                desc_text = self.font.render(opt["desc"], True, (200, 200, 200))
                self.screen.blit(desc_text, (rect_x + 100, y + 45))
                y += 85
            
            hint = self.font.render("按鍵盤 [1] ~ [5] 確認選擇", True, (150, 150, 150))
            self.screen.blit(hint, (self.map_width//2 - hint.get_width()//2 + 100, 540))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: selected_hero = 1
                    if event.key == pygame.K_2: selected_hero = 2
                    if event.key == pygame.K_3: selected_hero = 3
                    if event.key == pygame.K_4: selected_hero = 4
                    if event.key == pygame.K_5: selected_hero = 5
        
        return selected_hero

    # --- 難度選擇畫面 ---
    def difficulty_selection_screen(self):
        selected_diff = None
        while selected_diff is None:
            self.screen.fill((20, 10, 10))
            
            title = self.title_font.render("STEP 2: 選擇挑戰難度", True, (255, 200, 200))
            self.screen.blit(title, (self.map_width//2 - title.get_width()//2 + 100, 100))
            
            options = [
                {
                    "key": "[1]", "name": "一般 (Normal)", "color": (100, 255, 100),
                    "desc": "標準體驗。資源充足，敵人強度適中。"
                },
                {
                    "key": "[2]", "name": "困難 (Hard)", "color": (255, 165, 0),
                    "desc": "資源稀缺 (Spawn -30%)，飢餓速度加快，夜襲傷害倍增。"
                },
                {
                    "key": "[3]", "name": "地獄 (Hell)", "color": (255, 0, 0),
                    "desc": "極限挑戰。資源極少，且只要死亡任何一人，遊戲直接結束。"
                }
            ]
            
            y = 200
            cx = self.map_width // 2 + 100 
            
            for opt in options:
                rect_x = cx - 300
                rect_w = 600
                rect_h = 100
                
                pygame.draw.rect(self.screen, (40, 20, 20), (rect_x, y, rect_w, rect_h))
                pygame.draw.rect(self.screen, opt["color"], (rect_x, y, rect_w, rect_h), 2)
                
                key_text = self.large_font.render(opt["key"], True, opt["color"])
                self.screen.blit(key_text, (rect_x + 30, y + 25))
                
                name_text = self.title_font.render(opt["name"], True, (255, 255, 255))
                self.screen.blit(name_text, (rect_x + 120, y + 20))
                
                desc_text = self.font.render(opt["desc"], True, (200, 200, 200))
                self.screen.blit(desc_text, (rect_x + 120, y + 60))
                
                y += 120
            
            hint = self.font.render("按鍵盤 [1] [2] [3] 確認難度", True, (150, 150, 150))
            self.screen.blit(hint, (self.map_width//2 - hint.get_width()//2 + 100, 580))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: selected_diff = "Normal"
                    if event.key == pygame.K_2: selected_diff = "Hard"
                    if event.key == pygame.K_3: selected_diff = "Hell"
                    
        return selected_diff

    def game_over_screen(self):
        while True:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            title = self.large_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 200))
            
            if self.is_hell_mode and len(self.villagers) > 0:
                 reason = "地獄模式：有人犧牲了..."
            else:
                 reason = "村莊已滅亡..."
                 
            reason_text = self.title_font.render(reason, True, (200, 50, 50))
            self.screen.blit(reason_text, (self.screen.get_width()//2 - reason_text.get_width()//2, 260))

            score_text = self.title_font.render(f"存活天數: {self.day} 天", True, (255, 255, 255))
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

    def game_won_screen(self):
        while True:
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay.set_alpha(220)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            title = self.large_font.render("VICTORY!", True, (255, 215, 0))
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 150))
            
            sub = self.title_font.render("你成功生存了 15 天！", True, (255, 255, 255))
            self.screen.blit(sub, (self.screen.get_width()//2 - sub.get_width()//2, 210))
            
            final_score = int(self.prosperity)
            # 困難模式加分
            if self.difficulty == "Hard": final_score = int(final_score * 1.5)
            if self.difficulty == "Hell": final_score = int(final_score * 3.0)
            
            rank = "C"
            rank_color = (200, 200, 200)
            comment = "勉強倖存的難民營"
            
            if final_score >= 1500:
                rank = "S"
                rank_color = (255, 215, 0)
                comment = "傳說中的黃金帝國！"
            elif final_score >= 1000:
                rank = "A"
                rank_color = (255, 100, 255)
                comment = "繁榮昌盛的城邦"
            elif final_score >= 500:
                rank = "B"
                rank_color = (100, 255, 100)
                comment = "自給自足的村莊"
            
            rank_text = self.large_font.render(f"Rank: {rank}", True, rank_color)
            self.screen.blit(rank_text, (self.screen.get_width()//2 - rank_text.get_width()//2, 280))
            
            comment_text = self.font.render(comment, True, rank_color)
            self.screen.blit(comment_text, (self.screen.get_width()//2 - comment_text.get_width()//2, 330))

            pop = len([v for v in self.villagers if v.is_alive])
            score_text = self.font.render(f"最終繁榮度({self.difficulty}): {final_score} | 倖存人口: {pop}", True, (200, 200, 255))
            self.screen.blit(score_text, (self.screen.get_width()//2 - score_text.get_width()//2, 380))
            
            hint = self.font.render("按 [ESC] 離開遊戲", True, (200, 200, 200))
            self.screen.blit(hint, (self.screen.get_width()//2 - hint.get_width()//2, 450))
            
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
        # 1. 開始畫面
        if not self.start_screen():
            return
            
        # 2. 英雄選擇
        hero_choice = self.hero_selection_screen()
        if hero_choice is None:
            return
            
        # 3. 難度選擇
        diff_choice = self.difficulty_selection_screen()
        if diff_choice is None:
            return
            
        # 4. 套用難度並初始化世界
        self.apply_difficulty_settings(diff_choice)
        self.init_world(hero_choice)

        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            
            # 檢查死亡條件
            living_villagers = [v for v in self.villagers if v.is_alive]
            if len(living_villagers) == 0:
                self.log_event("村莊已滅亡...")
                self.draw()
                pygame.time.delay(1000)
                self.game_over_screen()
                running = False
            
            if self.day >= 15:
                self.log_event("目標達成！遊戲勝利！")
                self.draw()
                pygame.time.delay(1000)
                self.game_won_screen()
                running = False
            
            self.clock.tick(config.FPS)