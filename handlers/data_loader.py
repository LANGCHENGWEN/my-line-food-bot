# data_loader.py
"""
集中管理美食店家資料的載入與查詢工具：
- 讀取專案根目錄下的 TaichungEats_reviews.csv（一次）並快取。
- 依店名、類型+區域條件查詢。
- 部署於雲端時，若本地無 CSV，從雲端下載並存檔。
- 從環境變數讀取 CSV 直連下載 URL 與存取 Token（如果有）。
"""
# --- 套件匯入 & Logger ---
# 只需要 os 處理路徑、logging 便於偵錯及 pandas 讀取 CSV
import os
import logging
import requests
import pandas as pd
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# --- 載入 .env 檔案中的環境變數 ---
# load_dotenv() 會搜尋並讀取同層或父層的 .env，將其轉為系統環境變數，之後可用 os.getenv() 取得
load_dotenv()

# --- 本地 CSV 檔案路徑 ---
# 動態獲取專案根目錄的路徑
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# 指向特定 CSV 檔案的完整絕對路徑
CSV_FILE_PATH = os.path.join(PROJECT_ROOT, '..', 'fetch_data', 'TaichungEats_reviews.csv')

# 環境變數讀取
CSV_DOWNLOAD_URL = os.getenv("CSV_DOWNLOAD_URL", "")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)  # 如果沒有 Token 可設為 None

# --- 資料快取變數 ---
# 全局變數用於存儲數據，避免每次查詢都重新讀取
_store_data = None

def download_csv():
    """從雲端 URL 下載 CSV 並寫入本地。"""
    if not CSV_DOWNLOAD_URL:
        logger.error("未設定環境變數 CSV_DOWNLOAD_URL，無法下載 CSV")
        return False

    headers = {}
    if ACCESS_TOKEN:
        headers['Authorization'] = f"Bearer {ACCESS_TOKEN}"

    try:
        logger.info(f"從雲端下載 CSV：{CSV_DOWNLOAD_URL}")
        response = requests.get(CSV_DOWNLOAD_URL, headers=headers, timeout=30)
        response.raise_for_status()
        os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
        with open(CSV_FILE_PATH, 'wb') as f:
            f.write(response.content)
        logger.info(f"CSV 成功下載並存到本地：{CSV_FILE_PATH}")
        return True
    except Exception as e:
        logger.error(f"下載 CSV 失敗：{e}")
        return False

# --- 載入 CSV：load_store_data() ---
# 確保只讀取一次並且處理欄位清理/型別轉換
def load_store_data():
    global _store_data
    if _store_data is not None:
        return
    
    # 如果本地 CSV 不存在，嘗試從雲端下載（部署環境）
    if not os.path.exists(CSV_FILE_PATH):
        logger.warning(f"本地 CSV 不存在：{CSV_FILE_PATH}")
        if CSV_DOWNLOAD_URL:
            success = download_csv()
            if not success:
                _store_data = pd.DataFrame()  # 下載失敗，回傳空 DataFrame 避免錯誤
                return
        else:
            logger.error("無法下載 CSV，且本地 CSV 不存在")
            _store_data = pd.DataFrame()
            return

    try:
        # 讀取 CSV；確保「評論」欄為字串型態
        _store_data = pd.read_csv(CSV_FILE_PATH, encoding='utf-8', dtype={"評論": str})

        # 去除欄位名稱多餘空白，避免日後 KeyError
        _store_data.columns = _store_data.columns.str.strip()

        # 將 '店名' 轉為 str 並去空白，增進匹配準確度
        _store_data['店名'] = _store_data['店名'].astype(str).str.strip()
        logger.info(f"已成功載入店家數據 from {CSV_FILE_PATH}")

    except Exception as e:
        logger.exception(f"載入 CSV 檔案時發生未預期的錯誤：{e}")
        _store_data = pd.DataFrame()

# --- 依店名查詢：get_store_info_by_name() ---
def get_store_info_by_name(store_name):
    """
    根據店名查詢店家資訊:
    store_name (str): 要查詢的店家名稱。
    dict or None: 如果找到，返回包含店家資訊的字典；否則返回 None。
    """
    load_store_data() # 確保資料已載入

    if _store_data.empty:
        logger.debug("店家數據為空，無法查詢。")
        return None
    
    # 精確匹配：按鈕點擊傳來完整店名，使用 ==
    df_found = _store_data[_store_data['店名'] == store_name]

    if not df_found.empty:
        logger.debug(f"找到店名：{store_name}")
        return df_found.iloc[0].to_dict() # 返回第一條匹配的記錄（如果有多條同名店家，只返回第一條）
    else:
        logger.debug(f"找不到店名：{store_name}")
        return None
    
# --- 依類型 + 區域查詢：query_by_category_and_district() ---
def query_by_category_and_district(category: str, district: str) -> pd.DataFrame:
    """根據類型與區域條件回傳符合的店家"""
    load_store_data()

    if _store_data.empty:
        logger.debug("店家數據為空，無法查詢。")
        return pd.DataFrame()
    
    # 確保欄位存在
    if "美食類型" not in _store_data.columns or "區域" not in _store_data.columns:
        logger.error("CSV 缺少必要欄位（美食類型 或 區域）")
        return pd.DataFrame()
    
    return _store_data[(_store_data["美食類型"] == category) & (_store_data["區域"] == district)]