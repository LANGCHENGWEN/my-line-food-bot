import os
from dotenv import load_dotenv # 如果你使用 .env 檔案來管理環境變數，請加上這行

# 載入 .env 檔案中的環境變數 (如果存在且使用 dotenv)
# 確保你的 .env 檔案在 config.py 或你的主要執行檔 (test_app3.py) 同一層目錄下
load_dotenv()

# 存放 LINE Bot 的 Channel Secret 和 Chan# 從環境變數中獲取 LINE_CHANNEL_SECRET
# 從環境變數中獲取 LINE_CHANNEL_SECRET
# 如果環境變數不存在，os.getenv() 會返回 None
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET') #你的 Channel Secret

# 從環境變數中獲取 LINE_CHANNEL_ACCESS_TOKEN
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN') #你的 Channel Access Token

# 進行檢查，如果變數為 None，則發出警告並終止程式
if LINE_CHANNEL_SECRET is None:
    print("錯誤：環境變數 LINE_CHANNEL_SECRET 未設定。請確認已設定並重新啟動程式。")
    # 可以選擇在這裡 raise Exception 或 sys.exit()，讓程式明確停止
    # import sys
    # sys.exit(1)
if LINE_CHANNEL_ACCESS_TOKEN is None:
    print("錯誤：環境變數 LINE_CHANNEL_ACCESS_TOKEN 未設定。請確認已設定並重新啟動程式。")
    # import sys
    # sys.exit(1)

# 你可以在這裡添加更多配置變數
# EXAMPLE_VARIABLE = os.getenv('EXAMPLE_VARIABLE', '預設值')