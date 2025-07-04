# data_loader.py
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# 動態獲取專案根目錄的路徑
# 這個方法更健壯，因為它不依賴於 app.py 的啟動目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(PROJECT_ROOT, 'TaichungEats.csv') # 請將 'your_data.csv' 替換為您的 CSV 檔案名稱

# 假設您的 CSV 檔案路徑
#CSV_FILE_PATH = '台中美食推薦.csv'

# 全局變數用於存儲數據，避免每次查詢都重新讀取
_store_data = None

def load_store_data():
    """載入店家數據（如果尚未載入）。"""
    global _store_data
    if _store_data is None:
        try:
            _store_data = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
            _store_data.columns = _store_data.columns.str.strip()
            # 確保 '店名' 欄位是字串類型，並處理可能存在的空值
            _store_data['店名'] = _store_data['店名'].astype(str).str.strip()
            logger.info(f"已成功載入店家數據 from {CSV_FILE_PATH}")
        except FileNotFoundError:
            logger.error(f"找不到 CSV 檔案：{CSV_FILE_PATH}")
            _store_data = pd.DataFrame() # 載入失敗時，創建一個空 DataFrame
        except Exception as e:
            logger.exception(f"載入 CSV 檔案時發生未預期的錯誤：{e}")
            _store_data = pd.DataFrame()

def get_store_info_by_name(store_name):
    """
    根據店名查詢店家資訊。
    Args:
        store_name (str): 要查詢的店家名稱。
    Returns:
        dict or None: 如果找到，返回包含店家資訊的字典；否則返回 None。
    """
    load_store_data() # 確保數據已載入

    if _store_data.empty:
        logger.debug("店家數據為空，無法查詢。")
        return None

    # 使用 .loc 進行基於標籤的查詢，並確保店名匹配
    # 這裡使用 .str.contains 而不是 ==，因為店名可能會有細微差異
    # 但是，如果希望精確匹配，可以使用 ==
    # df_found = _store_data[_store_data['店名'].str.contains(store_name, na=False)]
    
    # 為了精確匹配按鈕發送的店名，建議使用 ==
    df_found = _store_data[_store_data['店名'] == store_name]

    if not df_found.empty:
        logger.debug(f"找到店名：{store_name}")
        # 返回第一條匹配的記錄（如果有多條同名店家，只返回第一條）
        return df_found.iloc[0].to_dict()
    else:
        logger.debug(f"找不到店名：{store_name}")
        return None
    
def query_by_category_and_district(category: str, district: str) -> pd.DataFrame:
    """根據類型和區域查詢店家資料"""
    load_store_data()
    if _store_data.empty:
        logger.debug("店家數據為空，無法查詢。")
        return pd.DataFrame()
    # 確保欄位存在
    if "類型" not in _store_data.columns or "區域" not in _store_data.columns:
        logger.error("CSV 缺少必要欄位（類型 或 區域）")
        return pd.DataFrame()
    return _store_data[(_store_data["類型"] == category) & (_store_data["區域"] == district)]

# 您現有的 create_flex_message_by_category_and_district 和 reply_region_carousel 函數也放在這裡
# ... (您的 create_flex_message_by_category_and_district 函數) ...
# ... (您的 reply_region_carousel 函數) ...