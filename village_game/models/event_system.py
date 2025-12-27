import pygame
import random
import config

class EventManager:
    def __init__(self, engine):
        self.engine = engine
        self.active_event = None
        self.cooldown = 0
        
        # 結算畫面狀態 (顯示成功/失敗用)
        self.showing_result = False
        self.result_text = ""
        self.result_detail = ""
        self.result_color = (255, 255, 255)
    
    def check_trigger(self):
        # 如果是第 5, 10 天，禁止觸發隨機事件，以免跟黑市商人強碰
        if self.engine.day % 5 == 0:
            return False

        if self.cooldown > 0:
            self.cooldown -= 1
            return False

        # 一般隨機事件機率
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

    # --- [新增] 每 5 天出現的黑市商人 ---
    def trigger_special_shop(self):
        self.active_event = {
            "title": "黑市商人 (定期補給)",
            "desc": "每五天經過一次的神秘商隊，這裡有錢能買到一切！",
            "options": [
                {
                    "text": "大量糧食包 (15 金 -> +100 食物)", 
                    "cost": {"gold": 15}, 
                    "effect": "shop_food_bulk"
                },
                {
                    "text": "高級建材 (15 金 -> +40 木頭)", 
                    "cost": {"gold": 15}, 
                    "effect": "shop_wood_bulk"
                },
                {
                    "text": "傭兵修牆 (20 金 -> +150 HP)", 
                    "cost": {"gold": 20}, 
                    "effect": "shop_repair_wall"
                },
                {
                    "text": "神秘盲盒 (25 金 -> ???)", 
                    "cost": {"gold": 25}, 
                    "effect": "shop_mystery_box"
                }
            ]
        }

    def trigger_risk_event(self):
        scenarios = [
            # --- 食物 ---
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
            # --- 木頭 ---
            {
                "title": "廢棄的礦坑", "desc": "洞口堆放著一些舊木材。",
                "options": [
                    {"text": "只撿洞口的 (70% +5木頭 / 30% 無)", "cost": {}, "effect": "risk_wood_mine_low"},
                    {"text": "深入內部 (50% +25木頭 / 50% 坍塌 -15HP)", "cost": {}, "effect": "risk_wood_mine_high"}
                ]
            },
            # --- 黃金 ---
            {
                "title": "神秘的旅人", "desc": "一位穿著斗篷的人路過。",
                "options": [
                    {"text": "點頭致意 (70% +5黃金 / 30% 被扒手 -2黃金)", "cost": {}, "effect": "risk_gold_traveler_low"},
                    {"text": "邀請晚餐 (50% +20黃金 / 50% 是強盜 -15黃金)", "cost": {}, "effect": "risk_gold_traveler_high"}
                ]
            },
            # --- 特殊 BUFF ---
            {
                "title": "發光的泉水", "desc": "喝下這泉水似乎能改變體質...",
                "options": [
                    {"text": "喝一小口 (70% 移速微增 / 30% 腹痛)", "cost": {}, "effect": "risk_speed_low"},
                    {"text": "大口暢飲 (50% 移速大增 / 50% 腿軟變慢)", "cost": {}, "effect": "risk_speed_high"}
                ]
            }
        ]
        self.active_event = random.choice(scenarios)

    def trigger_trade_event(self):
        events = [
            {
                "title": "流浪商人", "desc": "普通的商人兜售物資。",
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
        # 1. 如果正在顯示結果，按任意鍵關閉
        if self.showing_result:
            self.active_event = None
            self.showing_result = False
            return True 

        # 2. 如果正在顯示選項
        if not self.active_event: return False
        
        choice = None
        if key == pygame.K_1: choice = 0
        elif key == pygame.K_2: choice = 1
        elif key == pygame.K_3: choice = 2
        elif key == pygame.K_4: choice = 3 # [支援] 第4個選項
        
        if choice is not None and choice < len(self.active_event["options"]):
            opt = self.active_event["options"][choice]
            
            # 檢查資源夠不夠
            can_afford = True
            if "gold" in opt["cost"] and self.engine.gold < opt["cost"]["gold"]: can_afford = False
            if "wood" in opt["cost"] and self.engine.wood < opt["cost"]["wood"]: can_afford = False
            if "food" in opt["cost"] and self.engine.food < opt["cost"]["food"]: can_afford = False
            
            if not can_afford:
                self.set_result(False, "資源不足", "你買不起這個東西！")
                self.showing_result = True
                return False 
            
            # 扣除資源
            if "gold" in opt["cost"]: self.engine.gold -= opt["cost"]["gold"]
            if "wood" in opt["cost"]: self.engine.wood -= opt["cost"]["wood"]
            if "food" in opt["cost"]: self.engine.food -= opt["cost"]["food"]
            
            # 執行效果
            self.apply_effect(opt["effect"])
            self.showing_result = True
            return False 
            
        return False

    def set_result(self, is_good, title, detail):
        self.result_text = title
        self.result_detail = detail
        if is_good:
            self.result_color = (100, 255, 100) # 綠色
        else:
            self.result_color = (255, 100, 100) # 紅色
        self.engine.log_event(detail)

    def apply_effect(self, effect_name):
        rand = random.random() 

        # --- [新增] 黑市商人效果 ---
        if effect_name == "shop_food_bulk":
            self.engine.food += 100
            self.set_result(True, "購買成功", "倉庫堆滿了糧食 (+100 食物)")
            
        elif effect_name == "shop_wood_bulk":
            self.engine.wood += 40
            self.set_result(True, "購買成功", "獲得大量優質木材 (+40 木頭)")
            
        elif effect_name == "shop_repair_wall":
            self.engine.wall_hp += 150
            self.set_result(True, "修復完成", "傭兵把城牆修得像新的一樣 (+150 HP)")
            
        elif effect_name == "shop_mystery_box":
            # 盲盒邏輯：40% 大獎, 30% 小獎, 30% 詐騙
            dice = random.randint(1, 10)
            if dice <= 4: # 大獎 (40%)
                reward_type = random.choice(["JACKPOT", "SPEED"])
                if reward_type == "JACKPOT":
                    self.engine.food += 100
                    self.engine.wood += 50
                    self.engine.wall_hp += 100
                    self.set_result(True, "大獎！！！", "傳說級物資箱！資源與城牆大補給！")
                else:
                    for v in self.engine.villagers: v.speed *= 1.3
                    self.set_result(True, "神秘藥水", "全村喝了奇怪的藥水，移動速度永久+30%！")
                    
            elif dice <= 7: # 普通 (30%)
                self.engine.gold += 10 
                self.engine.food += 20
                self.set_result(True, "普通獎", "裡面只有一些餅乾和零錢...")
                
            else: # 詐騙 (30%)
                self.set_result(False, "被騙了！", "箱子打開是空的...奸商已經跑了！")

        # --- 以下是原本的隨機事件效果 ---
        elif effect_name == "risk_food_tree_low":
            if rand < 0.7: 
                self.engine.food += 10; self.set_result(True, "成功", "獲得 10 食物")
            else: 
                self.engine.food = max(0, self.engine.food - 5); self.set_result(False, "失敗", "損失 5 食物")
        elif effect_name == "risk_food_tree_high":
            if rand < 0.5: 
                self.engine.food += 40; self.set_result(True, "大成功", "獲得 40 食物")
            else: 
                self.engine.food = max(0, self.engine.food - 10); self.set_result(False, "失敗", "損失 10 食物")
        elif effect_name == "risk_food_mushroom_low":
            if rand < 0.8: self.engine.food += 15; self.set_result(True, "成功", "獲得 15 食物")
            else: self.engine.food = max(0, self.engine.food - 5); self.set_result(False, "失敗", "損失 5 食物")
        elif effect_name == "risk_food_mushroom_high":
            if rand < 0.4: self.engine.food += 60; self.set_result(True, "大成功", "獲得 60 食物")
            else: self.engine.food = max(0, self.engine.food - 30); self.set_result(False, "大失敗", "損失 30 食物")
        elif effect_name == "risk_wood_mine_low":
            if rand < 0.7: self.engine.wood += 5; self.set_result(True, "成功", "獲得 5 木頭")
            else: self.set_result(False, "無收穫", "沒找到東西")
        elif effect_name == "risk_wood_mine_high":
            if rand < 0.5: self.engine.wood += 25; self.set_result(True, "大成功", "獲得 25 木頭")
            else: self.engine.wall_hp = max(0, self.engine.wall_hp - 15); self.set_result(False, "失敗", "圍牆受損 -15")
        elif effect_name == "risk_gold_traveler_low":
            if rand < 0.7: self.engine.gold += 5; self.set_result(True, "成功", "獲得 5 黃金")
            else: self.engine.gold = max(0, self.engine.gold - 2); self.set_result(False, "失敗", "損失 2 黃金")
        elif effect_name == "risk_gold_traveler_high":
            if rand < 0.5: self.engine.gold += 20; self.set_result(True, "大成功", "獲得 20 黃金")
            else: self.engine.gold = max(0, self.engine.gold - 15); self.set_result(False, "失敗", "損失 15 黃金")
        elif effect_name == "risk_speed_low":
            if rand < 0.7:
                for v in self.engine.villagers: v.speed *= 1.1 
                self.set_result(True, "成功", "速度微增")
            else: self.set_result(False, "無效", "沒反應")
        elif effect_name == "risk_speed_high":
            if rand < 0.5:
                for v in self.engine.villagers: v.speed *= 1.5 
                self.set_result(True, "神蹟", "速度大增")
            else:
                for v in self.engine.villagers: v.speed *= 0.7 
                self.set_result(False, "中毒", "速度變慢")
        elif effect_name == "buy_food": self.engine.food += 30; self.set_result(True, "交易", "獲得 30 食物")
        elif effect_name == "buy_wood": self.engine.wood += 5; self.set_result(True, "交易", "獲得 5 木頭")
        elif effect_name == "build_wall_strong": self.engine.wall_hp += 50; self.set_result(True, "建設", "牆壁 +50 HP")
        elif effect_name == "build_wall_weak": self.engine.wall_hp += 15; self.set_result(True, "修補", "牆壁 +15 HP")
        elif effect_name == "none": self.set_result(True, "離開", "無事發生")

    def draw(self, screen):
        if not self.active_event: return
        
        # 背景遮罩
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))
        
        cx, cy = screen.get_width()//2, screen.get_height()//2
        w, h = 700, 450 
        
        # --- 模式 2: 顯示結算畫面 ---
        if self.showing_result:
            pygame.draw.rect(screen, (20, 20, 30), (cx-w//2, cy-h//2, w, h))
            pygame.draw.rect(screen, self.result_color, (cx-w//2, cy-h//2, w, h), 4)
            
            res_title = self.engine.large_font.render(self.result_text, True, self.result_color)
            screen.blit(res_title, (cx - res_title.get_width()//2, cy - 50))
            
            res_detail = self.engine.title_font.render(self.result_detail, True, (255, 255, 255))
            screen.blit(res_detail, (cx - res_detail.get_width()//2, cy + 20))
            
            hint = self.engine.font.render("按 [任意鍵] 繼續", True, (150, 150, 150))
            screen.blit(hint, (cx - hint.get_width()//2, cy + h//2 - 40))
            return
            
        # --- 模式 1: 顯示選項畫面 ---
        if "shop" in self.active_event["options"][0]["effect"]:
            border_color = (255, 215, 0) # 金色
            title_color = (255, 255, 0)
        elif "risk" in self.active_event["options"][0]["effect"]:
            border_color = (200, 100, 255) # 紫色
            title_color = (255, 100, 255)
        else:
            border_color = (100, 200, 255) # 藍色
            title_color = (255, 215, 0)

        pygame.draw.rect(screen, (30, 30, 40), (cx-w//2, cy-h//2, w, h))
        pygame.draw.rect(screen, border_color, (cx-w//2, cy-h//2, w, h), 3)
        
        title = self.engine.title_font.render(self.active_event["title"], True, title_color)
        screen.blit(title, (cx - title.get_width()//2, cy - h//2 + 25))
        
        desc = self.engine.font.render(self.active_event["desc"], True, (220, 220, 220))
        screen.blit(desc, (cx - desc.get_width()//2, cy - h//2 + 70))
        
        y = cy - h//2 + 130
        for i, opt in enumerate(self.active_event["options"]):
            # 檢查錢夠不夠
            can_afford = True
            if "gold" in opt["cost"] and self.engine.gold < opt["cost"]["gold"]: can_afford = False
            if "wood" in opt["cost"] and self.engine.wood < opt["cost"]["wood"]: can_afford = False
            
            if len(opt["cost"]) == 0: color = (150, 255, 150)
            elif can_afford: color = (100, 255, 255)
            else: color = (100, 100, 100) # 買不起變灰色
            
            text_surf = self.engine.font.render(f"{i+1}. {opt['text']}", True, color)
            screen.blit(text_surf, (cx - w//2 + 40, y))
            y += 60
            
        hint = self.engine.font.render("按鍵盤數字鍵選擇", True, (150, 150, 150))
        screen.blit(hint, (cx - hint.get_width()//2, cy + h//2 - 40))