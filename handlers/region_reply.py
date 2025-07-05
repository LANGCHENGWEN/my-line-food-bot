# region_reply.py
"""
第三層流程：
- 當使用者選定某『料理類型』後，顯示區域選擇輪播 (Carousel)。
- 讓使用者點擊區域按鈕，進入第四層「料理類型‑區域 → 店家列表」。
"""
# --- 匯入套件與 Logger ---
import logging

from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import (
    FlexMessage, FlexContainer, ReplyMessageRequest
)
from linebot.v3.webhooks.models import MessageEvent

logger = logging.getLogger(__name__)

# --- 定義 reply_region_carousel 函式，用於回覆使用者選擇特定料理類型後的區域選單 ---
def reply_region_carousel(category, regions):
    """
    函式接收 category (料理類型) 和 regions (可選區域列表) 作為輸入。
    每個區域會顯示為一個獨立的氣泡 (bubble)。
    """
    bubbles = [] # 初始化一個空列表，用於存放每個區域的 Flex Message 氣泡 JSON 字典

    # --- 遍歷每個區域，動態創建一個 Flex Message 氣泡 ---
    for region in regions:
        bubble = {
            "type": "bubble", # Flex Message 的根物件類型，這裡選擇 'bubble' (氣泡)
            "body": {
                "type": "box", # 容器類型，'box' 可以包含多個內容物件
                "layout": "vertical", # 佈局方向，'vertical' 表示內容垂直排列
                "spacing": "md", # 內容之間的間距
                "contents": [
                    # 使用列表動態生成多個按鈕
                    {
                        "type": "text",
                        "text": region, # 顯示區域名稱，作為標題
                        "weight": "bold", # 文字粗細，'bold' 表示粗體
                        "size": "xl"
                    },
                    {
                        "type": "text",
                        "text": f"看看{region}有哪些 {category}！", # 提示文字，結合區域和料理類型
                        "wrap": True # 是否自動換行
                    }
                ]
            },
            "footer": { # 氣泡的底部區塊，放置按鈕
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button", # 按鈕類型
                        "style": "primary", # 按鈕樣式，'primary' 是實心按鈕
                        "action": { # 按鈕點擊後觸發的動作
                            "type": "message", # 動作類型，'message' 表示發送文字訊息
                            "label": "查看", # 按鈕上顯示的文字
                            "text": f"{category}-{region}" # 點擊按鈕後實際發送的文字訊息內容
                        }
                    }
                ]
            }
        }
        bubbles.append(bubble) # 將創建好的氣泡 JSON 字典添加到列表中

    # --- 返回 Flex Carousel 的 JSON 結構 ---
    # 這個函式的最終目的是構建並返回整個 Carousel 結構，而不是直接發送
    # 主程式會接收這個 JSON 結構，然後將其轉換為 FlexMessage 物件並發送
    return {
        "type": "carousel", # Flex Message 的類型為 'carousel' (輪播)
        "contents": bubbles # 輪播的內容，即前面創建的氣泡列表
    }

# --- 對外 API：reply_region_selector() ---
# 直接回覆 Flex Carousel 給使用者。
def reply_region_selector(food_type: str, regions, event: MessageEvent, api: MessagingApi) -> None:
    """顯示區域 Carousel 供使用者選擇。"""
    carousel_json = reply_region_carousel(food_type, regions)
    flex_msg = FlexMessage(
        alt_text="請選擇區域",
        contents=FlexContainer.from_dict(carousel_json)
    )
    api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[flex_msg])
    )
    logger.debug("區域選單已送出 for %s", food_type)