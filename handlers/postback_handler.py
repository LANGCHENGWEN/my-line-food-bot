# postback_handler.py
import logging
import urllib.parse
from typing import Set, DefaultDict
from collections import defaultdict

from linebot.v3.messaging import MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks.models import PostbackEvent

from handlers.data_loader import get_store_info_by_name
from handlers.store_detail_reply import reply_store_detail

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# In‑memory storage for favourites. Replace with a DB/Redis in production.
# ----------------------------------------------------------------------------
user_favorites: DefaultDict[str, Set[str]] = defaultdict(set)

# 第五層:店家詳細資訊（地址/電話/評價）

def handle_postback_event(event: PostbackEvent, messaging_api: MessagingApi) -> None:
    """Process a single LINE *PostbackEvent*.

    Expect ``event.postback.data`` formatted as a URL‑encoded query‑string,
    e.g. ``action=save_favorite&shop_id=breakfast_zh``.

    Supported actions::

        action=save_favorite   → 將店家加入使用者收藏
        action=view_info       → 查看店家詳細資訊（地址/電話/評價）
    """
    try:
        # ---------------------------------------------------------------------
        # 1. 解析 postback data
        # ---------------------------------------------------------------------
        data_str = event.postback.data or ""
        data = urllib.parse.parse_qs(data_str)
        action = data.get("action", [""])[0]

        # ---------------------------------------------------------------------
        # 2. 不同 action 分支
        # ---------------------------------------------------------------------
        if action == "view_info":
            _handle_view_info(event, data, messaging_api)
        elif action == "share_shop":
            _handle_share_shop(event, data, messaging_api)
        else:
            logger.warning("Unknown postback action: %s", action)
            _reply(messaging_api, event.reply_token, "抱歉，無法識別的操作")

    except Exception:  # noqa: BLE001  pragma: no cover
        logger.exception("Error while handling postback")
        _reply(messaging_api, event.reply_token, "操作失敗，請稍後再試 🙏")


# -----------------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------------
def _handle_view_info(
    event: PostbackEvent, data: dict[str, list[str]], messaging_api: MessagingApi
) -> None:
    """Return address/phone/rating info for the selected *shop_id*."""
    shop_id_encoded = data.get("shop_id", [""])[0]
    shop_id = urllib.parse.unquote(shop_id_encoded)
    if not shop_id:
        raise ValueError("shop_id missing in postback data")

    logger.info("Send shop detail for %s to user %s", shop_id, event.source.user_id)

    store_info = get_store_info_by_name(shop_id)
    if store_info is None:
        _reply(messaging_api, event.reply_token, "抱歉，找不到該店家資訊。")
        return

    reply_store_detail(shop_id, event, messaging_api)

def _handle_share_shop(
    event: PostbackEvent, data: dict[str, list[str]], messaging_api: MessagingApi
) -> None:
    """將推薦文字回覆給使用者，方便他轉傳給朋友。"""
    shop_name_encoded = data.get("shop_name", [""])[0]
    shop_name = urllib.parse.unquote(shop_name_encoded)

    store_info = get_store_info_by_name(shop_name)
    if not store_info:
        _reply(messaging_api, event.reply_token, f"抱歉，找不到 {shop_name} 的資訊，無法分享。")
        return

    # 你可以自訂分享訊息格式
    share_text = (
        f"🍽️推薦給你一家美食店！\n"
        f"店名：{store_info.get('店名', '無')}\n"
        f"地址：{store_info.get('地址', '無')}\n"
        f"電話：{store_info.get('電話', '無')}\n"
        f"評價：{store_info.get('評價', '無')}\n"
        f"快去看看吧！🏃‍♀️"
    )
    _reply(messaging_api, event.reply_token, share_text)


def _reply(messaging_api: MessagingApi, reply_token: str, text: str) -> None:
    """Send a simple text reply."""
    messaging_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=text)])
    )