#第二層：使用者點選「文青早點」「在地美食」「高檔餐廳」之後，回覆對應的料理/餐廳類型選單
from linebot.v3.messaging.models import FlexMessage, FlexContainer, ReplyMessageRequest

def reply_categories(event, messaging_api, user_text): #category
    print("進入 reply_categories 函式")  # ✅ 測試用

    bubble_hipster_breakfast = {
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
            "contents": [
                {"type": "text", "text": "文青早點", "weight": "bold", "size": "xl"},
                {"type": "text", "text": "請選擇喜歡的料理類型：", "size": "sm", "margin": "md", "color": "#666666"},
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
                        for label, text in [
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
                {"type": "text", "text": "請選擇喜歡的料理類型：", "size": "sm", "margin": "md", "color": "#666666"},
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
                        for label, text in [
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
                {"type": "text", "text": "請選擇喜歡的料理類型：", "size": "sm", "margin": "md", "color": "#666666"},
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
                        for label, text in [
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
    '''
    bubbles = {
        "文青早點": bubble_hipster_breakfast,
        "在地美食": bubble_local_food,
        "高檔餐廳": bubble_fancy_restaurant
    }
    '''

    if user_text == "文青早點":
        message = FlexMessage(
            alt_text="文青早點選單",
            contents=FlexContainer.from_dict(bubble_hipster_breakfast)
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
    else:
        message = FlexMessage(text="請重新輸入『美食推薦』開始～")

    '''
    carousel_dict = {
        "type": "carousel",
        "contents": list(bubbles.values())  # ✅ 把三個 bubble dict 包成 carousel
    }
    '''
    '''
    flex_container = FlexContainer.from_dict(carousel_dict)

    message = FlexMessage(
        alt_text=f"{category}選單",
        contents=flex_container  # ✅ 傳入 dict，不用 FlexContainer.from_dict
    )
    '''
    '''
    message = FlexMessage(
        alt_text=f"{category}選單",
        contents=FlexContainer.from_dict(bubble_hipster_breakfast)  # ✅ 正確轉換方式
    )
    '''
    

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[message]
        )
    )

    '''
    if category not in bubbles:
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[FlexMessage(text="請重新輸入『美食推薦』開始～")]
            )
        )
        return
    '''