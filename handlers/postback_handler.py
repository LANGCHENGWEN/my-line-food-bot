# postback_handler.py
"""
處理 LINE PostbackEvent : 
- 支援「查看店家資訊」與「分享店家」兩種自訂 action。
- 解析 URL query-string 格式的 data 後路由至對應 helper。
"""
# --- 匯入套件與 Logger ---
import logging
import urllib.parse

from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks.models import PostbackEvent

from handlers.data_loader import get_store_info_by_name
from handlers.store_detail_reply import reply_store_detail

logger = logging.getLogger(__name__)

# --- 入口：handle_postback_event() ---
def handle_postback_event(event: PostbackEvent, messaging_api: MessagingApi) -> None:
    """
    解析 postback data → 根據 action 做不同操作。
    若解析或處理過程出錯，使用共用 _reply 輕量回覆。
    支援的操作:
    action=view_info  → 查看店家詳細資訊（地址/電話/評價）
    action=share_shop → 分享店家資訊
    """
    try:
        # 1. 解析 postback data
        data_str = event.postback.data or ""
        data = urllib.parse.parse_qs(data_str)
        action = data.get("action", [""])[0]

        # 2. 不同 action 分支
        if action == "view_info":
            _handle_view_info(event, data, messaging_api)
        elif action == "share_shop":
            _handle_share_shop(event, data, messaging_api)
        else:
            logger.warning("Unknown postback action: %s", action)
            _reply(messaging_api, event.reply_token, "抱歉，無法識別的操作😥")

    except Exception:
        logger.exception("Error while handling postback")
        _reply(messaging_api, event.reply_token, "操作失敗，請稍候再試 🙏")

# --- 將實際邏輯拆小函式，易於單元測試與維護 ---
# 查詢並回覆『店家詳細資訊』
def _handle_view_info(
    event: PostbackEvent, data: dict[str, list[str]], messaging_api: MessagingApi
) -> None:
    shop_id_encoded = data.get("shop_id", [""])[0]
    shop_id = urllib.parse.unquote(shop_id_encoded)
    if not shop_id:
        raise ValueError("postback data 中缺少 shop_id")

    logger.info("將 %s 的店家詳細資訊發送給用戶 %s", shop_id, event.source.user_id)

    store_info = get_store_info_by_name(shop_id)
    if store_info is None:
        _reply(messaging_api, event.reply_token, "抱歉，找不到該店家資訊😥")
        return

    # 交由 store_detail_reply.py 產生 Flex 卡片
    reply_store_detail(shop_id, event, messaging_api)

# 將推薦文字回覆給使用者，讓使用者可轉傳給好友
def _handle_share_shop(
    event: PostbackEvent, data: dict[str, list[str]], messaging_api: MessagingApi
) -> None:
    shop_name_encoded = data.get("shop_name", [""])[0]
    shop_name = urllib.parse.unquote(shop_name_encoded)

    store_info = get_store_info_by_name(shop_name)
    if not store_info:
        _reply(messaging_api, event.reply_token, f"抱歉，找不到 {shop_name} 的資訊，無法分享😥")
        return

    # 可以自訂分享訊息格式
    share_text = (
        f"🍽️推薦給你一家美食店！\n"
        f"店名：{store_info.get('店名', '無')}\n"
        f"地址：{store_info.get('地址', '無')}\n"
        f"電話：{store_info.get('電話', '無')}\n"
        f"評價：{store_info.get('評價', '無')}\n"
        f"快去看看吧！🏃‍♀️"
    )
    _reply(messaging_api, event.reply_token, share_text)

# 包裝簡易文字回覆：統一呼叫，減少重複碼
def _reply(messaging_api: MessagingApi, reply_token: str, text: str) -> None:
    messaging_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=text)])
    )