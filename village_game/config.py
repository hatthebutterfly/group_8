# config.py

# --- 視窗與地圖 ---
INITIAL_MAP_WIDTH = 800
INITIAL_MAP_HEIGHT = 600
MAX_MAP_WIDTH = 1600
MAX_MAP_HEIGHT = 1000
UI_WIDTH = 250       

# --- 顏色 (R, G, B) ---
COLOR_BG = (30, 30, 30)
COLOR_MAP = (34, 139, 34)       # 草地綠
COLOR_UI = (50, 50, 50)         # UI 背景
COLOR_TEXT = (255, 255, 255)
COLOR_BORDER = (20, 100, 20)

# 資源顏色
COLOR_FOOD = (0, 255, 0)        # 綠色
COLOR_WOOD = (139, 69, 19)      # 木頭褐
COLOR_GOLD = (255, 215, 0)      # 金色
COLOR_DEATH = (100, 100, 100)   # 屍體灰

# --- 遊戲平衡參數 ---
FPS = 60
DAY_LENGTH = 600      # 600幀 = 1天
HUNGER_RATE = 0.1     # 基礎飢餓速率

# --- 資源與繁榮度 ---
FOOD_NUTRITION = 30   # 食物補多少飽食度
WOOD_VALUE = 5        # 木頭增加繁榮度
GOLD_VALUE = 50       # 黃金增加繁榮度

PROSPERITY_THRESHOLD = 300 # 召喚英雄的初始門檻
MAX_HEROES = 5             # 英雄上限

# --- 字體設定 ---
FONT_FILE = "font.ttf"
