# 第一層：當使用者輸入「美食推薦」時，顯示分類選單
from linebot.v3.messaging.models import FlexMessage, FlexContainer, ReplyMessageRequest

def reply_menu(event, messaging_api):
    print("進入 reply_menu() 函式")  # ✅ 測試用
    flex_json = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/ZKHKhbB3/309915.jpg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "美食小幫手上線!",
                    "weight": "bold",
                    "size": "xl",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "請選擇想要推薦的風格餐廳：",
                    "margin": "md",
                    "wrap": True,
                    "size": "sm"
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
                        "label": "享用文青早點",
                        "text": "文青早點"
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

    flex_message = FlexMessage(
        alt_text="請選擇想要推薦的風格餐廳：",
        contents=FlexContainer.from_dict(flex_json)  # ✅ 正確轉換方式
    )
    
    print("準備呼叫 reply_message")

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[flex_message]  # 必須為 list
        )
    )

    print("已呼叫 reply_message")


    '''
        title='美食小幫手上線!',
        text='請選擇想要推薦的風格餐廳：',
        actions=[
            MessageAction(label="享用文青早點", text="文青早點"),
            MessageAction(label="品嘗在地美食", text="在地美食"),
            MessageAction(label="暢享高檔餐廳", text="高檔餐廳")
        ]
    )
    '''