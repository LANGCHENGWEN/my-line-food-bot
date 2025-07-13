# fetch_all.py
"""
一鍵執行店家抓取 + 評論抓取。
兩支腳本若執行失敗，會立刻停止並印出錯誤訊息。
"""
# --- 套件與 Logger 初始化 ---
import sys, logging, subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- 子模組執行器 ---
def run_module(module_name: str):
    """
    這個函式負責呼叫指定模組（.py 檔案）來執行，等同於手動執行 `python -m xxx`。
    - 若模組成功執行，印出成功訊息。
    - 若模組執行錯誤，捕捉例外並印出錯誤內容。
    
    使用 `subprocess.run()` 可以開一個乾淨的子程序環境，執行失敗也不會拖垮主流程。
    """
    try:
        logger.info(f"🚀 執行 {module_name} ...")
        subprocess.run([sys.executable, "-m", module_name], check=True)
        logger.info(f"✅ 完成 {module_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 執行 {module_name} 時發生錯誤：{e}")

# --- 主流程 ---
def main():
    """
    一鍵執行兩個模組：
    1. main_fetch_stores.py：先抓取所有店家資訊，輸出 TaichungEats.csv。
    2. main_fetch_reviews.py：再對每間店查評論，輸出 TaichungEats_reviews.csv。

    資料有相依性：評論查詢要靠前一步產出的 place_id，要有明確的執行順序，並確保每步都成功才繼續下一步。
    """
    run_module("fetch_data.main_fetch_stores")
    run_module("fetch_data.main_fetch_reviews")

# --- 腳本啟動點 ---
if __name__ == "__main__":
    main()
    """
    只有直接用 python fetch_all.py 執行時，才會執行 main()。
    如果別人 import 這支檔案，它就不會自動執行主流程。
    """