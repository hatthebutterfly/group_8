import pygame
import random
import config

class EventManager:
    def __init__(self, engine):
        self.engine = engine
        self.active_event = None
        self.cooldown = 0
        
        # --- [新增] 結算畫面狀態 ---
        self.showing_result = False
        self.result_text = ""
        self.result_detail = ""
        self.result_color = (255, 255, 255)
    
    def check_trigger(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            return False

        # 機率觸發 (0.8% 機率)
        if random.random() < 0.008:
            if self.engine.day <= 3:
                self.trigger_risk_event()
            else:
                if random.random() < 0.6:
                    self.trigger_risk_event()
                else:
                    self.trigger_trade_event()
            
            self.cooldown = 300 
            return True 
        return False

    def trigger_risk_event(self):
        scenarios = [
            # --- 食物類 ---
            {
                "title": "未知的果樹", "desc": "樹上結滿了紅色的果實。",
                "options": [
                    {"text": "撿地上的 (70% +10食物 / 30% -5食物)", "cost": {}, "effect": "risk_food_tree_low"},
                    {"text": "爬樹去搖 (50% +40食物 / 50% 受傷 -10食物)", "cost": {}, "effect": "risk_food_tree_high"}
                ]
            },
            {
                "title": "巨大的蘑菇", "desc": "顏色鮮豔的蘑菇，看起來很好吃？",
                "options": [
                    {"text": "帶回去煮湯 (80% +15食物 / 20% 煮壞了 -5食物)", "cost": {}, "effect": "risk_food_mushroom_low"},
                    {"text": "生吃測試 (40% +60食物 / 60% 中毒 -30食物)", "cost": {}, "effect": "risk_food_mushroom_high"}
                ]
            },
            # --- 木頭類 ---
            {
                "title": "廢棄的礦坑", "desc": "洞口堆放著一些舊木材。",
                "options": [
                    {"text": "只撿洞口的 (70% +5木頭 / 30% 無)", "cost": {}, "effect": "risk_wood_mine_low"},
                    {"text": "深入內部 (50% +25木頭 / 50% 坍塌 -15HP)", "cost": {}, "effect": "risk_wood_mine_high"}
                ]
            },
            {
                "title": "漂流木", "desc": "河邊漂來巨大的木頭，但水流很急。",
                "options": [
                    {"text": "用繩子勾 (60% +8木頭 / 40% 繩子斷了 無)", "cost": {}, "effect": "risk_wood_river_low"},
                    {"text": "下水去撈 (40% +30木頭 / 60% 溺水 -2村民)", "cost": {}, "effect": "risk_wood_river_high"}
                ]
            },
            # --- 黃金類 ---
            {
                "title": "神秘的旅人", "desc": "一位穿著斗篷的人路過。",
                "options": [
                    {"text": "點頭致意 (70% +5黃金 / 30% 被扒手 -2黃金)", "cost": {}, "effect": "risk_gold_traveler_low"},
                    {"text": "邀請晚餐 (50% +20黃金 / 50% 是強盜 -15黃金)", "cost": {}, "effect": "risk_gold_traveler_high"}
                ]
            },
            # --- 特殊能力類 ---
            {
                "title": "發光的泉水", "desc": "喝下這泉水似乎能改變體質...",
                "options": [
                    {"text": "喝一小口 (70% 移速微增 / 30% 腹痛)", "cost": {}, "effect": "risk_speed_low"},
                    {"text": "大口暢飲 (50% 移速大增 / 50% 腿軟變慢)", "cost": {}, "effect": "risk_speed_high"}
                ]
            },
            {
                "title": "部落祭典", "desc": "是否舉行祈雨舞來祈求豐收？",
                "options": [
                    {"text": "簡單跳舞 (70% 全員飽食度回復 / 30% 無效)", "cost": {}, "effect": "risk_hunger_low"},
                    {"text": "狂歡整晚 (50% 全員回滿+加食物 / 50% 集體更餓)", "cost": {}, "effect": "risk_hunger_high"}
                ]
            }
        ]
        self.active_event = random.choice(scenarios)

    def trigger_trade_event(self):
        events = [
            {
                "title": "流浪商人", "desc": "商人兜售物資。",
                "options": [
                    {"text": "買糧 (5 黃金 -> 30 食物)", "cost": {"gold": 5}, "effect": "buy_food"},
                    {"text": "買木 (5 黃金 -> 5 木頭)", "cost": {"gold": 5}, "effect": "buy_wood"},
                    {"text": "離開", "cost": {}, "effect": "none"}
                ]
            },
            {
                "title": "防禦工程", "desc": "工匠建議修牆。",
                "options": [
                    {"text": "堅固圍牆 (10 木 -> +50 HP)", "cost": {"wood": 10}, "effect": "build_wall_strong"},
                    {"text": "簡易修補 (3 木 -> +15 HP)", "cost": {"wood": 3}, "effect": "build_wall_weak"},
                    {"text": "暫不建設", "cost": {}, "effect": "none"}
                ]
            }
        ]
        self.active_event = random.choice(events)

    def handle_input(self, key):
        # 狀態 2: 顯示結果中 (按任意鍵關閉)
        if self.showing_result:
            self.active_event = None
            self.showing_result = False
            return True # 回傳 True 代表解除暫停

        # 狀態 1: 選擇選項中
        if not self.active_event: return False
        
        choice = None
        if key == pygame.K_1: choice = 0
        elif key == pygame.K_2: choice = 1
        elif key == pygame.K_3: choice = 2
        
        if choice is not None and choice < len(self.active_event["options"]):
            opt = self.active_event["options"][choice]
            
            # 檢查資源
            can_afford = True
            if "gold" in opt["cost"] and self.engine.gold < opt["cost"]["gold"]: can_afford = False
            if "wood" in opt["cost"] and self.engine.wood < opt["cost"]["wood"]: can_afford = False
            if "food" in opt["cost"] and self.engine.food < opt["cost"]["food"]: can_afford = False
            
            if not can_afford:
                return False 
            
            # 扣除資源
            if "gold" in opt["cost"]: self.engine.gold -= opt["cost"]["gold"]
            if "wood" in opt["cost"]: self.engine.wood -= opt["cost"]["wood"]
            if "food" in opt["cost"]: self.engine.food -= opt["cost"]["food"]
            
            # 執行效果並進入結果畫面
            self.apply_effect(opt["effect"])
            self.showing_result = True
            return False # 回傳 False 代表繼續暫停，顯示結果畫面
            
        return False

    def set_result(self, is_good, title, detail):
        """設定結算畫面的內容"""
        self.result_text = title
        self.result_detail = detail
        if is_good:
            self.result_color = (100, 255, 100) # 綠色 (成功)
        else:
            self.result_color = (255, 100, 100) # 紅色 (失敗)
        
        # 同步寫入 Log
        self.engine.log_event(detail)

    def apply_effect(self, effect_name):
        rand = random.random() 

        # --- 食物 ---
        if effect_name == "risk_food_tree_low":
            if rand < 0.7: 
                self.engine.food += 10
                self.set_result(True, "成功！", "幸運撿到了 10 食物")
            else: 
                self.engine.food = max(0, self.engine.food - 5)
                self.set_result(False, "失敗...", "果實爛掉了...損失 5 食物")

        elif effect_name == "risk_food_tree_high":
            if rand < 0.5: 
                self.engine.food += 40
                self.set_result(True, "大成功！", "大豐收！獲得 40 食物")
            else: 
                self.engine.food = max(0, self.engine.food - 10)
                self.set_result(False, "失敗...", "摔下來壓爛了果實，損失 10 食物")
            
        elif effect_name == "risk_food_mushroom_low":
            if rand < 0.8: 
                self.engine.food += 15
                self.set_result(True, "成功！", "蘑菇湯很美味 +15 食物")
            else: 
                self.engine.food = max(0, self.engine.food - 5)
                self.set_result(False, "失敗...", "湯煮焦了...損失 5 食物")

        elif effect_name == "risk_food_mushroom_high":
            if rand < 0.4: 
                self.engine.food += 60
                self.set_result(True, "大成功！", "發現稀有松露！+60 食物")
            else: 
                self.engine.food = max(0, self.engine.food - 30)
                self.set_result(False, "大失敗！", "全村食物中毒...損失 30 食物")

        # --- 木頭 ---
        elif effect_name == "risk_wood_mine_low":
            if rand < 0.7: 
                self.engine.wood += 5
                self.set_result(True, "成功！", "撿到 5 木頭")
            else: 
                self.set_result(False, "無收穫", "什麼都沒找到")

        elif effect_name == "risk_wood_mine_high":
            if rand < 0.5: 
                self.engine.wood += 25
                self.set_result(True, "大成功！", "發現隱藏坑道 +25 木頭")
            else: 
                self.engine.wall_hp = max(0, self.engine.wall_hp - 15)
                self.set_result(False, "失敗！", "坑道坍塌震動了圍牆 -15 HP")
            
        elif effect_name == "risk_wood_river_low":
            if rand < 0.6: 
                self.engine.wood += 8
                self.set_result(True, "成功！", "勾到了漂流木 +8 木頭")
            else: 
                self.set_result(False, "失敗", "繩子斷了，木頭漂走了")

        elif effect_name == "risk_wood_river_high":
            if rand < 0.4: 
                self.engine.wood += 30
                self.set_result(True, "大成功！", "成功撈起巨木 +30 木頭")
            else: 
                # 溺水事件
                if len(self.engine.villagers) > 0:
                    victim = random.choice(self.engine.villagers)
                    victim.is_alive = False
                    self.set_result(False, "慘劇！！", f"{victim.name} 溺水身亡...")
                else:
                    self.set_result(False, "失敗", "差點溺水，幸好沒事")

        # --- 黃金 ---
        elif effect_name == "risk_gold_traveler_low":
            if rand < 0.7: 
                self.engine.gold += 5
                self.set_result(True, "成功！", "獲得 5 黃金")
            else: 
                self.engine.gold = max(0, self.engine.gold - 2)
                self.set_result(False, "失敗", "被扒手偷了 2 黃金")

        elif effect_name == "risk_gold_traveler_high":
            if rand < 0.5: 
                self.engine.gold += 20
                self.set_result(True, "大成功！", "旅人回贈 20 黃金")
            else: 
                self.engine.gold = max(0, self.engine.gold - 15)
                self.set_result(False, "失敗！", "遇到強盜！損失 15 黃金")

        # --- BUFF ---
        elif effect_name == "risk_speed_low":
            if rand < 0.7:
                for v in self.engine.villagers: v.speed *= 1.1 
                self.set_result(True, "成功！", "全員移動速度微增！")
            else:
                self.set_result(False, "無效", "泉水只是普通的水")
                
        elif effect_name == "risk_speed_high":
            if rand < 0.5:
                for v in self.engine.villagers: v.speed *= 1.5 
                self.set_result(True, "神蹟！", "全員移動速度大幅提升！")
            else:
                for v in self.engine.villagers: v.speed *= 0.7 
                self.set_result(False, "中毒...", "泉水有毒...全員移動變慢")

        elif effect_name == "risk_hunger_low":
            if rand < 0.7:
                for v in self.engine.villagers: v.hunger = 0 
                self.set_result(True, "成功！", "祭典讓大家都吃飽了")
            else:
                self.set_result(False, "無效", "祈雨舞似乎沒什麼用")

        elif effect_name == "risk_hunger_high":
            if rand < 0.5:
                for v in self.engine.villagers: v.hunger = 0
                self.engine.food += 30
                self.set_result(True, "大成功！", "全員吃飽且剩餘食物變多了")
            else:
                for v in self.engine.villagers: v.hunger = min(100, v.hunger + 30)
                self.set_result(False, "失敗...", "狂歡太累了，大家變得更餓了")

        # --- 交易 ---
        elif effect_name == "buy_food": 
            self.engine.food += 30
            self.set_result(True, "交易成功", "獲得 30 食物")
        elif effect_name == "buy_wood": 
            self.engine.wood += 5
            self.set_result(True, "交易成功", "獲得 5 木頭")
        elif effect_name == "build_wall_strong": 
            self.engine.wall_hp += 50
            self.set_result(True, "建設完成", "城牆耐久度大幅提升")
        elif effect_name == "build_wall_weak": 
            self.engine.wall_hp += 15
            self.set_result(True, "修補完成", "城牆耐久度小幅提升")
        elif effect_name == "none": 
            self.set_result(True, "離開", "沒有發生什麼事")

    def draw(self, screen):
        if not self.active_event: return
        
        # 半透明背景
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))
        
        cx, cy = screen.get_width()//2, screen.get_height()//2
        w, h = 660, 380 
        
        # --- 模式 2: 顯示結算畫面 ---
        if self.showing_result:
            # 畫結算框
            pygame.draw.rect(screen, (20, 20, 30), (cx-w//2, cy-h//2, w, h))
            pygame.draw.rect(screen, self.result_color, (cx-w//2, cy-h//2, w, h), 4) # 邊框顏色代表結果
            
            # 顯示「成功」或「失敗」
            res_title = self.engine.large_font.render(self.result_text, True, self.result_color)
            screen.blit(res_title, (cx - res_title.get_width()//2, cy - 50))
            
            # 顯示詳細內容
            res_detail = self.engine.title_font.render(self.result_detail, True, (255, 255, 255))
            screen.blit(res_detail, (cx - res_detail.get_width()//2, cy + 20))
            
            # 提示按鍵
            hint = self.engine.font.render("按 [任意鍵] 繼續", True, (150, 150, 150))
            screen.blit(hint, (cx - hint.get_width()//2, cy + h//2 - 40))
            return
            
        # --- 模式 1: 顯示選擇畫面 (原本的程式碼) ---
        if "risk" in self.active_event["options"][0]["effect"]:
            if "speed" in self.active_event["options"][0]["effect"] or "hunger" in self.active_event["options"][0]["effect"]:
                border_color = (255, 100, 100)
                title_color = (255, 150, 150)
            else:
                border_color = (200, 100, 255)
                title_color = (255, 100, 255)
        else:
            border_color = (100, 200, 255)
            title_color = (255, 215, 0)

        pygame.draw.rect(screen, (30, 30, 40), (cx-w//2, cy-h//2, w, h))
        pygame.draw.rect(screen, border_color, (cx-w//2, cy-h//2, w, h), 3)
        
        title = self.engine.title_font.render(self.active_event["title"], True, title_color)
        screen.blit(title, (cx - title.get_width()//2, cy - h//2 + 25))
        
        desc = self.engine.font.render(self.active_event["desc"], True, (220, 220, 220))
        screen.blit(desc, (cx - desc.get_width()//2, cy - h//2 + 70))
        
        y = cy - h//2 + 130
        for i, opt in enumerate(self.active_event["options"]):
            can_afford = True
            if "gold" in opt["cost"] and self.engine.gold < opt["cost"]["gold"]: can_afford = False
            if "wood" in opt["cost"] and self.engine.wood < opt["cost"]["wood"]: can_afford = False
            if "food" in opt["cost"] and self.engine.food < opt["cost"]["food"]: can_afford = False
            
            if len(opt["cost"]) == 0: color = (150, 255, 150)
            elif can_afford: color = (100, 255, 255)
            else: color = (100, 100, 100)
            
            text_surf = self.engine.font.render(f"{i+1}. {opt['text']}", True, color)
            screen.blit(text_surf, (cx - w//2 + 40, y))
            y += 50
            
        hint = self.engine.font.render("按鍵盤 [1] [2] 做選擇", True, (150, 150, 150))
        screen.blit(hint, (cx - hint.get_width()//2, cy + h//2 - 40))