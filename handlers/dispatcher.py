# dispatcher.py
# 根據 user_text 來呼叫對應處理函數
import logging
from typing import Optional

from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent, FollowEvent

from handlers.menu_reply import reply_menu
from handlers.category_reply import reply_categories
from handlers.region_reply import reply_region_selector
from handlers.restaurant_carousel_reply import reply_food_by_type_and_region
from handlers.store_detail_reply import reply_store_detail

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FOOD_TYPES = [
    "台式傳統早餐", "西式輕食早餐", "健康營養早餐", "異國風味早餐",
    "必吃便當", "美味熱炒", "經典飯麵", "特色小吃",
    "火鍋盛宴", "西式精選", "創意料理", "自助饗宴"
]

REGIONS = ["西區", "北區", "南屯區"]

# ---------------------------------------------------------------------------
# Dispatcher public API
# ---------------------------------------------------------------------------

def dispatch_event(event: MessageEvent, messaging_api: MessagingApi) -> None:
    """Entry point called from app.py.

    Routes only text messages; other event types are ignored.
    """
    if not isinstance(event.message, TextMessageContent):
        logger.debug("忽略非文字訊息事件: %s", event)
        return

    user_text: str = event.message.text.strip()
    logger.info("使用者傳來：%s", user_text)
    logger.debug("user_text 長度=%d, ASCII=%s", len(user_text), [ord(c) for c in user_text])

    # Attempt to split "類型-區" 格式
    category: Optional[str] = None
    district: Optional[str] = None
    if "-" in user_text:
        category, district = user_text.split("-", 1)
        logger.debug("split → category=%s, district=%s", category, district)

    try:
        # 1. 第五層:店家詳細資訊（地址/電話/評價）
        if user_text.endswith("的地址") or user_text.endswith("的電話") or user_text.endswith("的評價"):
            reply_store_detail(user_text, event, messaging_api)
            return

        # 2. 第四層:依美食類型與區域回覆店家輪播
        if district and category in FOOD_TYPES:
            reply_food_by_type_and_region(category, district, event, messaging_api)
            return

        # 3. 第一層:主選單
        if user_text == "美食推薦":
            reply_menu(event, messaging_api)
            return

        # 4. 第二層:類別 → 子分類
        if user_text in ["文青早點", "在地美食", "高檔餐廳"]:
            reply_categories(event, messaging_api, user_text)
            return

        # 5. 第三層:單一美食類型 → 選地區
        if user_text in FOOD_TYPES:
            reply_region_selector(user_text, event, messaging_api)
            return

        # 6. fallback
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="請點選選單或輸入正確的格式")]
            )
        )

    except Exception:  # noqa: BLE001
        logger.exception("調度事件時出現意外錯誤")
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="處理您的請求時發生錯誤，請稍後再試或確認輸入格式。")]
            )
        )