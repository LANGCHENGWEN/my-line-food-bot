# data_loader.py
"""
集中管理美食店家資料的載入與查詢工具：
- 讀取專案根目錄下的 TaichungEats.csv（一次）並快取。
- 依店名、類型+區域條件查詢。
"""
# --- 套件匯入 & Logger ---
# 只需要 os 處理路徑、logging 便於偵錯及 pandas 讀取 CSV
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# 動態獲取專案根目錄的路徑
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 構建出一個指向特定 CSV 檔案的完整、正確的絕對路徑
CSV_FILE_PATH = os.path.join(PROJECT_ROOT, 'TaichungEats.csv')

# --- 資料快取變數 ---
# 全局變數用於存儲數據，避免每次查詢都重新讀取
_store_data = None

# --- 載入 CSV：load_store_data() ---
# 確保只讀取一次並且處理欄位清理/型別轉換
def load_store_data():
    global _store_data
    if _store_data is None:
        try:
            # 讀取 CSV；若編碼不同，可於此調整
            _store_data = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')

            # 去除欄位名稱多餘空白，避免日後 KeyError
            _store_data.columns = _store_data.columns.str.strip()

            # 將 '店名' 轉為 str 並去空白，增進匹配準確度
            _store_data['店名'] = _store_data['店名'].astype(str).str.strip()
            logger.info(f"已成功載入店家數據 from {CSV_FILE_PATH}")

        except FileNotFoundError:
            logger.error(f"找不到 CSV 檔案：{CSV_FILE_PATH}")
            _store_data = pd.DataFrame() # 載入失敗時，仍回傳空表避免程式整體崩潰
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
    if "類型" not in _store_data.columns or "區域" not in _store_data.columns:
        logger.error("CSV 缺少必要欄位（類型 或 區域）")
        return pd.DataFrame()
    
    return _store_data[(_store_data["類型"] == category) & (_store_data["區域"] == district)]