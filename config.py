import os

# 存放 LINE Bot 的 Channel Secret 和 Channel Access Token
LINE_CHANNEL_SECRET = os.getenv('868d181b90b6fb1068aa76ae2659c86d') #你的 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('HHPG9NfX+/9HNeAhMdq/w3yNiqM6nZBmT1pZc4EmzfyXqOugaxSkc6GP91vGfEBxsPZvU3tKcjvorkUXLyJmb5 p/2HSxnZVe9xvFNulueHXjCKnvvAqAVTeib9cW/K7mr2HYywP7oD8EuWhLKoeQxQdB04t89/1O/w1cDnyilFU=') #你的 Channel Access Token

if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    print("警告：LINE_CHANNEL_SECRET 或 LINE_CHANNEL_ACCESS_TOKEN 未設定為環境變數！")
    # 可以在這裡加入一個 sys.exit() 或者使用你喜歡的方式處理錯誤
    # sys.exit("請設定 LINE Channel 環境變數！")