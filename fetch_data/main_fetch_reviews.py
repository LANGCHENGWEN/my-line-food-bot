# main_fetch_reviews.py
"""
fetch_reviews.py的主程式，單獨執行程式時，執行這個檔案。
輸入 CSV 讀取店家資料（店名與地址），透過 Google Places API 抓取對應評論。
必要時翻譯成中文後寫入輸出 CSV。
"""
# --- 套件與 Logger 初始化 ---
import csv, time
import logging
import pandas as pd
from tqdm import tqdm
from .fetch_reviews import (
    input_csv, output_csv,
    max_rev, SAVE_FULL_REVIEWS,
    search_place_id, get_reviews, translate_text
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- 主流程 ---
def main():
    # 讀取輸入 CSV 檔案，先將資料載入 DataFrame（避免每筆重複），也確保 "評論" 欄位存在
    df = pd.read_csv(str(input_csv), encoding="utf-8", dtype={"評論": str})
    if "評論" not in df.columns:
        df["評論"] = ""

    full_reviews_rows = [] # 若啟用 SAVE_FULL_REVIEWS，就儲存完整原文+翻譯評論

    # 遍歷每一家店的資料，依序查詢評論
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Fetching"):
        store_name = str(row["店名"]).strip()
        address    = str(row["地址"]).strip()
        query      = f"{store_name} {address}" # 組成搜尋用的 query：店名 + 地址

        place_id = search_place_id(query) # 查詢該店家的 Google Place ID
        if not place_id:
            logger.warning(f"找不到 place_id: {store_name}，query: {query}")
            continue # 沒找到就跳過

        det = get_reviews(place_id) # 根據 Place ID 抓評論資訊
        if not det:
            continue # 沒有評論就跳過

        reviews = det.get("reviews", [])[:max_rev] # 擷取最多 max_rev 則評論
        reviews_translated = [] # 儲存翻譯結果
        reviews_full = [] # 若啟用儲存完整評論，額外存這裡

        # 處理每一則評論：讀取原文、判斷語言、決定是否翻譯
        for rev in reviews:
            text_field = rev.get("text", {})
            if isinstance(text_field, dict):
                comment = text_field.get("text", "") # 新版 API 格式
                lang    = text_field.get("languageCode", "zh-TW")
            else:
                comment = str(text_field) # 舊格式或 fallback
                lang = "zh-TW"

            lang = str(lang).strip() # 清潔和標準化 lang 變數的值
            logger.debug(f"lang raw repr: {repr(lang)}")

            # 判斷是否為繁體中文，若否就送翻譯 API
            if lang not in ("zh-TW", "zh-Hant"):
                logger.warning(f"⚠️ 會進翻譯區塊的語言: {lang!r}")
                trans = translate_text(comment)
            else:
                logger.debug("➡️ 繁體中文，直接使用原文，不呼叫翻譯 API")
                trans = comment

            # 確保 comment 是字串
            if not isinstance(comment, str):
                comment = str(comment)

            # 加入翻譯結果，並視情況記錄完整評論（原文＋翻譯）
            reviews_translated.append(trans)

            # 將評論的原文和翻譯版本結合起來，並儲存到一個清單 (list) 中
            if SAVE_FULL_REVIEWS:
                full_text = f"原文:\n{comment}\n\n翻譯:\n{trans}"
                reviews_full.append(full_text)

            logger.debug(f"comment type: {type(comment)}, trans type: {type(trans)}") 
            # 你可以選擇只顯示原文或翻譯文或兩者皆有
            logger.debug(f"原文: {comment}")
            logger.debug(f"翻譯: {trans}")
            logger.debug("-" * 20)

        # 將這家店所有評論（翻譯後）合併後寫入 DataFrame
        df.at[idx, "評論"] = "\n\n".join(reviews_translated)

        # 若有啟用完整評論輸出，就另外記錄下來以便後續寫檔
        if SAVE_FULL_REVIEWS:
            full_reviews_rows.append({
                "店名": store_name,
                "地址": address,
                "原文+翻譯評論": "\n\n---\n\n".join(reviews_full)
            })

        time.sleep(0.1) # 避免過快觸發 Google API 限制

    # 所有評論處理完成後，寫出主輸出檔（含翻譯後的評論欄）
    df.to_csv(str(output_csv), index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig")
    logger.info(f"✅ 完成！已輸出 {output_csv}（{len(df)} 則評論）")

    # 若啟用完整評論紀錄，寫出另一份 CSV
    if SAVE_FULL_REVIEWS:
        df_full = pd.DataFrame(full_reviews_rows)
        df_full.to_csv("full_reviews.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig")
        logger.info(f"✅ 也輸出完整原文+翻譯評論檔 full_reviews.csv")

# --- 程式進入點：只在直接執行此檔案時才會啟動 main() ---
if __name__ == "__main__":
    main()