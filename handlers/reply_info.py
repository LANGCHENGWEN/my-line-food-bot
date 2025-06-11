# 第四層：處理點擊 CarouselTemplate 中按鈕後，回覆餐廳詳細資訊（地址 / 電話 / 評價）
import pandas as pd
from linebot.v3.messaging.models import FlexMessage, FlexContainer #TextMessage

def create_flex_message_by_category_and_district(category, district, csv_file="台中美食推薦.csv"):
    df = pd.read_csv(csv_file, encoding='utf-8') #csv_file="台中美食推薦.csv"

    # 去除欄位名稱空白（很重要）
    df.columns = df.columns.str.strip()

    # 印出欄位名稱幫助除錯（可選）
    print("CSV 欄位名稱：", df.columns.tolist())
    
    '''
    df = pd.read_csv("台中美食推薦.csv", encoding='utf-8')
    print(df[(df["類型"] == "台式傳統早餐") & (df["區域"] == "北區")])
    '''

    # 過濾同時符合類型與區域
    if "類型" not in df.columns or "區域" not in df.columns:
        # 建議這裡直接返回 None 或拋出特定錯誤，讓調用者處理
        print("錯誤：CSV 缺少必要欄位（類型 或 區域）")
        raise ValueError("CSV 缺少必要欄位（類型 或 區域）")

    filtered = df[(df["類型"] == category) & (df["區域"] == district)]

    if filtered.empty:
        # **修改點 1: 當找不到店家時，回傳 None**
        # 讓調用此函數的地方（handle_message）來決定回覆文字訊息
        print(f"找不到 {district} 的 {category} 店家 😥")
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
    for index, row in filtered.head(10).iterrows(): # 直接使用 .head(10) 來取得前 10 筆資料
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
                        "text": str(row["店名"])[:40],
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": f'營業時間:{str(row["營業時間"])[:60]}' if pd.notna(row["營業時間"]) else "營業時間:無營業時間資料",
                        "size": "sm",
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
                                    "type": "message",
                                    "label": "地址",
                                    "text": f"{str(row['店名'])}的地址" # <-- 將這裡修改為更簡潔的問句
                                }
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "電話",
                                    "text": f"{str(row['店名'])}的電話"
                                }
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "評價",
                                    "text": f"{str(row['店名'])}的評價"
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
        print(f"雖然有資料，但無法建立 Flex Message for {district} 的 {category} 店家。")
        return None

    # **修改點 2: 直接回傳 FlexMessage 物件，內容是 Carousel**
    # 這裡的 FlexMessage 構造已經是正確的，不需要再額外包裝一層 dictionary
    return FlexMessage(
        alt_text=f"{district} 的 {category} 推薦店家",
        contents=FlexContainer.from_dict({
            "type": "carousel",
            "contents": bubbles
        })
    )

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