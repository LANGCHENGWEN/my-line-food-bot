# fetch_stores.py
"""
根據區域與美食類型，透過 Google Places API 抓取台中市餐廳資料，並輸出成 TaichungEats.csv。
涵蓋資訊包含：place_id、區域、美食類型、店名、營業時間、地址、電話等欄位。
- 支援自動載入舊資料、避免重複
- 自動排序與清洗資料
- 搭配 fetch_reviews.py 使用可補足評論資訊
"""
# --- 套件與環境變數設定 ---
import os, time, logging
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from constants import FOOD_TYPES, REGIONS, AREA_COORDS
from .api_quota_utils import request_with_quota_check

# --- Logger 初始化 ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- 載入 .env 環境變數 ---
load_dotenv()  # 讀取 .env
API_KEY = os.getenv("GOOGLE_API_KEY")

# --- 設定最終輸出的 CSV 路徑 ---
CSV_PATH = Path(__file__).resolve().parent / "TaichungEats.csv"

# --- 搜尋店家列表（TextSearch） ---
def search_places(food_type, location, max_results=3):
    """
    用 Google Maps API 根據美食類型和區域位置搜尋餐廳，回傳地點資料列表。
    以區域為中心點做半徑搜尋，抓取對應類型餐廳。
    """
    lat, lng = map(float, location.split(",")) # 分別取出緯度和經度，並轉成浮點數存到變數 lat 和 lng 裡

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName"
    }

    body = {
        "textQuery": food_type,
        "includedType": "restaurant",
        "pageSize": max_results, # 最多回傳筆數
        "languageCode": "zh-TW",
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": 3000 # 公尺
            }
        }
    }

    # 對指定的 url 發送一個 POST 請求，最後把回傳的結果存到 data 變數中
    data = request_with_quota_check(
        "POST", url, context=f"TextSearch {food_type}@{location}",
        headers=headers, json=body
    )

    # 如果配額真的用完，停止這一輪搜尋
    if data.get("status") == "OVER_QUERY_LIMIT": # 自己定義的回傳碼
        logger.warning("⚠️ %s @ %s 搜尋因配額不足終止", food_type, location)
        return []

    # 印出 Google Places 回傳的狀態
    logger.debug("📥 status=%s, results=%d, url=%s",
                data.get("status"), len(data.get("results", [])), url)

    # API New 把結果放在 data["places"]
    return data.get("places", [])

# --- 查詢店家詳細資料（Details API） ---
def get_place_details(place_id):
    """
    根據 place_id 取得該店家詳細資訊，包含營業時間、地址、電話等。
    TextSearch 僅提供簡略資訊，需額外請求詳細欄位。
    """
    field_mask = [
        "id",
        "displayName",
        "formattedAddress",
        "internationalPhoneNumber",
        "regularOpeningHours.weekdayDescriptions",
    ]

    url = (
        f"https://places.googleapis.com/v1/places/{place_id}"
        f"?languageCode=zh-TW&fields={','.join(field_mask)}"
    )

    headers = {"X-Goog-Api-Key": API_KEY}

    # 以 GET 方法向指定的 url 發送請求，最後把回傳的結果存到 data 變數中
    data = request_with_quota_check(
        "GET", url, context=f"GetPlace {place_id}", headers=headers
    )

    # 如果配額真的用完，停止這一輪搜尋
    if data.get("status") == "OVER_QUERY_LIMIT":
        return {}
    
    return data

# --- 載入舊資料 ---
REQUIRED_COLS = ["place_id", "區域", "美食類型", "店名", "營業時間", "地址", "電話"]

def load_old_data(csv_path: str) -> pd.DataFrame:
    """
    讀取舊有 CSV 並補齊欄位格式，若無舊資料則建立空表格。
    支援更新資料時合併新舊資訊，減少重複抓取。
    """
    if os.path.exists(csv_path):
        logger.info("📂 讀取舊資料 %s", csv_path)
        df = pd.read_csv(csv_path, dtype=str, encoding="utf-8")

        # 補缺少欄位，並填空字串
        for col in REQUIRED_COLS:
            if col not in df.columns:
                logger.warning("🔧 舊檔缺少欄位 %s，已補空白欄", col)
                df[col] = ""

        # 只保留且依照 REQUIRED_COLS 排序欄位
        df = df[REQUIRED_COLS]
        return df

    # 若舊檔不存在，回傳含必要欄位的空 DataFrame
    logger.info("📂 無舊資料，將建立新檔")
    return pd.DataFrame(columns=REQUIRED_COLS)

# --- 抓取所有新店家資料 ---
def collect_new_rows() -> list[dict]:
    """
    針對每種美食類型與區域，搜尋新店家，組成資料列清單。
    搭配 FOOD_TYPES 與區域座標逐一搜尋，保證資料覆蓋廣泛。
    """
    seen_ids = set()
    new_rows = []

    for food_type in FOOD_TYPES:
        for area_name, coord in AREA_COORDS.items():
            logger.info("🔍 正在抓取 %s @ %s", food_type, area_name)

            places = search_places(food_type, coord, max_results=3)
            for place in places:
                pid = place.get("id")
                if not pid or pid in seen_ids: # 用 pid 判斷是否重複
                    continue
                seen_ids.add(pid)

                details = get_place_details(pid)
                time.sleep(0.6)  # 控制 API 呼叫頻率，避免過度呼叫 API

                new_rows.append({
                    "place_id": pid,
                    "區域": area_name,
                    "美食類型": food_type,
                    "店名": details.get("displayName", {}).get("text", ""),
                    "營業時間": " / ".join(details.get("regularOpeningHours", {}).get("weekdayDescriptions", [])),
                    "地址": details.get("formattedAddress", ""),
                    "電話": details.get("internationalPhoneNumber", "")
                })
    return new_rows

# --- 排序 DataFrame ---
def sort_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    根據設定順序排序所有資料（區域 → 美食類型 → 店名）。
    """
    area_order = {a: i for i, a in enumerate(REGIONS)}
    type_order = {t: i for i, t in enumerate(FOOD_TYPES)}

    # Pandas DataFrame 欄位批次處理
    # 先把欄位轉成字串並去除前後空白
    df["區域"] = (
        df["區域"]
        .astype(str)
        .str.strip()
        .str.extract(r"（(.*?)）", expand=False) # 把括號內中文抓出
        .fillna(df["區域"].str.strip())          # 若本來就沒括號則保持原值
    )
    df["美食類型"] = df["美食類型"].str.strip()

    # 將「區域」和「美食類型」轉成排序用的數值欄位
    df["__area_rank"] = df["區域"].map(area_order)
    df["__type_rank"] = df["美食類型"].map(type_order)

    # 依照區域 → 美食類型 → 店名排序，回傳排序結果
    df_sorted = df.sort_values(
        by=["__area_rank", "__type_rank", "店名"],
        ascending=[True, True, True],
        ignore_index=True
    ).drop(columns=["__area_rank", "__type_rank"])
    return df_sorted