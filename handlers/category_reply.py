# category_reply.py
# 第二層：使用者點選「文青早點」「在地美食」「高檔餐廳」之後，回覆對應的料理類型選單
import logging

from linebot.v3.messaging.models import FlexMessage, FlexContainer, ReplyMessageRequest

logger = logging.getLogger(__name__)

# 定義 reply_categories 函數，用於回覆使用者選擇特定風格餐廳後的料理類型選單
# event: LINE 事件物件，包含 reply_token 等資訊
# messaging_api: MessagingApi 實例，用於發送回覆訊息
# user_text: 使用者輸入的文字，這裡代表選擇的風格類別 (例如 "文青早點", "在地美食", "高檔餐廳")
def reply_categories(event, messaging_api, user_text):
    logger.debug("進入 reply_categories 函式")  # ✅ 測試用，輸出進入函數的訊息

    # --- 定義「文青早點」風格的 Flex Message 氣泡卡片 JSON 結構 ---
    # 這個 JSON 字典描述了一個單一的 Flex Message 氣泡，用於展示「文青早點」的子類別按鈕 (台式傳統早餐、西式輕食早餐、健康營養早餐、異國風味早餐)
    bubble_hipster_breakfast = {
        "type": "bubble", # Flex Message 的根物件類型，這裡選擇 'bubble' (氣泡)
        "hero": { # 展示一張美食相關的圖片，讓選單更具視覺吸引力
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
                    "contents": [
                        # 使用列表生成式動態生成多個按鈕
                        {
                            "type": "button", # 按鈕類型
                            "style": "primary", # 按鈕樣式，'primary' 通常是實心按鈕
                            "action": {"type": "message", "label": label, "text": text},
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
    # 結構與「文青早點」類似，但內容和圖片針對「在地美食」進行了調整
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
                            "action": {"type": "message", "label": label, "text": text},
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
                            "action": {"type": "message", "label": label, "text": text},
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
    # 函數會檢查傳入的 user_text 參數（即使用者點擊按鈕後發送的文字），判斷使用者選擇了哪個大類別
    if user_text == "文青早點":
        # 建立一個 FlexMessage 物件，其內容是「文青早點」的氣泡卡片
        message = FlexMessage(
            alt_text="文青早點選單", # 替代文字，當 LINE 不支援 Flex Message 時顯示
            contents=FlexContainer.from_dict(bubble_hipster_breakfast) # 將 JSON 字典轉換為 LineBot SDK 能夠識別的 FlexContainer 物件
        )
    elif user_text == "在地美食":
        # 建立一個 FlexMessage 物件，其內容是「在地美食」的氣泡卡片
        message = FlexMessage(
            alt_text="在地美食選單",
            contents=FlexContainer.from_dict(bubble_local_food)
        )
    elif user_text == "高檔餐廳":
        # 建立一個 FlexMessage 物件，其內容是「高檔餐廳」的氣泡卡片
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