# store_detail_reply.py
"""
第五層流程：
- 解析『店名 + (地址|電話|評價)』文字指令。
- 回覆對應欄位的店家詳細資訊 Flex Message。
- 若 CSV 無該店家，回覆友善文字提示。
"""
# --- 匯入套件與 Logger ---
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

# --- 定義 build_store_detail_flex 函式，用於回覆店家地址 / 電話 / 評價 ---
def build_store_detail_flex(
    store_name: str, store_info: Dict[str, str]) -> FlexMessage:
    """建立店家詳細資訊的 Flex Message。"""
    address = store_info.get("地址", "未知")
    phone = store_info.get("電話", "未知")
    rating = store_info.get("評論", "未知")

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
                    "text": f"⭐ 評論：{rating}",
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

# --- 對外 API : reply_store_detail ---
# 判斷使用者文字結尾『的地址/電話/評價』→ 擷取店名 → 查資料
# 若找到 → 回覆 Flex；若無 → 文字提示
def reply_store_detail(user_text: str, event: MessageEvent, api: MessagingApi) -> None:
    """根據文字指令回覆店家地址 / 電話 / 評價 (Flex Message)。"""
    # 1. 解析指令
    if user_text.endswith("的地址"):
        store_name = user_text.replace("的地址", "").strip()
        field = "地址"
    elif user_text.endswith("的電話"):
        store_name = user_text.replace("的電話", "").strip()
        field = "電話"
    else:
        store_name = user_text.replace("的評論", "").strip()
        field = "評論"

    # 2. 查詢資料
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

    # 3. 回覆 Flex Message
    flex_msg = build_store_detail_flex(store_name, store_info)
    api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_msg])
    )
    logger.debug("已回覆店家資訊 detail (Flex): %s", store_name)