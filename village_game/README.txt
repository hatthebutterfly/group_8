Readme · MDCopy🏘️ Village Sim: 15 Days Challenge
一款生存策略遊戲，你需要帶領村莊在充滿危險的荒野中存活15天。管理資源、保護村民、應對隨機事件，最終獲得最高評級！
Show Image
Show Image
Show Image

📖 目錄

遊戲特色
遊戲截圖
安裝指南
遊戲玩法
遊戲系統
評分機制
文件結構
開發者指南
常見問題


✨ 遊戲特色
🎮 核心玩法

15天生存挑戰 - 在危機四伏的荒野中存活到第15天
5位可選英雄 - 每位英雄擁有獨特的被動能力
3種難度模式 - Normal / Hard / Hell，適合不同挑戰需求
完整評分系統 - 遊戲結束時根據表現給予S~F評級

🌟 遊戲系統

資源管理 - 收集糧食、木材、黃金三種資源
日夜循環 - 白天工作，夜晚野獸來襲
隨機事件 - 10+種隨機事件，每次遊玩都不同
村民AI - 智能尋路、自動收集、避免擁擠
城牆防禦 - 建造和維護城牆抵禦野獸
黑市商店 - 每5天可購買特殊物品

🎯 挑戰目標

🥉 入門 - 在Normal難度存活15天
🥈 進階 - 獲得A級以上評價
🥇 大師 - 在Hard難度零死亡通關
💎 傳說 - 在Hell難度獲得S級評價


🖼️ 遊戲截圖
[主選單]          [英雄選擇]        [遊戲畫面]
   |                  |                 |
   v                  v                 v
開始遊戲 → 選擇英雄 → 選擇難度 → 15天生存 → 評分畫面
遊戲界面說明

左側區域 - 遊戲地圖（960x720）
右側UI - 資源顯示、人口、城牆HP、日期、事件日誌


🚀 安裝指南
系統需求

Python 3.7 或更高版本
Pygame 2.0 或更高版本
作業系統：Windows / macOS / Linux

快速安裝
方法 1：使用 pip（推薦）
bash# 1. 安裝 Python（如果尚未安裝）
# 前往 https://www.python.org/downloads/

# 2. 安裝 Pygame
pip install pygame

# 3. 下載遊戲文件
# （將所有文件放在同一個資料夾）

# 4. 生成遊戲圖片資源
python create_assets.py

# 5. 啟動遊戲
python main.py
方法 2：使用虛擬環境（推薦給開發者）
bash# 1. 創建虛擬環境
python -m venv venv

# 2. 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安裝依賴
pip install pygame

# 4. 生成資源並運行
python create_assets.py
python main.py
首次運行
bash# 第一次運行前，務必先生成圖片資源
python create_assets.py
# 成功後會在 assets/ 資料夾生成 6 張圖片

# 然後啟動遊戲
python main.py

🎮 遊戲玩法
基本操作
鍵盤控制

WASD - 移動英雄角色
數字鍵 1-5 - 選擇英雄/難度/事件選項
ESC - 暫停遊戲 / 返回主選單
R - 重新開始（遊戲結束時）
任意鍵 - 繼續（事件/評分畫面）

遊戲目標

存活15天 - 這是勝利的唯一條件
保護村民 - 避免村民死於飢餓或野獸
管理資源 - 收集並善用糧食、木材、黃金
維護城牆 - 抵禦每晚的野獸襲擊
應對事件 - 在隨機事件中做出明智選擇

遊戲流程
主選單 → 英雄選擇 → 難度選擇 → 遊戲開始
   ↓
[第1天] 白天收集資源 → 夜晚野獸襲擊 → 每日結算
   ↓
[第2天] 白天收集資源 → 夜晚野獸襲擊 → 每日結算
   ↓
  ...（可能觸發隨機事件）
   ↓
[第5天] 黑市商人出現 → 購買物品
   ↓
  ...
   ↓
[第10天] 黑市商人出現 → 購買物品
   ↓
  ...
   ↓
[第15天] 勝利！ → 評分畫面 → 勝利畫面

🎯 遊戲系統
📊 資源系統
三種資源
資源顏色獲取方式用途🍎 糧食綠色地圖收集 / 事件餵養村民、事件消耗🪵 木材棕色地圖收集 / 事件修復城牆、事件消耗💰 黃金金色地圖收集 / 事件購買物品、事件消耗
資源生成

自動刷新 - 地圖上定期生成資源點
收集範圍 - 英雄30像素、村民15像素
資源價值 - 每個資源點 = 5單位

👥 人口系統
村民行為

白天 - 自動尋找並收集資源（木材 > 黃金 > 糧食）
夜晚 - 回到營火附近休息
飢餓 - 飢餓度>60時優先尋找食物，找到直接吃掉
AI避讓 - 自動避免與其他村民重疊

死亡條件

野獸襲擊時城牆已毀（60%機率）
特定事件選擇（如：野獸狩獵失敗）
地獄模式：一人死亡全體陣亡

🦁 野獸系統
夜間襲擊

攻擊時機 - 每天晚上（70%進度時）
傷害計算 - 基礎傷害 = 20 + (天數×5) + (天數²×0.8)
難度加成 - Hard ×1.3 / Hell ×1.5

防禦機制

有城牆 - 野獸優先攻擊城牆
無城牆 - 60%機率殺死一位村民
修復 - 可用木材修復（或選擇建築英雄）

🏰 城牆系統
城牆屬性

初始HP - 100
修復方式 -

手動：消耗木材（比例1:1）
自動：泰坦英雄每秒+2 HP
商店：購買神工匠（+400 HP）
事件：某些事件可修復



城牆狀態

HP > 200 - 🟢 堅固（綠色）
HP 100-200 - 🟡 普通（黃色）
HP < 100 - 🔴 危險（紅色）
HP = 0 - ⚫ 被摧毀（黑色）

🎲 事件系統
隨機事件（10種）

流亡難民 - 接納增加人口 / 拒絕無事
強盜勒索 - 給錢消災 / 拒絕賭運氣
流浪詩人 - 打賞修復城牆
雷暴來襲 - 花木材準備 / 賭運氣
神祕祭壇 - 獻祭食物換獎勵
野獸遷徙 - 冒險狩獵 / 躲避
瘋狂鍊金術士 - 喝藥賭效果
迷路的貴族 - 幫助獲回報 / 打劫
古代遺跡 - 探索找寶藏 / 封鎖
神祕流浪漢 - 購買藏寶圖

黑市商店（第5、10天）

大補給 - 15金 → +200糧食
建材包 - 20金 → +100木材
神工匠 - 25金 → +400城牆HP
命運盲盒 - 15金 → 隨機獎勵

👨‍🦰 英雄系統
5位可選英雄
英雄類型顏色被動能力適合玩法🏃 艾里奧Speed綠色移動速度×1.5快速掃蕩資源💰 摩根Tycoon金色每3秒產1金經濟流💊 芙蕾雅Healer粉色自動治療村民飢餓保護村民🛠️ 泰坦Builder灰色自動修復城牆防禦流🌾 瑟蕾絲Oracle橙色降低全體飢餓速度糧食節約
英雄特性

玩家控制 - WASD移動
更大收集範圍 - 30像素（村民15）
不會被野獸殺死 - 地獄模式除外

⚙️ 難度系統
難度飢餓速度資源生成野獸傷害特殊機制評分加成Normal0.05/幀45秒/次×1.0無×1.0Hard0.1/幀70秒/次×1.3資源-30%×1.5Hell0.15/幀100秒/次×1.5一人死亡全滅×2.0

🏆 評分機制
評分項目（9項）
項目分數範圍計算方式說明存活天數0-300天數×20（勝利=300）基礎分數資源儲備0-200(糧+木+金×5)÷2黃金價值高倖存人口0-150存活數×25保護村民死亡懲罰-∞~0死亡數×-10避免犧牲城牆防禦0-100城牆HP÷5防禦力野獸應對-100~0根據傷害懲罰防守表現事件參與0-∞事件數×5積極參與難度加成-×1.0/1.5/2.0挑戰獎勵勝利獎勵0/500通關=+500巨額獎勵
評級標準
評級分數要求稱號顏色難度建議S≥ 2000傳奇村長金色Hell完美通關A≥ 1500卓越領袖綠色Hard/Hell通關B≥ 1000稱職村長藍色Normal完美/Hard通關C≥ 600努力生存橙色Normal通關D≥ 300勉強及格灰色存活數天F< 300慘不忍睹紅色快速失敗
高分策略
🥇 S級攻略（2000+分）

選擇Hell難度（×2.0加成）
選擇泰坦（自動修牆）或芙蕾雅（保護村民）
零死亡通關（避免-10×n懲罰）
囤積黃金（×5價值）
保持城牆滿血（+100分）
勝利獎勵（+500分）

範例計算：
存活15天: 300
資源(糧100+木50+金30×5=300): 150
倖存7人: 175
死亡0人: 0
城牆500HP: 100
野獸應對: -40
事件10個: 50
─────────
基礎分: 735
×2.0難度: 1470
+勝利: 500
─────────
總分: 1970 (接近S級)

📁 文件結構
village-sim/
├── main.py              # 遊戲入口
├── engine.py            # 遊戲引擎核心
├── config.py            # 遊戲設定檔
├── create_assets.py     # 圖片資源生成器
├── font.ttf             # 遊戲字體（可選）
│
├── models/              # 遊戲模型
│   ├── __init__.py
│   ├── villager.py      # 村民系統
│   ├── hero.py          # 英雄系統
│   ├── resource.py      # 資源系統
│   └── event_system.py  # 事件系統
│
├── utils.py             # 工具函數
│
├── assets/              # 圖片資源（自動生成）
│   ├── hero.png
│   ├── villager.png
│   ├── food.png
│   ├── wood.png
│   ├── gold.png
│   └── wall.png
│
├── README.md            # 本文件
├── 評分系統說明.md      # 評分詳細說明
├── 更新日誌.md          # 版本更新記錄
└── 修改對照表.md        # 代碼修改對照
核心文件說明
main.py
python# 遊戲入口，負責啟動和錯誤處理
from engine import GameEngine
game = GameEngine()
game.run()
engine.py

遊戲主循環
資源管理
日夜循環
評分系統
畫面渲染

config.py
python# 可調整的遊戲參數
FPS = 60                    # 幀率
DAY_LENGTH = 1200           # 一天的幀數
HUNGER_RATE = 0.05          # 飢餓速度
INITIAL_MAP_WIDTH = 960     # 地圖寬度
INITIAL_MAP_HEIGHT = 720    # 地圖高度
models/villager.py

村民AI邏輯
資源收集
飢餓系統
日夜作息

models/hero.py

5位英雄的特殊能力
玩家控制邏輯

models/event_system.py

10種隨機事件
黑市商店
事件效果處理


👨‍💻 開發者指南
修改遊戲參數
調整難度
python# 在 config.py 修改
HUNGER_RATE = 0.05        # 降低=更簡單
DAY_LENGTH = 1200         # 增加=天更長
調整資源
python# 在 engine.py 的 reset_game_state()
self.food = 50            # 初始糧食
self.wood = 0             # 初始木材
self.gold = 0             # 初始黃金
self.wall_hp = 100        # 初始城牆
調整野獸傷害
python# 在 engine.py 的 process_night_phase()
base_dmg = 20 + (self.day * 5) + growth
# 降低係數可減少傷害
添加新英雄
python# 在 models/hero.py

class NewHero(PlayerHero):
    def __init__(self, engine, name):
        super().__init__(engine, name, (255, 0, 0), "Hero")  # 紅色
        self.speed = 1.2
        
    def update(self):
        self.update_movement()  # 玩家控制
        
        # 你的特殊能力
        if self.engine.frame_count % 60 == 0:
            # 每秒執行一次
            pass
添加新事件
python# 在 models/event_system.py 的 trigger_random_event()

events = [
    # ... 現有事件
    {
        "title": "你的事件名稱",
        "desc": "事件描述",
        "options": [
            {
                "text": "選項1描述",
                "cost": {"gold": 10},  # 消耗
                "effect": "your_effect_name"
            },
            {
                "text": "選項2描述",
                "cost": {},
                "effect": "none"
            }
        ]
    }
]

# 然後在 apply_effect() 添加效果
elif effect == "your_effect_name":
    self.engine.food += 100
    self.set_result(True, "成功", "獲得了食物！")
修改評分規則
python# 在 engine.py 的 calculate_score()

# 調整權重
survival_score = min(300, self.day * 30)  # 每天30分
population_score = living_count * 50      # 每人50分

# 調整評級門檻
def get_rank(self, score):
    if score >= 2500:  # 提高S級門檻
        return "S", (255, 215, 0), "傳奇村長"
調試技巧
python# 在 engine.py 添加調試模式
DEBUG_MODE = True

if DEBUG_MODE:
    self.food = 9999
    self.gold = 9999
    self.wall_hp = 9999
    
# 快速測試15天
config.DAY_LENGTH = 120  # 減少到原本的1/10

❓ 常見問題
安裝問題
Q: 無法安裝 Pygame？
bash# Windows 用戶如果pip安裝失敗，試試：
python -m pip install --upgrade pip
python -m pip install pygame

# macOS 用戶可能需要：
pip3 install pygame

# Linux 用戶可能需要額外安裝：
sudo apt-get install python3-pygame
Q: 運行時出現 "No module named 'pygame'"？
bash# 確認 Pygame 已安裝
pip list | grep pygame

# 如果沒有，重新安裝
pip install pygame
Q: 缺少圖片資源？
bash# 執行資源生成器
python create_assets.py

# 應該會看到：
# 成功！已在 assets 資料夾產生 6 張圖片。
遊戲問題
Q: 村民全部餓死怎麼辦？

優先收集糧食（綠色圓點）
選擇瑟蕾絲（Oracle）降低飢餓速度
白天主動用英雄收集資源

Q: 城牆一直被打破？

多收集木材修復
選擇泰坦（Builder）自動修牆
第5天/第10天購買神工匠（+400 HP）

Q: 如何獲得S級評價？

必須在Hell難度完成（×2.0加成）
零死亡（避免-10×n懲罰）
囤積黃金（×5價值）
保持高城牆HP
參考「高分策略」章節

Q: 事件選擇哪個好？

有黃金就買（投資未來）
沒錢選保守選項
難民事件建議接納（+2人）
危險事件（如狩獵）視情況

技術問題
Q: 遊戲太卡？
python# 在 config.py 降低幀率
FPS = 30  # 從60降到30
Q: 字體顯示錯誤？
python# 如果沒有 font.ttf，遊戲會自動使用系統字體
# 或者下載字體放到遊戲目錄
Q: 如何關閉評分系統？
python# 在 engine.py 註解這兩行：
# self.show_score_screen(victory=False)  # game_over_screen
# self.show_score_screen(victory=True)   # game_won_screen
Q: 修改代碼後沒效果？
python# 確保修改的是正確文件
# Python 會緩存，可以刪除 __pycache__ 資料夾
rm -rf __pycache__ models/__pycache__

🎓 遊戲技巧
新手教學
第1-3天：建立基礎

選擇簡單英雄（摩根或泰坦）
瘋狂收集糧食（保證村民不餓）
收集木材修復城牆到200+
避免冒險事件

第4-7天：穩定發展

保持糧食>100
城牆維持在150+
開始囤積黃金（準備購物）
第5天購買神工匠或大補給

第8-12天：中期挑戰

野獸傷害變高，重視城牆
適度參與事件（有閒錢才冒險）
第10天再次購物
保持人口穩定

第13-15天：衝刺階段

確保城牆HP充足
糧食儲備>150
小心選擇事件（避免翻車）
倒數3天穩扎穩打

進階技巧
速通攻略（艾里奧）

利用超高速度瘋狂掃地圖
黃金優先（×5評分價值）
城牆靠購買維持

防守流（泰坦）

自動修牆，安心收集資源
木材可以賣換黃金（透過事件）
適合穩健玩家

經濟流（摩根）

黃金自動產出，有錢買一切
第5天/第10天大採購
適合喜歡購物的玩家

保姆流（芙蕾雅）

自動治療，村民不會餓死
適合接納難民玩法
人口優勢（每人25分）

糧食流（瑟蕾絲）

全體飢餓減半，糧食消耗低
可以多囤其他資源
適合資源管理型玩家

Hell難度生存指南
⚠️ 一人死亡全體陣亡！

絕對不能死人

城牆時刻保持200+ HP
第5天必買神工匠
糧食>200隨時備用


避免高風險事件

野獸狩獵 - ❌ 不要選
古代遺跡 - ❌ 風險高
流浪詩人 - ✅ 可以選（修牆）
流亡難民 - ⚠️ 謹慎（人多難養）


英雄選擇

首選：泰坦（自動修牆）
次選：芙蕾雅（保護村民）
避免：艾里奧（速度無法保證防禦）


資源分配

木材>黃金>糧食
每晚檢查城牆
黃金全部用於防禦


🔄 版本歷史
v1.1.0 (2025-12-29)

✨ 新增完整評分系統（S~F評級）
✨ 新增9項評分指標
✨ 新增評分明細畫面
🐛 修復地獄模式團滅計數問題
📝 完善文檔和說明
  
v1.0.0 (2025-12)

🎉 初始版本發布
✨ 5位英雄系統
✨ 3種難度模式
✨ 10種隨機事件
✨ 完整的日夜循環
✨ 野獸襲擊系統
✨ 黑市商店系統




📜 授權協議
本項目採用 MIT 授權協議。
MIT License

Copyright (c) 2025 Village Sim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

🙏 致謝

Pygame - 優秀的遊戲開發框架
Python - 簡潔優雅的程式語言

📞 聯繫方式
  
問題回報 - 透過 GitHub Issues
功能建議 - 歡迎提交 Pull Request
討論交流 - 歡迎在社群分享遊玩心得


🎮 開始遊玩
準備好了嗎？現在就開始你的15天生存挑戰！
bashpython main.py
祝你遊戲愉快，挑戰S級評價！ 🏆✨

最後更新：2025年12月29日 
