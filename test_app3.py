from flask import Flask, request, abort, jsonify
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest, FlexMessage, FlexContainer # ✅ 用這個回覆文字
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from handlers import menu_handler, reply_categories, region_handler
from handlers.reply_info import create_flex_message_by_category_and_district
from handlers.data_loader import get_store_info_by_name
import traceback

app = Flask(__name__)
#parser = WebhookParser(LINE_CHANNEL_SECRET)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 建立 Configuration 實例
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

# 建立 ApiClient 和 MessagingApi 實例
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)

@app.route("/callback", methods=['POST'])
def callback():
    # 取得 LINE 傳來的 signature
    signature = request.headers.get('X-Line-Signature')

    # 取得 request body 內容
    body = request.get_data(as_text=True)
    print("[Webhook 收到訊息] body=", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print("[處理時發生錯誤]", e)
        abort(400)

    return jsonify({"status": "ok"})

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip()
    print("使用者傳來：", user_text)
    print(f"DEBUG: 進入 handle_message，使用者輸入: '{user_text}'")
    print(f"DEBUG: user_text 的長度是 {len(user_text)}")
    print(f"DEBUG: user_text 的 ASCII 值 (每個字元): {[ord(c) for c in user_text]}") # <-- 新增這行

    # 這兩個變數在處理 "-"" 之前不應被賦值為 user_text，以避免混淆
    # 讓它們在需要時才被設定
    category = None
    district = None

    if "-" in user_text:
        category, district = user_text.split("-", 1)
        print(f"DEBUG: 檢測到連字號，category='{category}', district='{district}'")

    try:
        # 【5】處理像是「阿秋大肥鵝 地址」這類查詢
        # **修正點：將處理地址、電話、評價的邏輯移動到最前面**
        # 優先處理地址、電話、評價查詢
        # 在這裡，我們也印出匹配的關鍵詞是否存在
        # 1. 處理「店名 的地址」或「店名 的電話」等查詢
        if user_text.endswith("的地址") or user_text.endswith("的電話") or user_text.endswith("的評價"):
            print(f"DEBUG: 匹配到 店家資訊查詢 條件: '{user_text}'")
            # 判斷是查詢地址、電話還是評價
            query_type = ""
            if user_text.endswith("的地址"):
                store_name = user_text.replace("的地址", "").strip()
                query_type = "地址"
            elif user_text.endswith("的電話"):
                store_name = user_text.replace("的電話", "").strip()
                query_type = "電話"
            elif user_text.endswith("的評價"):
                store_name = user_text.replace("的評價", "").strip()
                query_type = "評價"
            
            print(f"DEBUG: 提取店名: '{store_name}', 查詢類型: '{query_type}'")

            # 假設您有一個函數來根據店名獲取資訊
            # 您需要創建這個 get_store_info_by_name 函數，它會從您的數據源（例如 CSV）查詢店名
            store_info = get_store_info_by_name(store_name) 

            reply_message_text = ""
            if store_info:
                if query_type == "地址":
                    reply_message_text = f"{store_name}的地址：{store_info.get('地址', '未知')}"
                elif query_type == "電話":
                    reply_message_text = f"{store_name}的電話：{store_info.get('電話', '未知')}"
                elif query_type == "評價":
                    reply_message_text = f"{store_name}的評價：{store_info.get('評價', '未知')}"
            else:
                reply_message_text = f"抱歉，找不到 {store_name} 的資訊。"

            # 直接回覆使用者點擊按鈕後產生的文字訊息
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_message_text)]
                )
            )
            print("DEBUG: 已發送地址/電話/評價資訊，準備返回")
            return # 處理完畢後立即返回
        
        # 將邏輯分流給不同的 handler 處理
        # 【1】根據區域（例如 "西屯區"、"北區"）顯示該地區的美食店家 Carousel
        # 只有當 user_text 包含 "-" 且成功解析出 district 和 category 時才進入
        elif district and category in [ # 確保 district 不為 None 且 category 在有效列表中
            "台式傳統早餐", "西式輕食早餐", "健康營養早餐", "異國風味早餐",
            "必吃便當", "美味熱炒", "經典飯麵", "特色小吃",
            "火鍋盛宴", "西式精選", "創意料理", "自助饗宴"
        ]:
            print(f"使用者選擇類型：{category}、區域：{district}")
            # create_flex_message_by_category_and_district 應該回傳 FlexMessage 或 None
            carousel_message = create_flex_message_by_category_and_district(category, district)
                        
            # 如果回傳是 None，表示找不到店家
            if carousel_message is None: # 確保明確判斷是否為 None
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="目前找不到符合條件的店家喔！")]
                    )
                )
            else:
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[carousel_message]
                    )
                )
            print("DEBUG: 已發送回覆，準備返回")
            return # 重要：處理完畢後立即返回，避免進入其他條件判斷


        # 【1】主選單：美食推薦
        elif user_text == "美食推薦":
            print("準備呼叫 reply_menu")
            menu_handler.reply_menu(event, messaging_api)  # ✅ 直接呼叫這個
            print("reply_menu 呼叫結束")
            return # 這裡也要加 return

        # 【2】選擇類別
        elif user_text in ["文青早點", "在地美食", "高檔餐廳"]:
            reply_categories(event, messaging_api, user_text)  # ✅ 直接呼叫這個
            print("DEBUG: reply_categories 呼叫結束")
            return # 這裡也要加 return
        
        # 【3】選擇美食類型 → 顯示地區選單
        # 【4】選擇美食類型（例如「台式傳統早餐」）→ 顯示地區選單
        # 這個條件現在只處理純粹的美食類型輸入，而不是「美食類型-區域」
        elif user_text in [ # 注意這裡改為 user_text，以避免與 category 混淆
            "台式傳統早餐", "西式輕食早餐", "健康營養早餐", "異國風味早餐",
            "必吃便當", "美味熱炒", "經典飯麵", "特色小吃",
            "火鍋盛宴", "西式精選", "創意料理", "自助饗宴"
        ]:
            print("DEBUG: 匹配到 選擇美食類型 → 顯示地區選單 條件")
            regions = ["西區", "北區", "南屯區"]

            # 顯示地區選單
            carousel_json = region_handler.reply_region_carousel(user_text, regions)
    
            # 建立 FlexMessage 並回覆
            flex_msg = FlexMessage(
                alt_text="請選擇地區",
                contents=FlexContainer.from_dict(carousel_json)
            )

            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[flex_msg]
                )
            )
            print("DEBUG: 已發送地區選單，準備返回")
            return # 這裡也要加 return
        
        # 【6】找不到指令 → 給提示
        else:
            print("DEBUG: 未匹配任何條件，發送預設訊息")
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="請點選選單或輸入正確的格式")]
                )
            )
            print("DEBUG: 已發送預設訊息，準備返回")
            return # 這裡也要加 return

    except Exception as e:
        print("處理訊息時發生錯誤:", e)
        traceback.print_exc()
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="處理您的請求時發生錯誤，請稍後再試或確認輸入格式。")]
            )
        )
        print("DEBUG: 已發送錯誤訊息，準備返回")
        return # 這裡也要加 return

if __name__ == "__main__":
    app.run(port=5000, debug=True)  # 設定 debug=True 方便開發時查看錯誤訊息