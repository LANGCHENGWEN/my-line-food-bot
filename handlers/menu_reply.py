# menu_reply.py
"""
『美食推薦』第一層入口選單：
- 當使用者輸入「美食推薦」時，顯示三大風格分類按鈕。
- 以 Flex Message 氣泡形式建構，包含圖片、標題、描述與三個按鈕的互動式選單。
- 將 UI 組裝集中在此函式，方便未來替換圖像或文字。
"""
# --- 套件與 Logger ---
import logging
from linebot.v3.messaging.models import (
    FlexMessage, FlexContainer, ReplyMessageRequest
)

logger = logging.getLogger(__name__)

# --- 定義 reply_menu 函式，用於回覆使用者主選單 ---
def reply_menu(event, messaging_api):
    """
    event：  LINE Webhook 事件，包含 reply_token。
    messaging_api： MessagingApi 物件，用於發送回覆訊息。
    """
    logger.debug("進入 reply_menu() 函式") # 協助追蹤流程

    # --- 定義 Flex Message 氣泡卡片 JSON 結構 ---
    """
    使用一致的氣泡結構：hero 圖片 + body 文字 + 多顆按鈕。
    按鈕 action 採 message，讓使用者點擊後再次觸發文字事件，方便後續第二層邏輯串接。
    """
    flex_json = {
        "type": "bubble", # Flex Message 的根物件類型，這裡選擇 'bubble' (氣泡)
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/ZKHKhbB3/309915.jpg",
            "size": "full",
            "aspectRatio": "20:13", # 圖片的長寬比
            "aspectMode": "cover" # 圖片的顯示模式，'cover' 表示圖片會被裁切以填滿區域
        },
        "body": { # 包含標題 ("美食小幫手上線!") 和提示文字 ("請選擇想要推薦的風格餐廳：")，引導使用者進行選擇
            "type": "box", # 容器類型，'box' 可以包含多個內容物件
            "layout": "vertical", # 佈局方向，'vertical' 表示內容垂直排列
            "contents": [ # 主體內的內容列表
                {
                    "type": "text", # 文字類型
                    "text": "美食小幫手上線!",
                    "weight": "bold", # 文字粗細，'bold' 表示粗體
                    "size": "xl",
                    "wrap": True # 是否自動換行
                },
                {
                    "type": "text",
                    "text": "請選擇想要推薦的風格餐廳：",
                    "margin": "md", # 上邊距
                    "wrap": True,
                    "size": "md"
                }
            ]
        },
        "footer": { # 放置了三個按鈕，分別是 "享用文青早點"、"品嘗在地美食"、"暢享高檔餐廳"
            "type": "box",
            "layout": "vertical",
            "spacing": "sm", # 內容之間的間距
            "contents": [ # 底部內的內容列表 (這裡是按鈕)
                {
                    "type": "button", # 按鈕類型
                    "style": "primary", # 按鈕樣式，'primary' 是實心按鈕
                    "action": { # 按鈕點擊後觸發的動作
                        "type": "message", # 動作類型，'message' 表示發送文字訊息
                        "label": "享用文青早點", # 按鈕上顯示的文字
                        "text": "文青早點" # 點擊按鈕後實際發送的文字訊息內容
                    }
                },
                {
                    "type": "button",
                    "style": "primary",
                    "action": {
                        "type": "message",
                        "label": "品嘗在地美食",
                        "text": "在地美食"
                    }
                },
                {
                    "type": "button",
                    "style": "primary",
                    "action": {
                        "type": "message",
                        "label": "暢享高檔餐廳",
                        "text": "高檔餐廳"
                    }
                }
            ]
        }
    }

    # --- 建立 FlexMessage 物件 ---
    # 將定義好的 JSON 字典轉換為 LineBot SDK 的 FlexMessage 物件
    flex_message = FlexMessage(
        alt_text="請選擇想要推薦的風格餐廳：", # 當使用者環境不支援 Flex Message 時顯示的替代文字
        contents=FlexContainer.from_dict(flex_json)  # 正確轉換方式：將 JSON 字典轉換為 FlexContainer 物件
    )

    logger.debug("準備呼叫 reply_message")

    # --- 回覆訊息給使用者 ---
    # 使用 messaging_api 回覆訊息
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token, # 每個事件都有一個唯一的 reply_token，用於回覆該事件
            messages=[flex_message]  # 回覆的訊息內容，必須是一個訊息物件的list (即使只有一個)
        )
    )

    logger.debug("已呼叫 reply_message")