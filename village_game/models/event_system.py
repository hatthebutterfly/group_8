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

        # 0.8% 機率觸發
        if random.random() < 0.008:
            self.trigger_mixed_event()
            self.cooldown = 300 
            return True 
        return False

    def trigger_mixed_event(self):
        # 1. 幸運事件
        lucky_events = [
            {"title": "幸運的發現", "desc": "撿到一袋糧食。", "options": [{"text": "撿起來 (+20 食物)", "cost": {}, "effect": "get_food"}]},
            {"title": "廢棄的營地", "desc": "發現可用的木材。", "options": [{"text": "回收木材 (+5 木頭)", "cost": {}, "effect": "get_wood"}]},
            {"title": "迷路的貴族", "desc": "指引貴族方向。", "options": [{"text": "接受謝禮 (+5 黃金)", "cost": {}, "effect": "get_gold"}]}
        ]

        # 2. 交易與建設 (Day 4 後才會出現)
        trade_events = [
            {
                "title": "流浪商人", "desc": "商人兜售物資。",
                "options": [
                    {"text": "買糧 (5 黃金 -> 30 食物)", "cost": {"gold": 5}, "effect": "buy_food"},
                    {"text": "買木 (5 黃金 -> 5 木頭)", "cost": {"gold": 5}, "effect": "buy_wood"},
                    {"text": "趕走他", "cost": {}, "effect": "none"}
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
        
        # 3. 厄運事件
        bad_events = [
            {
                "title": "鼠患爆發！", "desc": "老鼠正在啃食倉庫的糧食！",
                "options": [
                    {"text": "用木頭堵洞 (花費 3 木頭)", "cost": {"wood": 3}, "effect": "fix_rat_hole"},
                    {"text": "放任不管 (損失 30 食物)", "cost": {}, "effect": "lose_food_bad"}
                ]
            },
            {
                "title": "強盜勒索", "desc": "一群強盜包圍了村莊！",
                "options": [
                    {"text": "破財消災 (損失 5 黃金)", "cost": {"gold": 5}, "effect": "pay_bandit"},
                    {"text": "誓死抵抗 (牆壁受損 -30 HP)", "cost": {}, "effect": "fight_bandit"}
                ]
            },
             {
                "title": "流行病", "desc": "村民感到身體不適...",
                "options": [
                    {"text": "分發藥草 (花費 20 食物)", "cost": {"food": 20}, "effect": "cure_sickness"},
                    {"text": "無能為力 (繁榮度 -50)", "cost": {}, "effect": "epidemic_hit"}
                ]
            }
        ]

        # --- [關鍵修改] 根據天數決定事件池 ---
        
        if self.engine.day <= 3:
            # 前三天：只有幸運 (50%) 和 厄運 (50%)
            # 沒有商人，純粹看運氣和初期資源分配
            if random.random() < 0.5:
                self.active_event = random.choice(lucky_events)
            else:
                self.active_event = random.choice(bad_events)
        else:
            # 第四天後：混合模式
            # 30% 幸運, 40% 交易, 30% 厄運
            rand_val = random.random()
            if rand_val < 0.3:
                self.active_event = random.choice(lucky_events)
            elif rand_val < 0.7:
                self.active_event = random.choice(trade_events)
            else:
                self.active_event = random.choice(bad_events)

    def handle_input(self, key):
        if not self.active_event: return False
        
        choice = None
        if key == pygame.K_1: choice = 0
        elif key == pygame.K_2: choice = 1
        elif key == pygame.K_3: choice = 2
        
        if choice is not None and choice < len(self.active_event["options"]):
            opt = self.active_event["options"][choice]
            
            can_afford = True
            if "gold" in opt["cost"] and self.engine.gold < opt["cost"]["gold"]: can_afford = False
            if "wood" in opt["cost"] and self.engine.wood < opt["cost"]["wood"]: can_afford = False
            if "food" in opt["cost"] and self.engine.food < opt["cost"]["food"]: can_afford = False
            
            if not can_afford:
                return False 
            
            if "gold" in opt["cost"]: self.engine.gold -= opt["cost"]["gold"]
            if "wood" in opt["cost"]: self.engine.wood -= opt["cost"]["wood"]
            if "food" in opt["cost"]: self.engine.food -= opt["cost"]["food"]
            
            self.apply_effect(opt["effect"])
            self.active_event = None
            return True
        return False

    def apply_effect(self, effect_name):
        if effect_name == "get_food": self.engine.food += 20; self.engine.log_event("幸運：獲得 20 食物")
        elif effect_name == "get_wood": self.engine.wood += 5; self.engine.log_event("幸運：獲得 5 木頭")
        elif effect_name == "get_gold": self.engine.gold += 5; self.engine.log_event("幸運：獲得 5 黃金")
        elif effect_name == "buy_food": self.engine.food += 30; self.engine.log_event("交易：獲得 30 食物")
        elif effect_name == "buy_wood": self.engine.wood += 5; self.engine.log_event("交易：獲得 5 木頭")
        elif effect_name == "build_wall_strong": self.engine.wall_hp += 50; self.engine.log_event("城牆大修完成")
        elif effect_name == "build_wall_weak": self.engine.wall_hp += 15; self.engine.log_event("城牆簡易修補")
        
        elif effect_name == "fix_rat_hole":
            self.engine.log_event("修補了鼠洞，保住了糧食")
        elif effect_name == "lose_food_bad":
            loss = min(self.engine.food, 30)
            self.engine.food -= loss
            self.engine.log_event(f"老鼠吃掉了 {loss} 食物！")
        elif effect_name == "pay_bandit":
            self.engine.log_event("強盜拿了錢離開了")
        elif effect_name == "fight_bandit":
            self.engine.wall_hp = max(0, self.engine.wall_hp - 30)
            self.engine.log_event("抵抗成功，但牆壁受損嚴重！")
        elif effect_name == "cure_sickness":
            self.engine.log_event("村民恢復了健康")
        elif effect_name == "epidemic_hit":
            self.engine.prosperity = max(0, self.engine.prosperity - 50)
            self.engine.log_event("疫情蔓延，繁榮度大跌...")
        
        elif effect_name == "none": self.engine.log_event("沒有發生什麼事")

    def draw(self, screen):
        if not self.active_event: return
        
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))
        
        cx, cy = screen.get_width()//2, screen.get_height()//2
        w, h = 600, 350
        
        border_color = (200, 200, 200)
        pygame.draw.rect(screen, (40, 40, 50), (cx-w//2, cy-h//2, w, h))
        pygame.draw.rect(screen, border_color, (cx-w//2, cy-h//2, w, h), 2)
        
        title_color = (255, 215, 0)
        if "爆發" in self.active_event["title"] or "強盜" in self.active_event["title"] or "流行病" in self.active_event["title"]:
            title_color = (255, 50, 50)

        title = self.engine.title_font.render(self.active_event["title"], True, title_color)
        screen.blit(title, (cx - title.get_width()//2, cy - h//2 + 20))
        
        desc = self.engine.font.render(self.active_event["desc"], True, (255, 255, 255))
        screen.blit(desc, (cx - desc.get_width()//2, cy - h//2 + 60))
        
        y = cy - h//2 + 120
        for i, opt in enumerate(self.active_event["options"]):
            can_afford = True
            if "gold" in opt["cost"] and self.engine.gold < opt["cost"]["gold"]: can_afford = False
            if "wood" in opt["cost"] and self.engine.wood < opt["cost"]["wood"]: can_afford = False
            if "food" in opt["cost"] and self.engine.food < opt["cost"]["food"]: can_afford = False
            
            if len(opt["cost"]) == 0: color = (100, 255, 255)
            elif can_afford: color = (100, 255, 100)
            else: color = (100, 100, 100)
            
            text = self.engine.font.render(f"{i+1}. {opt['text']}", True, color)
            screen.blit(text, (cx - w//2 + 30, y))
            y += 40
            
        hint = self.engine.font.render("按鍵盤 [1] [2] [3] 選擇", True, (150, 150, 150))
        screen.blit(hint, (cx - hint.get_width()//2, cy + h//2 - 30))