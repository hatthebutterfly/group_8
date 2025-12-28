import pygame
import json
import os

class ShopItem:
    """商店物品"""
    def __init__(self, id, name, description, category, price, effect_type, effect_value, is_permanent=False, icon_color=(255, 255, 255)):
        self.id = id
        self.name = name
        self.description = description
        self.category = category  # appearance, consumable, upgrade, ability
        self.price = price  # 鑽石價格
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.is_permanent = is_permanent
        self.icon_color = icon_color
        self.purchased = False
        
    def can_purchase(self, engine):
        """檢查是否可購買"""
        if self.purchased and self.is_permanent:
            return False, "已擁有此物品"
        if not hasattr(engine, 'diamonds') or engine.diamonds < self.price:
            return False, f"鑽石不足 (需要{self.price}💎)"
        return True, ""
    
    def purchase(self, engine):
        """購買物品"""
        can_buy, reason = self.can_purchase(engine)
        if not can_buy:
            return False, reason
        
        engine.diamonds -= self.price
        
        if self.is_permanent:
            self.purchased = True
        
        self.apply_effect(engine)
        return True, f"成功購買 {self.name}"
    
    def apply_effect(self, engine):
        """應用效果"""
        if self.effect_type == "map_theme":
            engine.shop_items_owned['map_theme'] = self.effect_value
            
        elif self.effect_type == "villager_skin":
            engine.shop_items_owned['villager_skin'] = self.effect_value
            
        elif self.effect_type == "hero_effect":
            engine.shop_items_owned['hero_effect'] = self.effect_value
            
        elif self.effect_type == "speed_boost":
            if not hasattr(engine, 'active_buffs'):
                engine.active_buffs = {}
            engine.active_buffs['speed'] = {'value': self.effect_value, 'duration': 1}
            
        elif self.effect_type == "harvest_boost":
            if not hasattr(engine, 'active_buffs'):
                engine.active_buffs = {}
            engine.active_buffs['harvest'] = {'value': self.effect_value, 'duration': 1}
            
        elif self.effect_type == "wall_repair":
            engine.wall_hp += self.effect_value
            
        elif self.effect_type == "delay_beast":
            if hasattr(engine, 'beast_delay'):
                engine.beast_delay += self.effect_value
            else:
                engine.beast_delay = self.effect_value
                
        elif self.effect_type == "lucky_coin":
            if not hasattr(engine, 'active_buffs'):
                engine.active_buffs = {}
            engine.active_buffs['luck'] = {'value': 1, 'duration': 1}
            
        elif self.effect_type == "warehouse_upgrade":
            engine.shop_items_owned['warehouse'] = True
            
        elif self.effect_type == "wall_upgrade":
            engine.shop_items_owned['wall_upgrade'] = True
            engine.wall_hp += 100
            
        elif self.effect_type == "campfire_upgrade":
            engine.shop_items_owned['campfire'] = True
            
        elif self.effect_type == "watchtower":
            engine.shop_items_owned['watchtower'] = True
            engine.spawn_interval = max(20, int(engine.spawn_interval * 0.8))
            
        elif self.effect_type == "resource_magnet":
            engine.shop_items_owned['magnet'] = True
            
        elif self.effect_type == "time_freeze":
            engine.shop_items_owned['time_freeze'] = True
            
        elif self.effect_type == "group_heal":
            engine.shop_items_owned['group_heal'] = True

class Shop:
    """商店系統"""
    def __init__(self, engine):
        self.engine = engine
        self.items = []
        self.save_file = "shop_data.json"
        
        # 初始化已購買物品追蹤
        if not hasattr(engine, 'shop_items_owned'):
            engine.shop_items_owned = {
                'map_theme': 'default',
                'villager_skin': 'default',
                'hero_effect': 'none',
                'warehouse': False,
                'wall_upgrade': False,
                'campfire': False,
                'watchtower': False,
                'magnet': False,
                'time_freeze': False,
                'group_heal': False
            }
        
        self.init_items()
        self.load_purchases()
    
    def init_items(self):
        """初始化所有商品"""
        
        # === 外觀商店 ===
        
        # 地圖主題
        self.items.append(ShopItem(
            "map_desert", "沙漠主題", "將地圖變成金黃色沙漠",
            "appearance", 50, "map_theme", "desert", True, (255, 215, 100)
        ))
        
        self.items.append(ShopItem(
            "map_snow", "雪地主題", "將地圖變成白雪皚皚",
            "appearance", 50, "map_theme", "snow", True, (240, 248, 255)
        ))
        
        self.items.append(ShopItem(
            "map_forest", "深林主題", "將地圖變成深綠森林",
            "appearance", 50, "map_theme", "forest", True, (34, 100, 34)
        ))
        
        self.items.append(ShopItem(
            "map_lava", "岩漿主題", "將地圖變成紅黑岩漿地",
            "appearance", 100, "map_theme", "lava", True, (200, 50, 50)
        ))
        
        # 村民皮膚
        self.items.append(ShopItem(
            "skin_warrior", "武士服裝", "村民變成武士造型",
            "appearance", 80, "villager_skin", "warrior", True, (200, 50, 50)
        ))
        
        self.items.append(ShopItem(
            "skin_merchant", "商人服裝", "村民變成商人造型",
            "appearance", 80, "villager_skin", "merchant", True, (255, 215, 0)
        ))
        
        self.items.append(ShopItem(
            "skin_noble", "貴族服裝", "村民變成貴族造型",
            "appearance", 150, "villager_skin", "noble", True, (138, 43, 226)
        ))
        
        # 英雄特效
        self.items.append(ShopItem(
            "effect_fire", "火焰尾跡", "移動時留下火焰軌跡",
            "appearance", 100, "hero_effect", "fire", True, (255, 100, 0)
        ))
        
        self.items.append(ShopItem(
            "effect_lightning", "閃電特效", "移動時閃爍電光",
            "appearance", 100, "hero_effect", "lightning", True, (255, 255, 100)
        ))
        
        self.items.append(ShopItem(
            "effect_rainbow", "彩虹光環", "移動時散發彩虹光",
            "appearance", 150, "hero_effect", "rainbow", True, (255, 150, 255)
        ))
        
        # === 消耗品 ===
        
        self.items.append(ShopItem(
            "scroll_speed", "加速卷軸", "移動速度×1.5 (持續1天)",
            "consumable", 30, "speed_boost", 1.5, False, (100, 255, 255)
        ))
        
        self.items.append(ShopItem(
            "rune_harvest", "豐收符文", "資源收集×2 (持續1天)",
            "consumable", 40, "harvest_boost", 2.0, False, (100, 255, 100)
        ))
        
        self.items.append(ShopItem(
            "amulet_guard", "守護護符", "立即修復城牆200 HP",
            "consumable", 25, "wall_repair", 200, False, (200, 200, 200)
        ))
        
        self.items.append(ShopItem(
            "hourglass_time", "時光沙漏", "延遲野獸襲擊1天",
            "consumable", 60, "delay_beast", 1, False, (255, 215, 0)
        ))
        
        self.items.append(ShopItem(
            "coin_lucky", "幸運硬幣", "下個事件必定好結果",
            "consumable", 35, "lucky_coin", 1, False, (255, 215, 0)
        ))
        
        # === 建築升級 ===
        
        self.items.append(ShopItem(
            "upgrade_warehouse", "高級倉庫", "資源上限+50% (永久)",
            "upgrade", 120, "warehouse_upgrade", 1.5, True, (139, 69, 19)
        ))
        
        self.items.append(ShopItem(
            "upgrade_wall", "堅固城牆", "基礎HP+100 (永久)",
            "upgrade", 150, "wall_upgrade", 100, True, (150, 150, 150)
        ))
        
        self.items.append(ShopItem(
            "upgrade_campfire", "豪華營火", "飢餓速度-20% (永久)",
            "upgrade", 100, "campfire_upgrade", 0.8, True, (255, 100, 50)
        ))
        
        self.items.append(ShopItem(
            "upgrade_watchtower", "瞭望塔", "資源生成+20% (永久)",
            "upgrade", 180, "watchtower", 1.2, True, (100, 150, 200)
        ))
        
        # === 特殊能力 ===
        
        self.items.append(ShopItem(
            "ability_magnet", "資源磁鐵", "自動吸收附近資源 (永久)",
            "ability", 200, "resource_magnet", 50, True, (255, 215, 0)
        ))
        
        self.items.append(ShopItem(
            "ability_freeze", "時間凍結", "按[F]暫停3秒 (永久)",
            "ability", 250, "time_freeze", 3, True, (100, 200, 255)
        ))
        
        self.items.append(ShopItem(
            "ability_heal", "群體治療", "按[H]治療所有人 (永久)",
            "ability", 220, "group_heal", 50, True, (100, 255, 100)
        ))
    
    def save_purchases(self):
        """保存購買記錄"""
        data = {
            "purchased_items": [item.id for item in self.items if item.purchased],
            "owned_items": self.engine.shop_items_owned
        }
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存商店數據失敗: {e}")
    
    def load_purchases(self):
        """讀取購買記錄"""
        if not os.path.exists(self.save_file):
            return
        
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item_id in data.get("purchased_items", []):
                for item in self.items:
                    if item.id == item_id:
                        item.purchased = True
                        break
            
            owned = data.get("owned_items", {})
            self.engine.shop_items_owned.update(owned)
            
        except Exception as e:
            print(f"讀取商店數據失敗: {e}")
    
    def get_items_by_category(self, category=None):
        """按類別獲取商品"""
        if category is None:
            return self.items
        return [item for item in self.items if item.category == category]
    
    def show_shop_screen(self, screen, font, title_font):
        """顯示商店畫面"""
        selected_category = "全部"
        categories = ["全部", "外觀", "消耗品", "升級", "能力"]
        category_map = {
            "全部": None,
            "外觀": "appearance",
            "消耗品": "consumable",
            "升級": "upgrade",
            "能力": "ability"
        }
        category_index = 0
        scroll_offset = 0
        
        while True:
            screen.fill((15, 15, 25))
            cx = (screen.get_width()) // 2
            
            # 標題
            title = title_font.render("🏪 神秘商店", True, (255, 215, 0))
            screen.blit(title, (cx - title.get_width()//2, 20))
            
            # 鑽石顯示
            diamond_text = title_font.render(f"💎 {self.engine.diamonds} 鑽石", True, (100, 200, 255))
            screen.blit(diamond_text, (cx - diamond_text.get_width()//2, 70))
            
            # 類別選擇
            y = 120
            cat_text = font.render(f"類別: {selected_category}", True, (255, 255, 255))
            screen.blit(cat_text, (50, y))
            hint = font.render("[左右鍵切換]", True, (150, 150, 150))
            screen.blit(hint, (250, y))
            
            # 獲取當前類別商品
            items = self.get_items_by_category(category_map[selected_category])
            
            # 顯示商品列表
            y = 170
            max_display = 7
            start_idx = scroll_offset
            end_idx = min(start_idx + max_display, len(items))
            
            for i in range(start_idx, end_idx):
                item = items[i]
                box_y = y + (i - start_idx) * 75
                box_height = 70
                
                # 判斷是否可購買
                can_buy, reason = item.can_purchase(self.engine)
                
                # 背景色
                if item.purchased and item.is_permanent:
                    bg_color = (30, 50, 30)
                    border_color = (100, 200, 100)
                elif not can_buy:
                    bg_color = (40, 20, 20)
                    border_color = (100, 50, 50)
                else:
                    bg_color = (30, 30, 40)
                    border_color = item.icon_color
                
                pygame.draw.rect(screen, bg_color, (50, box_y, screen.get_width() - 100, box_height), 0, 5)
                pygame.draw.rect(screen, border_color, (50, box_y, screen.get_width() - 100, box_height), 2, 5)
                
                # 商品圖標
                pygame.draw.circle(screen, item.icon_color, (90, box_y + box_height//2), 25)
                
                # 商品名稱
                name = title_font.render(item.name, True, (255, 255, 255))
                screen.blit(name, (140, box_y + 5))
                
                # 描述
                desc = font.render(item.description, True, (200, 200, 200))
                screen.blit(desc, (140, box_y + 35))
                
                # 價格
                price_color = (100, 200, 255) if can_buy else (150, 150, 150)
                price_text = title_font.render(f"{item.price}💎", True, price_color)
                screen.blit(price_text, (screen.get_width() - 200, box_y + 15))
                
                # 狀態
                if item.purchased and item.is_permanent:
                    status = font.render("已擁有", True, (100, 255, 100))
                    screen.blit(status, (screen.get_width() - 200, box_y + 45))
                elif not can_buy:
                    status = font.render(reason, True, (255, 100, 100))
                    screen.blit(status, (screen.get_width() - 250, box_y + 45))
                else:
                    buy_hint = font.render(f"按[{i-start_idx+1}]購買", True, (150, 255, 150))
                    screen.blit(buy_hint, (screen.get_width() - 200, box_y + 45))
            
            # 滾動提示
            if len(items) > max_display:
                scroll_hint = font.render(f"[上下鍵滾動] {start_idx + 1}-{end_idx}/{len(items)}", True, (150, 150, 150))
                screen.blit(scroll_hint, (cx - scroll_hint.get_width()//2, screen.get_height() - 80))
            
            # 返回提示
            back_hint = font.render("按 [ESC] 返回", True, (150, 150, 150))
            screen.blit(back_hint, (cx - back_hint.get_width()//2, screen.get_height() - 40))
            
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
                        scroll_offset = min(len(items) - max_display, scroll_offset + 1) if len(items) > max_display else 0
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:
                        # 購買商品
                        index = event.key - pygame.K_1
                        if start_idx + index < end_idx:
                            item = items[start_idx + index]
                            success, message = item.purchase(self.engine)
                            if success:
                                self.save_purchases()
                                self.engine.show_notification(message, (100, 255, 100))
                            else:
                                self.engine.show_notification(message, (255, 100, 100))
