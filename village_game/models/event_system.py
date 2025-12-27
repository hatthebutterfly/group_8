import pygame
import random
import config

class EventManager:
    def __init__(self, engine):
        self.engine = engine
        self.active_event = None
        self.cooldown = 0
    
    def check_trigger(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            return False

        # 機率觸發 (0.8% 機率)
        if random.random() < 0.008:
            # 根據天數決定事件池
            if self.engine.day <= 3:
                # 前三天：只有風險抉擇事件
                self.trigger_risk_event()
            else:
                # 第四天後：風險事件 與 商人事件 混合出現
                if random.random() < 0.6: # 60% 風險抉擇
                    self.trigger_risk_event()
                else:
                    self.trigger_trade_event()
            
            self.cooldown = 300 
            return True 
        return False

    def trigger_risk_event(self):
        """
        風險管理事件：
        選項 1 (保守)：70% 獲得小獎勵，30% 獲得小處罰
        選項 2 (冒險)：50% 獲得大獎勵，50% 獲得大處罰
        """
        scenarios = [
            {
                "title": "未知的果樹",
                "desc": "發現一種沒看過的果實，要怎麼採集？",
                "options": [
                    {
                        "text": "保守：只撿地上的 (70% +15食物 / 30% -5食物)", 
                        "cost": {}, 
                        "effect": "risk_food_low"
                    },
                    {
                        "text": "冒險：爬上去搖樹 (50% +50食物 / 50% 受傷 -20食物)", 
                        "cost": {}, 
                        "effect": "risk_food_high"
                    }
                ]
            },
            {
                "title": "廢棄的礦坑",
                "desc": "這裡似乎還有剩下的資源...",
                "options": [
                    {
                        "text": "保守：在洞口撿拾 (70% +5木頭 / 30% 無收穫)", 
                        "cost": {}, 
                        "effect": "risk_wood_low"
                    },
                    {
                        "text": "冒險：深入內部 (50% +20木頭 / 50% 坍塌 -15HP)", 
                        "cost": {}, 
                        "effect": "risk_wood_high"
                    }
                ]
            },
            {
                "title": "神秘的旅人",
                "desc": "遇到一位看起來很可疑的旅人。",
                "options": [
                    {
                        "text": "保守：簡單問候 (70% +5黃金 / 30% 被偷 -2黃金)", 
                        "cost": {}, 
                        "effect": "risk_gold_low"
                    },
                    {
                        "text": "冒險：邀請共進晚餐 (50% +20黃金 / 50% 被洗劫 -10黃金)", 
                        "cost": {}, 
                        "effect": "risk_gold_high"
                    }
                ]
            }
        ]
        self.active_event = random.choice(scenarios)

    def trigger_trade_event(self):
        """
        商人與建設事件 (Day 4 後才會出現)
        """
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
        if not self.active_event: return False
        
        choice = None
        if key == pygame.K_1: choice = 0
        elif key == pygame.K_2: choice = 1
        elif key == pygame.K_3: choice = 2
        
        if choice is not None and choice < len(self.active_event["options"]):
            opt = self.active_event["options"][choice]
            
            # 檢查資源是否足夠 (針對商人事件)
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
            
            self.apply_effect(opt["effect"])
            self.active_event = None
            return True
        return False

    def apply_effect(self, effect_name):
        rand = random.random() # 擲骰子 (0.0 ~ 1.0)

        # --- 風險抉擇：食物 ---
        if effect_name == "risk_food_low":
            if rand < 0.7: # 70% 成功
                self.engine.food += 15
                self.engine.log_event("保守：幸運撿到了 15 食物")
            else:          # 30% 失敗
                self.engine.food = max(0, self.engine.food - 5)
                self.engine.log_event("保守：果實有毒...損失 5 食物")

        elif effect_name == "risk_food_high":
            if rand < 0.5: # 50% 成功
                self.engine.food += 50
                self.engine.log_event("大冒險：大豐收！獲得 50 食物")
            else:          # 50% 失敗
                self.engine.food = max(0, self.engine.food - 20)
                self.engine.log_event("大冒險：摔下來受傷了...損失 20 食物")

        # --- 風險抉擇：木頭 ---
        elif effect_name == "risk_wood_low":
            if rand < 0.7:
                self.engine.wood += 5
                self.engine.log_event("保守：收集到 5 木頭")
            else:
                self.engine.log_event("保守：什麼都沒找到")

        elif effect_name == "risk_wood_high":
            if rand < 0.5:
                self.engine.wood += 20
                self.engine.log_event("大冒險：發現隱藏倉庫！+20 木頭")
            else:
                self.engine.wall_hp = max(0, self.engine.wall_hp - 15)
                self.engine.log_event("大冒險：引發坍塌！牆壁受損 -15")

        # --- 風險抉擇：黃金 ---
        elif effect_name == "risk_gold_low":
            if rand < 0.7:
                self.engine.gold += 5
                self.engine.log_event("保守：旅人送了 5 黃金")
            else:
                self.engine.gold = max(0, self.engine.gold - 2)
                self.engine.log_event("保守：錢包被偷了...損失 2 黃金")

        elif effect_name == "risk_gold_high":
            if rand < 0.5:
                self.engine.gold += 20
                self.engine.log_event("大冒險：旅人是富豪！回贈 20 黃金")
            else:
                self.engine.gold = max(0, self.engine.gold - 10)
                self.engine.log_event("大冒險：是強盜！被搶走 10 黃金")

        # --- 商人與建設 (100% 成功) ---
        elif effect_name == "buy_food": self.engine.food += 30; self.engine.log_event("交易：獲得 30 食物")
        elif effect_name == "buy_wood": self.engine.wood += 5; self.engine.log_event("交易：獲得 5 木頭")
        elif effect_name == "build_wall_strong": self.engine.wall_hp += 50; self.engine.log_event("城牆大修完成")
        elif effect_name == "build_wall_weak": self.engine.wall_hp += 15; self.engine.log_event("城牆簡易修補")
        
        elif effect_name == "none": self.engine.log_event("沒有發生什麼事")

    def draw(self, screen):
        if not self.active_event: return
        
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))
        
        cx, cy = screen.get_width()//2, screen.get_height()//2
        w, h = 640, 360 # 稍微加寬一點，因為選項文字變長了
        
        # 根據事件類型畫框框顏色
        # 風險事件用紫色，商人用藍色
        if "risk" in self.active_event["options"][0]["effect"]:
            border_color = (200, 100, 255) # 紫色
            title_color = (255, 100, 255)
        else:
            border_color = (100, 200, 255) # 藍色
            title_color = (255, 215, 0)    # 金色

        pygame.draw.rect(screen, (30, 30, 40), (cx-w//2, cy-h//2, w, h))
        pygame.draw.rect(screen, border_color, (cx-w//2, cy-h//2, w, h), 3)
        
        title = self.engine.title_font.render(self.active_event["title"], True, title_color)
        screen.blit(title, (cx - title.get_width()//2, cy - h//2 + 25))
        
        desc = self.engine.font.render(self.active_event["desc"], True, (220, 220, 220))
        screen.blit(desc, (cx - desc.get_width()//2, cy - h//2 + 70))
        
        # 畫選項
        y = cy - h//2 + 130
        for i, opt in enumerate(self.active_event["options"]):
            can_afford = True
            if "gold" in opt["cost"] and self.engine.gold < opt["cost"]["gold"]: can_afford = False
            if "wood" in opt["cost"] and self.engine.wood < opt["cost"]["wood"]: can_afford = False
            if "food" in opt["cost"] and self.engine.food < opt["cost"]["food"]: can_afford = False
            
            if len(opt["cost"]) == 0: color = (150, 255, 150) # 綠色 (免費/風險選項)
            elif can_afford: color = (100, 255, 255) # 青色 (可買)
            else: color = (100, 100, 100) # 灰色 (不可買)
            
            # 選項文字可能比較長，這裡簡單處理
            text_surf = self.engine.font.render(f"{i+1}. {opt['text']}", True, color)
            screen.blit(text_surf, (cx - w//2 + 40, y))
            y += 50
            
        hint = self.engine.font.render("按鍵盤 [1] [2] 做選擇", True, (150, 150, 150))
        screen.blit(hint, (cx - hint.get_width()//2, cy + h//2 - 40))