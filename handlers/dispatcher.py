# dispatcher.py
"""
集中事件路由：
- 接收 main.py 傳入的 MessageEvent。
- 根據使用者輸入文字決定呼叫哪一層 handler。
- 將 UI / 業務處理分散到 handlers 目錄，保持單一職責。
"""
# --- 套件與處理器匯入 ---
import logging
from typing import Optional

from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent

from handlers.menu_reply import reply_menu
from handlers.category_reply import reply_categories
from handlers.region_reply import reply_region_selector
from handlers.restaurant_carousel_reply import reply_food_by_type_and_region
from handlers.store_detail_reply import reply_store_detail

logger = logging.getLogger(__name__)

# --- 常數：快速集中維護 ---
FOOD_TYPES = [
    "台式傳統早餐", "西式輕食早餐", "健康營養早餐", "異國風味早餐",
    "必吃便當", "美味熱炒", "經典飯麵", "特色小吃",
    "火鍋盛宴", "西式精選", "創意料理", "自助饗宴"
]

REGIONS = ["西區", "北區", "南屯區"]

# --- 對外 API：dispatch_event() ---
def dispatch_event(event: MessageEvent, messaging_api: MessagingApi) -> None:
    """
    從 main.py 呼叫的入口點。
    任何 MessageEvent 進入此函式，由條件判斷決定下一步應回覆的邏輯層。
    若為非文字事件則直接忽略。
    """
    # 前置檢查：是否為文字訊息
    if not isinstance(event.message, TextMessageContent):
        logger.debug("忽略非文字訊息事件: %s", event)
        return

    # 取出並標準化使用者文字
    user_text: str = event.message.text.strip()
    logger.info("使用者傳來：%s", user_text)
    logger.debug("user_text 長度=%d, ASCII=%s", len(user_text), [ord(c) for c in user_text])

    # 若符合 "類型-區域" 格式，事先分割
    category: Optional[str] = None
    district: Optional[str] = None
    if "-" in user_text:
        category, district = user_text.split("-", 1)
        logger.debug("分割 → 類別=%s, 區域=%s", category, district)

    # 依優先順序進行事件分派
    try:
        # 1. 第五層 : 店家詳細資訊（地址/電話/評價）
        if user_text.endswith("的地址") or user_text.endswith("的電話") or user_text.endswith("的評論"):
            reply_store_detail(user_text, event, messaging_api)
            return

        # 2. 第四層 : 依美食類型與區域回覆店家輪播
        if district and category in FOOD_TYPES:
            reply_food_by_type_and_region(category, district, event, messaging_api)
            return

        # 3. 第一層 : 主選單觸發
        if user_text == "美食推薦":
            reply_menu(event, messaging_api)
            return

        # 4. 第二層 : 主類別 → 回覆子類別選單
        if user_text in ["文青早點", "在地美食", "高檔餐廳"]:
            reply_categories(event, messaging_api, user_text)
            return

        # 5. 第三層 : 單一美食類型 → 區域選擇
        if user_text in FOOD_TYPES:
            reply_region_selector(user_text, REGIONS, event, messaging_api)
            return

        # 6. Fallback : 皆不符合時回覆提示
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="請點選選單或輸入正確的格式")]
            )
        )

    # --- 全域例外攔截 ---
    # 避免因未捕捉錯誤導致 webhook 超時；同時回覆友善訊息
    except Exception:
        logger.exception("調度事件時出現意外錯誤")
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="處理您的請求時發生錯誤😥，請稍候再試或確認輸入格式。")]
            )
        )