# config.py
# 這個檔案用來存放應用程式的配置設定
import os
import sys
import logging
from dotenv import load_dotenv # 如果你使用 .env 檔案來管理環境變數，請加上這行
from logging.handlers import RotatingFileHandler

# 載入 .env 檔案中的環境變數 (如果存在且使用 dotenv)
# 確保你的 .env 檔案在 config.py 或你的主要執行檔 (test_app3.py) 同一層目錄下
load_dotenv()

LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE",  "main.log")

# 把字串轉成 logging 模組用的數字等級，找不到就退回 INFO
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)

def setup_logging() -> None:
    """Configure root logger once."""
    root = logging.getLogger()
    if root.handlers:          # 避免重複設定
        return

    root.setLevel(LOG_LEVEL)

    fmt = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # console # 由環境變數主控，預設 INFO
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # rotating file
    fh = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.DEBUG)  # 設定檔案日誌的等級為 DEBUG
    fh.setFormatter(fmt)
    root.addHandler(fh)

setup_logging()
logger = logging.getLogger(__name__)

# 存放 LINE Bot 的 Channel Secret 和 Chan# 從環境變數中獲取 LINE_CHANNEL_SECRET
# 從環境變數中獲取 LINE_CHANNEL_SECRET
# 如果環境變數不存在，os.getenv() 會返回 None
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET') #你的 Channel Secret

# 從環境變數中獲取 LINE_CHANNEL_ACCESS_TOKEN
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN') #你的 Channel Access Token

# 進行檢查，如果變數為 None，則發出警告並終止程式
if LINE_CHANNEL_SECRET is None:
    logger.error("環境變數 LINE_CHANNEL_SECRET 未設定。請確認已設定並重新啟動程式。")
    # 可以選擇在這裡 raise Exception 或 sys.exit()，讓程式明確停止
    # import sys
    # sys.exit(1)
if LINE_CHANNEL_ACCESS_TOKEN is None:
    logger.error("環境變數 LINE_CHANNEL_ACCESS_TOKEN 未設定。請確認已設定並重新啟動程式。")
    # import sys
    # sys.exit(1)