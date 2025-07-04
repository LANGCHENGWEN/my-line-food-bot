# restaurant_carousel_reply.py
# 第四層：依美食類型與區域回覆店家輪播 (Flex Message)
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

def create_flex_message_by_category_and_district(category: str, district: str):
    df = query_by_category_and_district(category, district)

    if df.empty:
        # **修改點 1: 當找不到店家時，回傳 None**
        # 讓調用此函數的地方（handle_message）來決定回覆文字訊息
        logger.info(f"找不到 %s 的 %s 店家 😥", district, category)
        return None
        #return TextMessage(text=f"找不到 {district} 的 {category} 店家 😥")

    bubbles = []
    '''
    for i, row in filtered.iterrows():
        if i >= 10:
            break  # Carousel 最多10筆
    '''

    # **修改點：使用計數器來限制 bubble 數量**
    # 確保只取前 10 個結果來建立 bubble
    for _, row in df.head(10).iterrows(): # 直接使用 .head(10) 來取得前 10 筆資料
        store_name = str(row["店名"])
        address = row.get("地址", "")
        maps_q = urllib.parse.quote_plus(store_name if not address else f"{store_name} {address}")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_q}"
        
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://i.postimg.cc/SQt91q6x/image.jpg",  # 可改為每家店不同圖片
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
    '''
    flex_message = {
        "type": "carousel",
        "contents": bubbles
    }
    '''

    # **額外檢查：如果 bubbles 最終是空的，也返回 None**
    # 這樣在 app.py 中會回覆「目前找不到符合條件的店家喔！」
    if not bubbles:
        logger.info(f"無法建立 Flex Message for %s-%s，bubbles 為空", category, district)
        return None

    # **修改點 2: 直接回傳 FlexMessage 物件，內容是 Carousel**
    # 這裡的 FlexMessage 構造已經是正確的，不需要再額外包裝一層 dictionary
    return FlexMessage(
        alt_text=f"{district} 的 {category} 推薦店家",
        contents=FlexContainer.from_dict({"type": "carousel", "contents": bubbles})
    )

def reply_food_by_type_and_region(
    category: str, district: str,
    event: MessageEvent, api: MessagingApi
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

    '''
    return TemplateMessage(
        alt_text=f"{district} 的 {category} 推薦美食",
        template=CarouselTemplate(columns=columns)
    )
    '''


'''
from linebot.models import TextSendMessage
from data.restaurant_data import restaurant_info

def reply_restaurant_detail(event, line_bot_api, user_text):
    # user_text 可能為："吐司男 地址", "早安公雞 電話", "好味道牛肉麵 評價" 等
    for name, info in restaurant_info.items():
        if name in user_text:
            if "地址" in user_text:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=info["地址"])
                )
                return
            elif "電話" in user_text:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=info["電話"])
                )
                return
            elif "評價" in user_text:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=info["評價"])
                )
                return
    # 如果沒有匹配到，回覆預設
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="找不到該店家或指令，請重新選擇。")
    )
'''