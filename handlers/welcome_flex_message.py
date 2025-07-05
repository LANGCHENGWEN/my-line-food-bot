# welcome_flex_message.py
"""
好友加入 Bot 時的歡迎訊息：
- 建立簡易歡迎 Flex Bubble，提示使用關鍵字「美食推薦」。
- 由 reply_welcome() 在 FollowEvent 觸發時呼叫。
"""
# --- 匯入套件 ---
from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import (
    FlexMessage, ReplyMessageRequest, FlexContainer
)
from linebot.v3.webhooks.models import FollowEvent

# --- 定義 get_welcome_flex_message 函式，用於回覆歡迎訊息 ---
def get_welcome_flex_message() -> dict:
    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🎉 歡迎加入美食推薦小幫手",
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "輸入「美食推薦」就可以幫你找好吃的哦 😋",
                    "size": "md",
                    "wrap": True,
                    "margin": "md"
                }
            ]
        }
    }
    return FlexMessage(
        alt_text="歡迎訊息",
        contents=FlexContainer.from_dict(bubble)
    )

# --- 對外 API : reply_welcome ---
def reply_welcome(event: FollowEvent, messaging_api: MessagingApi) -> None:
    """
    使用者第一次把 Bot 加為好友時的自動回覆。
    FollowEvent 觸發時調用：
    - 取得 FlexMessage
    - 使用 Reply API 回覆
    """
    flex_msg = get_welcome_flex_message()

    messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, # 每個事件都有一個唯一的 reply_token，用於回覆該事件
                messages=[flex_msg] # 回覆的訊息內容，必須是一個訊息物件的list (即使只有一個)
            )
        )