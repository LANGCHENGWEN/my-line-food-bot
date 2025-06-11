# 第三層：使用者點選某個料理之後，顯示地區選單，然後顯示對應的 CarouselTemplate
from linebot.v3.messaging.models import (
    ReplyMessageRequest, FlexMessage, FlexContainer
)

def reply_region_carousel(category, regions): #event, messaging_api
    # category 可能為 "台式傳統早餐", "西式輕食早餐", "健康營養早餐", "異國風味早餐", "必吃便當", "美味熱炒", "經典飯麵", "特色小吃", "火鍋盛宴", "西式精選", "創意料理", "自助饗宴"
    # 接著要回覆地區選單，不同料理對應不同地區按鈕文字
    bubbles = []

    for region in regions:
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": region,
                        "weight": "bold",
                        "size": "xl"
                    },
                    {
                        "type": "text",
                        "text": f"看看{region}有哪些 {category}！",
                        "wrap": True
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "message",
                            "label": "查看",
                            "text": f"{category}-{region}"
                        }
                    }
                ]
            }
        }
        bubbles.append(bubble)

    return {
        "type": "carousel",
        "contents": bubbles
    }

    '''
    if not columns:
        messaging_api.reply_message(
            reply_token=event.reply_token,
            messages=[TextMessage(text="找不到地區，請重新選擇。")]
        )
        return
    '''
    
    message = FlexMessage(
        alt_text="請選擇地區",
        contents=FlexContainer.from_dict(bubble_region_carousel)
    )
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[message] # message 是 TextMessage 或 FlexMessage 物件
        )
    )


    '''
    if selection in ["吐司", "蛋餅", "貝果"]:
        buttons_template = ButtonsTemplate(
            title=f'你選擇 {selection}',
            text='請選擇你所在的區域~',
            actions=[
                MessageAction(label="大安區", text=f"{selection}_大安區"),
                MessageAction(label="中山區", text=f"{selection}_中山區"),
                MessageAction(label="信義區", text=f"{selection}_信義區")
            ]
        )
        message = TemplateSendMessage(
            alt_text="請選擇你所在的區域~", template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, message)

    elif "_" in selection:
        # 進到選擇地區之後，selection 例如 "吐司_大安區"
        food, region = selection.split("_")
        # 根據 food 和 region，產生 Carousel
        carousel_columns = []
        # 簡單篩選出 restaurant_info 中符合條件的店家（示範：名稱包含 food 且 region）
        for name, info in restaurant_info.items():
            # 這邊假設資料庫裡沒放 region，但用 name 或其他方式對應，
            # 為簡化示例，直接把「吐司」相關放在 key 中
            if food in ["吐司", "牛肉麵", "法式餐廳"]:
                # 將大安區店家放到輪播上
                # 以 restaurant_info 中已有的資料
                # 你可以用更精確比對條件
                if (food == "吐司" and region == "大安區" and name in ["吐司男", "早安公雞"]) or \
                   (food == "牛肉麵" and region == "中山區" and name in ["好味道牛肉麵", "阿義牛肉麵"]) or \
                   (food == "法式餐廳" and region == "信義區" and name in ["法蘭西餐桌", "高級饗宴"]):
                    carousel_columns.append(
                        CarouselColumn(
                            thumbnail_image_url=info["圖片"],
                            title=name,
                            text=info["評價"],
                            actions=[
                                MessageAction(label="地址", text=f"{name} 地址"),
                                MessageAction(label="電話", text=f"{name} 電話"),
                                MessageAction(label="評價", text=f"{name} 評價")
                            ]
                        )
                    )
        # 如果沒有符合的店家，回覆文字
        if not carousel_columns:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="目前該區域暫無店家，請重新選擇。"))
            return
        carousel_template = CarouselTemplate(columns=carousel_columns)
        message = TemplateSendMessage(
            alt_text=f"{region}{food}推薦", template=carousel_template
        )
        line_bot_api.reply_message(event.reply_token, message)
    else:
        # 非預期格式
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請重新輸入"))
'''