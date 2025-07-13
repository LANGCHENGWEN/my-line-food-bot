# api_quota_utils.py
"""
對 Google API 發送請求時，能「自動處理流量限制錯誤」。
並重試幾次後再放棄，避免程式整體崩潰或異常。
"""
# --- 套件與 Logger 初始化 ---
import time, logging, requests

logger = logging.getLogger(__name__)

# --- 定義 request_with_quota_check 函式，用於發送 Google API 請求時，自動偵測配額限制並處理重試 ---
def request_with_quota_check(
    method: str,
    url: str,
    context: str = "", # 額外的字串，方便標記是哪一個功能模組在呼叫（例如："place search"）
    retries: int = 3,  # 最多嘗試幾次（避免無限重試）
    backoff: int = 60, # 每次重試等待秒數（避免馬上重打導致被封 IP）
    **kwargs           # requests 的額外參數如 headers、params 等
) -> dict:
    """
    對 Google API 發送 GET 請求，並偵測配額不足的狀況。
    若遇到配額不足 (HTTP 429 或 status == OVER_QUERY_LIMIT)，會嘗試重試，並記錄錯誤。
    """
    # --- 重試機制 ---
    # 進行最多 `retries` 次請求，遇到錯誤或配額問題時會 sleep 後再嘗試
    for attempt in range(1, retries + 1):
        try:
            # 發送實際的 HTTP 請求（使用 requests 的萬用 request 方法）
            resp = requests.request(method, url, timeout=10, **kwargs)
        except requests.exceptions.RequestException as e:
            # 若連不上（例如網路斷線），記錄錯誤並回傳失敗狀態
            logger.error("🔌 [%s] 無法連線 (%s)", context, e)
            return {"status": "REQUEST_FAILED"}

        # --- 層級一：HTTP 回應碼檢查 ---
        # 如果 HTTP 回傳 429，代表觸發流量控制（Too Many Requests）
        if resp.status_code == 429:
            logger.error("⛔️ [%s] API 配額已用盡 (HTTP 429) — 第 %d/%d 次", context, attempt, retries)
            time.sleep(backoff)
            continue # 重試下一輪

        # 若是其他 HTTP 錯誤（例如 400、403、500），則直接記錄並回傳失敗
        if resp.status_code >= 400:
            logger.error("❌ [%s] HTTP %d\n%s", context, resp.status_code, resp.text)
            return {"status": f"HTTP_{resp.status_code}"}

        # --- 層級二：API 回傳的 JSON 結果檢查 ---
        # 若是成功的回應就轉成 JSON，並檢查是否有 API 自定義的錯誤訊息（例如 OVER_QUERY_LIMIT）
        data = resp.json()
        if data.get("status") == "OVER_QUERY_LIMIT":
            logger.error("⛔️ [%s] API 配額已用盡 (OVER_QUERY_LIMIT) — 第 %d/%d 次", context, attempt, retries)
            time.sleep(backoff)
            continue # 重試下一輪

        return data # 若一切正常，直接回傳資料（例如包含搜尋結果）

    # --- 最終失敗處理區塊 ---
    # 若超過重試次數仍未成功，就明確回傳 OVER_QUERY_LIMIT (配額不足) 狀態，讓上層可依此判斷
    return {"status": "OVER_QUERY_LIMIT"}