# main.py
# 主程式
# Flask 與 WebhookHandler 初始化
# 只在主程式設定 @handler.add() 裝飾器，把事件分派到 dispatcher.py 和 postback_handler.py
import logging # 引入日誌模組，方便除錯與追蹤
from flask import Flask, request, abort, jsonify # 建置 webhook 的 HTTP 伺服器

# Line Bot SDK——Messaging API 與 Webhook 驗章/事件
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks.models import (
    MessageEvent, TextMessageContent, PostbackEvent, FollowEvent
)
from linebot.v3.exceptions import InvalidSignatureError # 驗證失敗時會用到

# 自訂的設定與各種業務邏輯 handler
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from handlers.welcome_flex_message import reply_welcome # 首次加入好友歡迎訊息
from handlers.dispatcher import dispatch_event # 文字訊息總調度
from handlers.postback_handler import handle_postback_event # postback 事件處理

logger = logging.getLogger(__name__)

# --- Flask 與 WebhookHandler 初始化 ---
app = Flask(__name__) # 建立 Flask 應用，供 LINE Webhook 呼叫
handler = WebhookHandler(LINE_CHANNEL_SECRET)
# WebhookHandler 會驗證 X-Line-Signature，確保請求真正來自 LINE 平台

# --- 建立 LINE Messaging API 用戶端 ---
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
# 建立 Configuration 實例

# --- 建立 ApiClient 和 MessagingApi 實例 ---
api_client = ApiClient(configuration) # ApiClient 用於發送 HTTP 請求到 LINE API
messaging_api = MessagingApi(api_client) # 提供 reply_message / push_message 等方法

# --- Webhook 入口 ---
@app.route("/callback", methods=['POST'])
def callback():
    """
    LINE 平台會把所有事件 (文字、貼圖、追蹤、退追蹤 …) 以 POST 請求的形式傳送到 /callback 端點。

    1. 先抓 `X-Line-Signature` 進行「防偽」驗證
    2. 驗證通過後交給 `handler.handle()` 解析 JSON 並分派到對應的 `handler.add` 裝飾器 (FollowEvent / MessageEvent / PostbackEvent …)。
    """
    # 取得 LINE 傳來的 X-Line-Signature HTTP Header，用於驗證訊息來源
    signature = request.headers.get('X-Line-Signature')

    # 取得請求的原始 request body 內容 (JSON 格式的事件數據)
    body = request.get_data(as_text=True)
    logger.info("[Webhook 收到訊息] body= %s", body)

    try:
        # 使用 handler 處理收到的 body 和 signature
        # 解析訊息事件: handler.handle() 會解析 JSON 格式的訊息內容，並觸發對應的事件處理函式
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.warning("LINE 簽名無效 - 請求被拒絕")
        # 如果簽章無效，表示訊息可能不是來自 LINE 平台或被篡改，返回 400 錯誤
        abort(400)
    except Exception as e:
        # 處理其他可能發生的異常，例如處理邏輯中的錯誤
        logger.error("[處理時發生錯誤] %s", e, exc_info=True)
        abort(500) # 返回 500 錯誤表示請求處理失敗

    return jsonify({"status": "ok"}) # 200 OK 回應，告訴 LINE 已成功接收

# --- FollowEvent：使用者把 Bot 加為好友 ---
@handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    """
    使用者第一次「加好友」或「解除封鎖後重新開啟」會觸發。
    這裡只做兩件事：
      1. Log 使用者 ID，方便日後 debug 或行銷分析
      2. 回傳一個歡迎 Flex Message（封裝在 handlers.welcome_flex_message）
    """
    logger.info(f"[FollowEvent] {event.source.user_id} 加入好友")
    reply_welcome(event, messaging_api)

# --- 文字訊息 (MessageEvent + Text) → 交給 dispatcher.py 分流 ---
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """
    任何文字訊息都走這裡，再交由 dispatcher.py 決定要回覆哪一個事件。
    分層好處： main.py 只負責「收→丟」，商業邏輯集中在 dispatcher.py。
    """
    try:
        dispatch_event(event, messaging_api)
    except Exception:
        logger.exception("調度程序處理事件時出錯")

# --- Postback 事件 : 不會模擬使用者輸入 ---
@handler.add(PostbackEvent)
def on_postback(event):
    """
    任何 postback data (action=xxx&...) 都進來這裡，再交給 postback_handler.py 去解析 data 字串做事情。
    """
    handle_postback_event(event, messaging_api)

# --- 應用程式啟動點 (僅在直接執行 python main.py 時啟動) ---
if __name__ == "__main__":
    app.run(port=5000, debug=True)
    """
    port=5000：應用程式將在 5000 端口上運行
    debug=True：開啟除錯模式，當程式碼有變動時會自動重載，並提供更詳細的錯誤信息
    """