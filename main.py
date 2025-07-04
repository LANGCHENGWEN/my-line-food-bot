import logging
import urllib.parse
from collections import defaultdict
from flask import Flask, request, abort, jsonify

from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks.models import (
    MessageEvent, TextMessageContent, PostbackEvent, FollowEvent
)
from linebot.v3.exceptions import InvalidSignatureError

from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from handlers.welcome_flex_message import reply_welcome
from handlers.dispatcher import dispatch_event
from handlers.postback_handler import handle_postback_event

logger = logging.getLogger(__name__)

# --- Flask 應用程式初始化 ---
app = Flask(__name__)
# 驗證訊息來源: 使用 WebhookHandler 驗證 X-Line-Signature，確保訊息確實來自 LINE，防止偽造
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- LINE Messaging API 設定 ---
# 建立 Configuration 實例，設定 LINE Channel Access Token
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

# 建立 ApiClient 和 MessagingApi 實例
# ApiClient 用於發送 HTTP 請求到 LINE API
# MessagingApi 提供與 LINE Messaging API 互動的方法 (例如回覆訊息)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

user_favorites = {}

# --- Webhook 回調端點 ---
# 接收 LINE 訊息 (Webhook): LINE 平台會將使用者發送的訊息以 POST 請求的形式傳送到 /callback 端點
@app.route("/callback", methods=['POST'])
def callback():
    # 取得 LINE 傳來的 X-Line-Signature HTTP Header，用於驗證訊息來源
    signature = request.headers.get('X-Line-Signature')

    # 取得請求的原始 request body 內容 (JSON 格式的事件數據)
    body = request.get_data(as_text=True)  # body = request.get_json(force=True)
    logger.info("[Webhook 收到訊息] body= %s", body) # 輸出收到的訊息 body 到控制台，方便除錯

    '''
    events = body.get("events", [])
    for event in events:
        # 只處理 postback 事件
        if event["type"] == "postback":
            data = event["postback"]["data"]
            user_id = event["source"]["userId"]
            logger.info(f"收到 postback data: {data}，來自 user: {user_id}")
    return "OK"
    '''

    try:
        # 使用 handler 處理收到的 body 和 signature
        # 解析訊息事件: handler.handle() 會解析 JSON 格式的訊息內容，並觸發對應的事件處理函數 (例如 handle_message)
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("LINE 簽名無效 - 請求被拒絕")
        # 如果簽章無效，表示訊息可能不是來自 LINE 平台或被篡改，返回 400 錯誤
        abort(400)
    except Exception as e:
        # 處理其他可能發生的異常，例如處理邏輯中的錯誤
        logger.error("[處理時發生錯誤] %s", e, exc_info=True) # 輸出錯誤信息
        abort(500) # 返回 500 錯誤表示請求處理失敗

    # 成功處理後返回一個 JSON 響應，表示狀態為 "ok"
    return jsonify({"status": "ok"})

# 註冊 FollowEvent 處理器
@handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    logger.info(f"[FollowEvent] {event.source.user_id} 加入好友")
    reply_welcome(event, messaging_api)

# --- 訊息事件處理器 ---
# 使用 handler.add 裝飾器，將 handle_message 函數註冊為 TextMessageContent 類型的 MessageEvent 處理器
# 當 LINE 傳來文字訊息時，此函數會被調用
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        dispatch_event(event, messaging_api)
    except Exception:
        logger.exception("調度程序處理事件時出錯")

@handler.add(PostbackEvent)
def on_postback(event):
    handle_postback_event(event, messaging_api)

# --- 應用程式啟動點 ---
if __name__ == "__main__":
    app.run(port=5000, debug=True)
    # 當直接運行此腳本時，啟動 Flask 應用程式
    # port=5000: 應用程式將在 5000 端口上運行
    # debug=True: 開啟除錯模式，當程式碼有變動時會自動重載，並提供更詳細的錯誤信息 (建議在生產環境關閉)