# 🍜 美食推薦 LINE Bot

一個智慧型的 LINE Bot，幫助用戶從「選風格」到「查店家」，一步步推薦合適的美食，並整合 Google 地圖、評論與分享功能，適合日常用餐、旅行找餐廳，或與朋友分享美食。

---

## 📹 LINE Bot Demo：美食推薦小幫手操作展示

這段影片展示了 LINE Bot 的實際操作流程，包括：

- 根據使用者選擇美食類型與區域，推薦店家美食
- 顯示 Flex Message 卡片格式、店家資訊、美食評論
- 整合 Google Maps 導航到該店

🎬 點擊下方縮圖觀看影片：

[![LINE Bot Demo 影片預覽](https://img.youtube.com/vi/zUHMCs9_erM/maxresdefault.jpg)](https://youtu.be/zUHMCs9_erM)

---

## 📲 使用流程介紹

### 🧭 用戶完整互動流程

1. 👋 **首次加入好友**  
　→ Bot 回覆歡迎訊息與使用說明

2. 💬 **輸入「美食推薦」**  
　→ Bot 回覆多種「餐廳風格選單」  
　（例如：文青早點、在地美食、高檔餐廳）

3. 🍽️ **點選風格選單中的一項**  
　→ Bot 回覆該風格的「料理類型選單」  
　（例如：在地美食 → 便當、熱炒、飯麵、小吃）

4. 🗺️ **點選料理類型**  
　→ Bot 回覆「區域滑動選單」  
　（例如：北區、北屯區、西區）

5. 🏠 **點選區域**  
　→ Bot 回覆「多家店家卡片滑動選單」  
　　包含：店名 + 營業時間

6. 🔍 **點選其中一家店的「查看資訊」按鈕**  
　→ Bot 回覆該店的資訊：
   - 店名
   - 地址
   - 電話
   - 評論

7. 🗺️ **點選「開啟地圖」**  
　→ 直接打開 Google Maps 導航到該店

8. 📤 **點選「分享店家」**  
　→ Bot 回覆完整資訊，方便用戶**長按複製或轉傳給朋友**

---

## 🔧 技術架構

- 💻 後端框架 | Python + Flask
- ☁️ 雲端部署 | Render
- 💬 LINE SDK | LINE Messaging API (v3)
- 🌐 外部 API | Google Maps + Google Places API（店家搜尋與評論）
- 🌍 翻譯功能 | Google Translate API（英文評論自動翻譯成中文）
- 🎨 訊息格式 | Flex Message（支援滑動選單與卡片）

---

## 🔑 使用技術細節

- **狀態管理**：根據使用者點擊動作記錄進度，逐層導引選單（風格 → 類型 → 區域 → 店家）
- **動態回覆**：Flex Message 自動生成，結合用戶選擇回覆個性化資訊
- **評論翻譯**：抓取 Google 英文評論，自動翻譯為中文後附上原文

---

## ⚙️ 開發與部署

### 安裝環境

```bash
# 建立虛擬環境
python -m venv my_venv

#（Windows）啟動虛擬環境 (Linux 或 macOS 用 source venv/bin/activate)
my_venv\Scripts\activate

# 安裝所有依賴套件
pip install -r requirements.txt
```

### 在專案根目錄建立環境變數 `.env` 檔案

```env
LINE_CHANNEL_SECRET=YOUR_CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN=YOUR_CHANNEL_ACCESS_TOKEN
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
GOOGLE_TRANSLATE_KEY=YOUR_GOOGLE_TRANSLATE_KEY
```

### 本地啟動

```bash
python main.py
```

### Render 部署指令

```bash
# 在 Render 網頁上新增 Web Service 時填入：

# 📌 Build Command:
pip install -r requirements.txt

# 📌 Start Command:
gunicorn main:app

# 📌 Health Check Path:
/
```

---

## 📄 授權說明
本專案僅供學術研究與作品展示用途。
LINE 與 Google 為其商標所有者，與本專案無商業合作。

---

## 🙋‍♂️ 作者
郎承文｜2025
如果你對專案有興趣，歡迎交流或點 star 🌟 支持！
