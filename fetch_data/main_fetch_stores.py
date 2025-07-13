# main_fetch_stores.py
"""
fetch_stores.py的主程式，單獨執行程式時，執行這個檔案。
整合舊的店家資料與新抓取的店家清單，並更新輸出到一份完整的 CSV 檔。
避免重複寫入相同店家，同時新增新的店家。
"""
# --- 套件與 Logger 初始化 ---
import csv, logging
import pandas as pd
from .fetch_stores import (
    load_old_data, collect_new_rows, sort_dataframe,
    REQUIRED_COLS, CSV_PATH
)

logger = logging.getLogger(__name__)

# --- 主流程 ---
def main():
    # 1. 讀舊資料
    # 從既有的 CSV 檔中讀取舊的店家資料
    df_old = load_old_data(CSV_PATH)

    # 把舊檔分成兩批：有 place_id 與沒 place_id
    df_with_pid    = df_old[df_old["place_id"].str.strip() != ""]
    df_without_pid = df_old[df_old["place_id"].str.strip() == ""]

    # 建立一個包含所有不重複 place_id 的集合
    existing_pids  = set(df_with_pid["place_id"].str.strip())

    # 對於沒有 place_id 的舊資料，改用 (店名 + 區域 + 地址) 的組合作為 key 來比對新資料
    existing_keys  = set(
        zip(df_without_pid["店名"].str.strip(),
            df_without_pid["區域"].str.strip(),
            df_without_pid["地址"].str.strip())
    )

    # 2. 抓取新的店家資料
    rows = collect_new_rows()
    logger.info("🔍 collect_new_rows() 抓到 %d 家", len(rows))

    new_rows = []
    for r in rows:
        """判斷新抓到的資料中哪些是新的店家，並過濾掉重複的。"""
        pid = r["place_id"].strip()
        name_addr = (r["店名"].strip(), r["區域"].strip(), r["地址"].strip())

        if pid:  # 新資料有 place_id
            if pid not in existing_pids:
                new_rows.append(r)
        else:    # 新資料沒有 place_id，用 (店名, 區域, 地址) 判重
            if name_addr not in existing_keys:
                new_rows.append(r)

    logger.info("🆕 新增 %d 筆", len(new_rows))

    # 3. 合併 & 排序
    # 將新舊資料合併為一份統一的表格
    df_new = pd.DataFrame(new_rows)
    df_merged = pd.concat([df_old, df_new], ignore_index=True)
    
    # 根據自定義邏輯排序資料，並確保輸出欄位順序符合需求
    df_merged = sort_dataframe(df_merged)[REQUIRED_COLS]

    # 4. 輸出
    # 將合併後的完整資料寫回指定的 CSV 檔案
    df_merged.to_csv(CSV_PATH, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
    logger.info("✅ 完成！總筆數 %d，已寫入 %s", len(df_merged), CSV_PATH)

# --- 程式進入點：只在直接執行此檔案時才會啟動 main() ---
if __name__ == "__main__":
    main()