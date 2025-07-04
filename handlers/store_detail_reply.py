# store_detail_reply.py
# 第五層: 回覆店家地址 / 電話 / 評價 (Flex Message)
import logging
from typing import Dict, Optional

from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import (
    TextMessage, FlexMessage,
    FlexContainer, ReplyMessageRequest
)
from linebot.v3.webhooks.models import MessageEvent

from handlers.data_loader import get_store_info_by_name

logger = logging.getLogger(__name__)

def build_store_detail_flex(
    store_name: str, store_info: Dict[str, str]
) -> FlexMessage:
    """建立店家詳細資訊的 Flex Message。"""
    address = store_info.get("地址", "未知")
    phone = store_info.get("電話", "未知")
    rating = store_info.get("評價", "未知")

    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": store_name,
                    "weight": "bold",
                    "size": "xl",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": f"📍 地址：{address}",
                    "wrap": True,
                    "size": "md"
                },
                {
                    "type": "text",
                    "text": f"📞 電話：{phone}",
                    "wrap": True,
                    "size": "md"
                },
                {
                    "type": "text",
                    "text": f"⭐ 評價：{rating}",
                    "wrap": True,
                    "size": "md"
                },
            ],
        },
    }

    return FlexMessage(
        alt_text=f"{store_name} 詳細資訊",
        contents=FlexContainer.from_dict(bubble)
    )

def reply_store_detail(user_text: str, event: MessageEvent, api: MessagingApi) -> None:
    """回覆店家地址 / 電話 / 評價 (Flex Message)。"""
    if user_text.endswith("的地址"):
        store_name = user_text.replace("的地址", "").strip()
        field = "地址"
    elif user_text.endswith("的電話"):
        store_name = user_text.replace("的電話", "").strip()
        field = "電話"
    else:
        store_name = user_text.replace("的評價", "").strip()
        field = "評價"

    store_info: Optional[dict] = get_store_info_by_name(store_name)
    if not store_info:
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"抱歉，找不到 {store_name}{field} 的資訊。")]
            )
        )
        logger.debug("找不到店家：%s", store_name)
        return

    flex_msg = build_store_detail_flex(store_name, store_info)
    api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_msg])
    )
    logger.debug("已回覆店家資訊 detail (Flex): %s", store_name)