# restaurant_carousel_reply.py
"""
第四層流程：
- 當使用者選擇「料理類型‑區域」後，回覆對應店家清單 (最多 10 筆) 的 Flex Carousel。
- 每家店家顯示名稱、營業時間與 3 顆按鈕：查看資訊 / Google 地圖 / 分享店家。
"""
# --- 匯入套件與 Logger ---
import logging
import urllib.parse
import pandas as pd

from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import (
    TextMessage, FlexMessage, FlexContainer, ReplyMessageRequest
)
from linebot.v3.webhooks.models import MessageEvent

from handlers.data_loader import query_by_category_and_district

logger = logging.getLogger(__name__)

# --- 定義 create_flex_message_by_category_and_district 函式，用於回覆店家輪播 ---
def create_flex_message_by_category_and_district(category: str, district: str):
    # 1. 取資料
    df = query_by_category_and_district(category, district)

    if df.empty:
        logger.info(f"找不到 %s 的 %s 店家 😥", district, category)
        return None # 找不到店家時，回傳 None

    # 2. 組 Bubble
    # --- 將前 10 筆資料轉換成 Flex Bubble，組合成 Carousel 並回傳 FlexMessage ---
    bubbles = []
    for _, row in df.head(10).iterrows(): # 限制最多 10 筆 (Carousel 上限)
        store_name = str(row["店名"])
        address = row.get("地址", "")

        # 建立 Google Maps 連結：店名 + 地址
        maps_q = urllib.parse.quote_plus(store_name if not address else f"{store_name} {address}")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_q}"
        
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://i.postimg.cc/SQt91q6x/image.jpg",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": store_name[:40],
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": f'營業時間:{str(row["營業時間"])[:60]}' if pd.notna(row["營業時間"]) else "營業時間:無營業時間資料",
                        "size": "md",
                        "color": "#666666",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "postback",
                                    "label": "查看資訊",
                                    "data": f"action=view_info&shop_id={urllib.parse.quote(store_name)}",
                                    "displayText": "查看資訊"
                                }
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "uri",
                                    "label": "開啟地圖",
                                    "uri": maps_url
                                }
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "postback",
                                    "label": "分享店家",
                                    "data": f"action=share_shop&shop_name={urllib.parse.quote(store_name)}",
                                    "displayText": f"分享店家"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        bubbles.append(bubble)

    # 3. 若無 bubble 就回 None
    if not bubbles:
        logger.info(f"無法建立 Flex Message for %s-%s，bubbles 為空", category, district)
        return None

    # 4. 回傳 FlexMessage 物件，內容是 Carousel
    return FlexMessage(
        alt_text=f"{district} 的 {category} 推薦店家",
        contents=FlexContainer.from_dict({"type": "carousel", "contents": bubbles})
    )

# --- 對外 API : reply_food_by_type_and_region() ---
# 由 dispatcher.py 呼叫：若有 FlexMessage → 回覆；若無結果 → 回覆文字提醒
def reply_food_by_type_and_region(
    category: str, district: str, event: MessageEvent, api: MessagingApi
) -> None:
    """依美食類型與區域回覆店家輪播 (Flex Message)。"""
    carousel = create_flex_message_by_category_and_district(category, district)

    if carousel is None:
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="目前找不到符合條件的店家喔！")],
            )
        )
        logger.debug("類型=%s 區域=%s 找不到店家", category, district)
    else:
        api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[carousel])
        )
        logger.debug("已回覆 Carousel for %s-%s", category, district)