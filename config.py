# config.py
# 這個檔案用來存放應用程式的配置設定
import os
import sys
import logging
from dotenv import load_dotenv # 透過 .env 檔案管理環境變數
from logging.handlers import RotatingFileHandler
# 當日誌檔案達到一定大小或數量時，會自動進行輪替

# --- 載入 .env 檔案中的環境變數 ---
# load_dotenv() 會搜尋並讀取同層或父層的 .env，將其轉為系統環境變數，之後可用 os.getenv() 取得
load_dotenv()

# --- 日誌等級與檔案名稱設定 ---
# 從環境變數讀取 LOG_LEVEL 與 LOG_FILE，預設值為 "INFO" 與 "main.log"
LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE",  "main.log")

# 把字串轉成 logging 模組用的數字等級，找不到就退回 INFO
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)

# --- 建立全域 Logger 設定函式 ---
def setup_logging() -> None:
    """
    這段將所有日誌輸出邏輯集中到一個地方：
    避免在多個檔案重複撰寫 handler 與 formatter。
    只要呼叫一次即可，全專案共享相同設定。
    """
    root = logging.getLogger() # 為整個應用程式配置一次根日誌器，方便集中管理日誌和全域配置
    if root.handlers:       # 若已經設定過 Handler，則直接返回，避免重複設定
        return

    root.setLevel(LOG_LEVEL) # 設定根日誌器的最低日誌等級

    # 共用的格式：時間 - logger 名稱 - 等級 - 訊息
    fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # console : 適合在開發或部署到雲端查看，預設 INFO
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # rotating file：記錄更完整的 DEBUG 資訊到檔案，可追蹤歷史
    if os.getenv("ENABLE_FILE_LOG", "False").lower() == "true":
        fh = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        root.addHandler(fh)

setup_logging() # 呼叫函式以初始化 logging
logger = logging.getLogger(__name__) # 供其他模組引用此檔案時使用的預設 logger

# --- 讀取 LINE Bot 憑證 ---
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# --- 基本檢查：若缺少憑證則顯示錯誤 ---
# 如果變數為 None，則發出警告並終止程式
if LINE_CHANNEL_SECRET is None:
    logger.error("環境變數 LINE_CHANNEL_SECRET 未設定。請確認已設定並重新啟動程式。")

if LINE_CHANNEL_ACCESS_TOKEN is None:
    logger.error("環境變數 LINE_CHANNEL_ACCESS_TOKEN 未設定。請確認已設定並重新啟動程式。")