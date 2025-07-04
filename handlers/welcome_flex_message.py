# welcome_flex_message
from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import (
    FlexMessage, ReplyMessageRequest, FlexContainer
)
from linebot.v3.webhooks.models import FollowEvent

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


def reply_welcome(event: FollowEvent, messaging_api: MessagingApi) -> None:
    """使用者第一次把 Bot 加為好友時的自動回覆。"""
    flex_msg = get_welcome_flex_message()

    messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token, # 每個事件都有一個唯一的 reply_token，用於回覆該事件
                messages=[flex_msg] # 回覆的訊息內容，必須是一個訊息物件的list (即使只有一個)
            )
        )