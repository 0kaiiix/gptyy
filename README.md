# AI 語音助手

基於 OpenAI ChatGPT 3.5 和 gTTS 的 AI 對話與語音合成應用。

## 功能特點

- 🤖 使用 OpenAI ChatGPT 3.5 強大的 AI 模型回答問題
- 🔊 自動將 AI 回應轉換為語音
- 🌐 支援多種語言輸入和語音輸出
- 💬 保存對話歷史記錄
- ✨ 美觀的用戶界面與互動效果

## 安裝步驟

1. 克隆或下載此專案
2. 安裝所需套件：
   ```
   pip install -r requirements.txt
   ```
3. 設置 OpenAI API 金鑰：
   - 複製 `.env-sample` 檔案為 `.env`
   - 編輯 `.env` 檔案，將 `your_api_key_here` 替換為您的 OpenAI API 金鑰
   - 確保以 UTF-8 編碼儲存 .env 檔案

## 使用方法

1. 啟動應用程式：
   ```
   streamlit run TF.py
   ```
2. 在瀏覽器中打開顯示的網址（通常是 http://localhost:8501）
3. 在輸入框中輸入您的問題
4. 點擊「發送問題」按鈕
5. 查看 AI 回應並聆聽語音輸出

## 取得 OpenAI API 金鑰

1. 訪問 [OpenAI Platform](https://platform.openai.com/)
2. 註冊或登入您的 OpenAI 帳號
3. 前往 API Key 頁面
4. 創建新的 API Key

## 技術架構

- **前端框架**：Streamlit
- **AI 模型**：OpenAI ChatGPT 3.5
- **語音合成**：Google Text-to-Speech (gTTS)
- **動畫效果**：Lottie

## 系統要求

- Python 3.8 或更高版本
- 網絡連接（用於 API 調用）
- 支援音訊播放的瀏覽器 