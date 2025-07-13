# fetch_reviews.py
"""
根據 TaichungEats.csv 裡的店家基本資訊，查詢每家店的 place_id 並抓取評論。
評論包含原文與翻譯（僅翻非中文），最終輸出為 TaichungEats_reviews.csv。
- 使用 Google Places v1 API 查詢 place_id 與評論
- 使用 Google Translate API 翻譯英文內容
- 可調整最多抓取評論數量與是否儲存完整評論記錄
"""
# --- 套件與環境變數設定 ---
import os, json
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

# --- Logger 初始化 ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- 載入 .env 環境變數 ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
TRANSLATE_KEY = os.getenv("GOOGLE_TRANSLATE_KEY")

# --- 檔案路徑與參數 ---
BASE_DIR   = Path(__file__).resolve().parent
input_csv  = BASE_DIR / "TaichungEats.csv"
output_csv = BASE_DIR / "TaichungEats_reviews.csv"
max_rev    = 3            # 每間店最多抓幾則評論
SAVE_FULL_REVIEWS = False # 若為 True，會另存原文+翻譯完整評論檔案

# --- 步驟 3：翻譯英文評論（只翻非中文）---
def translate_text(text, target_lang="zh-TW"):
    """
    呼叫 Google Translate API 將評論翻譯成中文。
    確保英文評論能被中文使用者理解，也便於後續 Flex Message 呈現。
    """
    url = f"https://translation.googleapis.com/language/translate/v2?key={TRANSLATE_KEY}"
    payload = {
        "q": text,
        "target": target_lang,
        "format": "text"
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=payload)
    try:
        return resp.json()["data"]["translations"][0]["translatedText"]
    except Exception as e:
        logger.error(f"⚠️ 翻譯失敗", e, exc_info=True)
        return text # 失敗時直接回傳原文，避免整體流程崩潰

# --- 步驟 1：查詢 place_id ---
def search_place_id(query: str) -> str | None:
    """
    使用 Google Places v1 的 Text Search API，根據店名+地址查詢 place_id。
    後續取得評論資料必須先拿到 place_id。
    """
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"
    }

    payload = {
        "textQuery": query,
        "languageCode": "zh-TW",
        "regionCode": "TW"
    }

    resp  = requests.post(url, headers=headers, json=payload, timeout=10)
    data  = resp.json()
    logger.debug(json.dumps(data, indent=2, ensure_ascii=False)) # 印出 API 回傳內容以利除錯

    if data.get("places"):
        place_id = data["places"][0]["id"]
        logger.info(f"✅ 找到 place_id: {place_id}")
        return place_id
    else:
        logger.warning(f"❌ 找不到 place_id")
        return None

# --- 步驟 2：查詢詳細資料與評論 ---
def get_reviews(place_id: str) -> dict | None:
    """
    根據 place_id 查詢該店的詳細資料，包括評論列表。
    評論是我們最終要取得的資料，這個步驟是主流程的核心。
    """
    details_url = f"https://places.googleapis.com/v1/places/{place_id}?key={API_KEY}&languageCode=zh-TW&regionCode=TW&fields=displayName,formattedAddress,userRatingCount,reviews"

    details_headers = {
        "Content-Type": "application/json"
    }

    try:
        details_resp = requests.get(details_url, headers=details_headers, timeout=10)
        det = details_resp.json()
    
        if isinstance(det, dict):
            logger.info(f"✅ 成功取得詳細資料")
            logger.debug(json.dumps(det, indent=2, ensure_ascii=False))
            return det
        else:
            logger.warning(f"❌ 回傳不是 dict，而是 {type(det)}")
            return {}

    except Exception as e:
        logger.error(f"❌ get_reviews 發生錯誤", e, exc_info=True)
        return {}