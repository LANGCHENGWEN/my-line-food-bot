# category_reply.py
"""
提供『美食推薦』第二層流程：
- 當使用者在第一層選單點選「文青早點／在地美食／高檔餐廳」時，由本模組回覆對應料理類型的 Flex Message 選單。
- 將視覺化選單與邏輯封裝在同一個函式，方便其他 handler 直接呼叫。
"""
# --- 套件與 Logger 初始化 ---
import logging
from linebot.v3.messaging.models import FlexMessage, FlexContainer, ReplyMessageRequest

logger = logging.getLogger(__name__)

# --- 定義 reply_categories 函式，用於回覆使用者選擇特定風格餐廳後的料理類型選單 ---
def reply_categories(event, messaging_api, user_text):
    """
    依據使用者點選的『風格類別』(user_text) 回覆對應的料理子類別選單。
    event：  LINE Webhook 事件，包含 reply_token。
    messaging_api： MessagingApi 物件，用於發送回覆訊息。
    user_text： 字串，代表使用者當前選定的風格主類別 (例如 "文青早點", "在地美食", "高檔餐廳")。
    """
    logger.debug("進入 reply_categories 函式")  # 協助追蹤流程

    # --- 定義「文青早點」風格的 Flex Message 氣泡卡片 JSON 結構 ---
    """
    使用一致的氣泡結構：hero 圖片 + body 文字 + 多顆按鈕。
    按鈕 action 採 message，讓使用者點擊後再次觸發文字事件，方便後續第三層邏輯串接。
    """
    bubble_hipster_breakfast = {
        "type": "bubble", # Flex Message 的根物件類型，這裡選擇 'bubble' (氣泡)
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/SQt91q6x/image.jpg",
            "size": "full",
            "aspectRatio": "20:13", # 圖片的長寬比
            "aspectMode": "cover" # 圖片的顯示模式，'cover' 表示圖片會被裁切以填滿區域
        },
        "body": { # 包含標題 ("文青早點") 和提示文字 ("請選擇喜歡的料理類型：")，引導使用者進行選擇
            "type": "box", # 容器類型，'box' 可以包含多個內容物件
            "layout": "vertical", # 佈局方向，'vertical' 表示內容垂直排列
            "contents": [ # 主體內的內容列表
                {"type": "text","text": "文青早點", "weight": "bold", "size": "xl"},
                {"type": "text", "text": "請選擇喜歡的料理類型：", "size": "md", "margin": "md", "color": "#666666"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md", # 上邊距
                    "spacing": "sm", # 內容之間的間距
                    "contents": [ # 使用列表生成式動態生成多個按鈕
                        {
                            "type": "button", # 按鈕類型
                            "style": "primary", # 按鈕樣式，'primary' 是實心按鈕
                            "action": {"type": "message", "label": label, "text": text}
                        }
                        for label, text in [ # 這裡定義了「文青早點」下的四個子類別按鈕
                            ("🍳台式傳統早餐", "台式傳統早餐"),
                            ("🥪西式輕食早餐", "西式輕食早餐"),
                            ("🥗健康營養早餐", "健康營養早餐"),
                            ("🌮異國風味早餐", "異國風味早餐")
                        ]
                    ]
                }
            ]
        }
    }

    # --- 定義「在地美食」風格的 Flex Message 氣泡卡片 JSON 結構 ---
    # 結構同上；僅替換標題、圖片與按鈕文字。
    bubble_local_food = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/wTymSP2c/image.jpg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "在地美食", "weight": "bold", "size": "xl"},
                {"type": "text", "text": "請選擇喜歡的料理類型：", "size": "md", "margin": "md", "color": "#666666"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {"type": "message", "label": label, "text": text}
                        }
                        for label, text in [ # 這裡定義了「在地美食」下的四個子類別按鈕
                            ("🍱必吃便當", "必吃便當"),
                            ("🥘美味熱炒", "美味熱炒"),
                            ("🍜經典飯麵", "經典飯麵"),
                            ("🍢特色小吃", "特色小吃")
                        ]
                    ]
                }
            ]
        }
    }

    # --- 定義「高檔餐廳」風格的 Flex Message 氣泡卡片 JSON 結構 ---
    # 結構與前兩個類似，內容和圖片針對「高檔餐廳」進行了調整
    bubble_fancy_restaurant = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/4ND9Z5FC/image.jpg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "高檔餐廳", "weight": "bold", "size": "xl"},
                {"type": "text", "text": "請選擇喜歡的料理類型：", "size": "md", "margin": "md", "color": "#666666"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {"type": "message", "label": label, "text": text}
                        }
                        for label, text in [ # 這裡定義了「高檔餐廳」下的四個子類別按鈕
                            ("🍲火鍋盛宴", "火鍋盛宴"),
                            ("🍝西式精選", "西式精選"),
                            ("🍛創意料理", "創意料理"),
                            ("🍣自助饗宴", "自助饗宴")
                        ]
                    ]
                }
            ]
        }
    }

    # --- 根據 user_text (使用者選擇的類別) 決定要回覆哪個 Flex Message ---
    # 函數會檢查傳入的 user_text 參數（使用者點擊按鈕後發送的文字），判斷使用者選擇了哪個主類別
    if user_text == "文青早點":
        message = FlexMessage(
            alt_text="文青早點選單", # 替代文字，當 LINE 不支援 Flex Message 時顯示
            contents=FlexContainer.from_dict(bubble_hipster_breakfast)
            # 將 JSON 字典轉換為 LineBot SDK 能夠識別的 FlexContainer 物件
        )
    elif user_text == "在地美食":
        message = FlexMessage(
            alt_text="在地美食選單",
            contents=FlexContainer.from_dict(bubble_local_food)
        )
    elif user_text == "高檔餐廳":
        message = FlexMessage(
            alt_text="高檔餐廳選單",
            contents=FlexContainer.from_dict(bubble_fancy_restaurant)
        )
    else: # 如果 user_text 不匹配任何預期的類別，回覆一個簡單的文字訊息提示使用者
        message = FlexMessage(text="請重新輸入『美食推薦』開始～")
    
    # --- 回覆訊息給使用者 ---
    # 使用 messaging_api 回覆訊息
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token, # 每個事件都有一個唯一的 reply_token，用於回覆該事件
            messages=[message] # 回覆的訊息內容，必須是一個訊息物件的list (即使只有一個)
        )
    )