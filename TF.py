#
import streamlit as st
import openai
from gtts.lang import tts_langs
from gtts import gTTS
import base64
from tempfile import NamedTemporaryFile
import time
from streamlit_lottie import st_lottie
import requests
import json
import os
from dotenv import load_dotenv
import pkg_resources
#streamlit run TF.py

# 載入環境變數和檢查依賴
try:
    load_dotenv(encoding='utf-8')
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not OPENAI_API_KEY:
        st.error("未找到 OPENAI_API_KEY 環境變數")
        st.info("請在 .env 檔案中設置 OPENAI_API_KEY=您的API金鑰")
        with st.expander("如何設置 .env 檔案"):
            st.markdown("""
            1. 在專案資料夾中找到或創建 `.env` 檔案
            2. 使用記事本或其他文字編輯器以 UTF-8 編碼開啟此檔案
            3. 輸入以下內容（用您的實際 API 金鑰替換）:
            ```
            OPENAI_API_KEY=您的OpenAI_API金鑰
            ```
            4. 儲存檔案並重新啟動應用程式
            
            **取得API金鑰的方法**:
            1. 訪問 [OpenAI API](https://platform.openai.com/)
            2. 註冊或登入您的 OpenAI 帳號
            3. 前往 API 頁面
            4. 創建 API Key
            """)
        st.stop()
except Exception as e:
    st.error(f"載入 .env 檔案時出錯: {e}")
    st.info("請確保 .env 檔案以 UTF-8 編碼儲存，並使用正確的格式")
    st.stop()

# 設置 OpenAI API
try:
    # 使用新版的OpenAI客戶端初始化方式
    from openai import OpenAI
    
    # 創建OpenAI客戶端
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    st.error(f"設置 OpenAI API 時出錯: {e}")
    st.info("請確認您的 API 金鑰是否有效，以及您的 openai 套件版本是否為最新")
    st.stop()

# 頁面配置和樣式設定
st.set_page_config(
    page_title="AI 語音助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition-duration: 0.4s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    .css-1fkbmr4 {
        font-size: 36px;
        font-weight: bold;
        color: #2e4057;
        margin-bottom: 20px;
    }
    .css-q8sbsg p {
        font-size: 18px;
        line-height: 1.6;
    }
    .user-question {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4361ee;
        color: #000000;
    }
    .bot-response {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #3a86ff;
        color: #000000;
    }
    #chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e6e6e6;
        background-color: #fafafa;
        margin-bottom: 20px;
    }
    /* 自訂滾動條樣式 */
    #chat-container::-webkit-scrollbar {
        width: 8px;
    }
    #chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    #chat-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    #chat-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# 加載Lottie動畫
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error(f"無法載入動畫: {e}")
        return None

# 預設動畫數據 (簡單的動畫JSON)
default_animation = {
    "v": "5.8.1",
    "fr": 30,
    "ip": 0,
    "op": 60,
    "w": 100,
    "h": 100,
    "nm": "Loading Animation",
    "ddd": 0,
    "assets": [],
    "layers": [{
        "ddd": 0,
        "ind": 1,
        "ty": 4,
        "nm": "Circle",
        "sr": 1,
        "ks": {
            "o": {"a": 0, "k": 100},
            "r": {
                "a": 1,
                "k": [{"t": 0, "s": [0], "e": [360]}, {"t": 60, "s": [360], "e": [720]}]
            },
            "p": {"a": 0, "k": [50, 50, 0]},
            "a": {"a": 0, "k": [0, 0, 0]},
            "s": {"a": 0, "k": [100, 100, 100]}
        },
        "shapes": [{
            "ty": "el",
            "d": 1,
            "s": {"a": 0, "k": [40, 40]},
            "p": {"a": 0, "k": [0, 0]},
            "nm": "Ellipse Path 1",
            "mn": "ADBE Vector Shape - Ellipse"
        }, {
            "ty": "st",
            "c": {"a": 0, "k": [0.2, 0.6, 1, 1]},
            "o": {"a": 0, "k": 100},
            "w": {"a": 0, "k": 8},
            "lc": 2,
            "lj": 1,
            "ml": 4,
            "nm": "Stroke 1",
            "mn": "ADBE Vector Graphic - Stroke"
        }, {
            "ty": "tr",
            "p": {"a": 0, "k": [0, 0]},
            "a": {"a": 0, "k": [0, 0]},
            "s": {"a": 0, "k": [100, 100]},
            "r": {"a": 0, "k": 0},
            "o": {"a": 0, "k": 100},
            "sk": {"a": 0, "k": 0},
            "sa": {"a": 0, "k": 0}
        }]
    }]
}

# 加載動畫 (使用備用選項)
lottie_bot_url = "https://assets6.lottiefiles.com/packages/lf20_QUshUY.json"
lottie_voice_url = "https://assets9.lottiefiles.com/packages/lf20_ystsffqy.json"

lottie_bot = load_lottieurl(lottie_bot_url) or default_animation
lottie_voice = load_lottieurl(lottie_voice_url) or default_animation

# 側邊欄
with st.sidebar:
    st.markdown("### ⚙️ 設定")
    langs = tts_langs().keys()
    lang = st.selectbox("選擇語言", options=langs, index=12)  # en 12
    
    # 檢查OpenAI套件版本
    try:
        openai_version = pkg_resources.get_distribution("openai").version
        st.markdown(f"🔌 OpenAI SDK 版本: `{openai_version}`")
    except:
        st.markdown("❓ 無法檢測OpenAI版本")
    
    # 添加重設聊天按鈕
    if st.button("🔄 重設聊天", use_container_width=True):
        st.session_state.messages = []
        st.session_state.audio_counter = 0
        st.session_state.user_input = ""
        st.session_state.sidebar_counter = 1
        st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("### 🤖 關於")
    st.markdown("這是一個使用 ChatGPT 3.5 和 gTTS 的 AI 對話與語音合成應用")
    
    # 初始化側邊欄動畫計數器
    if "sidebar_counter" not in st.session_state:
        st.session_state.sidebar_counter = 1
    else:
        st.session_state.sidebar_counter += 1
    
    # 顯示小機器人動畫在側邊欄
    try:
        sidebar_key = f"sidebar_bot_{st.session_state.sidebar_counter}"
        st_lottie(lottie_bot, height=200, key=sidebar_key)
    except Exception as e:
        st.image("https://via.placeholder.com/200x200.png?text=AI+Assistant", caption="AI 助手")

# 主畫面
st.markdown("<h1 style='text-align: center;'>🤖 AI 語音助手</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>與 ChatGPT 3.5 模型即時對話，並聆聽 AI 的回應</h3>", unsafe_allow_html=True)

# 增加分隔線並留出足夠的聊天空間
st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 初始化聊天歷史和其他session_state變數
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "audio_counter" not in st.session_state:
    st.session_state.audio_counter = 0
    
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
    
if "last_ai_response" not in st.session_state:
    st.session_state.last_ai_response = ""
    
if "new_message_submitted" not in st.session_state:
    st.session_state.new_message_submitted = False

# 聊天容器
chat_container = st.container()

# 創建固定高度的聊天容器
container_placeholder = chat_container.empty()

# 顯示聊天記錄
def display_chat_messages():
    messages_html = ""
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            messages_html += f"""<div class='user-question' id='msg_{i}'>
                <strong style='color:#000000;'>您:</strong> 
                <span style='color:#000000;'>{message['content']}</span>
            </div>"""
        else:
            messages_html += f"""<div class='bot-response' id='msg_{i}'>
                <strong style='color:#000000;'>AI:</strong> 
                <span style='color:#000000;'>{message['content']}</span>
            </div>"""
    
    # 自動滾動腳本
    scroll_script = """
    <script>
        function scrollToBottom() {
            var chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }
        
        // 在頁面載入時滾動到底部
        window.addEventListener('load', function() {
            setTimeout(scrollToBottom, 100);
        });
        
        // 在內容改變時滾動到底部
        setTimeout(scrollToBottom, 100);
        
        // 每隔一段時間嘗試滾動，確保總能滾到底部
        setInterval(scrollToBottom, 500);
    </script>
    """
    
    # 渲染帶有訊息的聊天容器和自動滾動腳本
    container_placeholder.markdown(f"""
    <div id="chat-container">
        {messages_html}
    </div>
    {scroll_script}
    """, unsafe_allow_html=True)

# 初始顯示聊天訊息
display_chat_messages()

# 用戶輸入區
with st.container():
    # 初始化輸入欄位的值
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    # 定義送出訊息的回調函數
    def submit_message():
        # 只有當輸入不為空時才處理
        if st.session_state.input_widget.strip():
            # 複製當前輸入以供使用
            current_input = st.session_state.input_widget
            
            # 添加用戶訊息到聊天記錄
            st.session_state.messages.append({"role": "user", "content": current_input})
            
            # 設置標記，表示有新訊息待處理
            st.session_state.new_message_submitted = True
            
            # 清空輸入欄位
            st.session_state.input_widget = ""
            st.session_state.user_input = ""
    
    # 使用session_state控制的輸入欄位
    user_input = st.text_area(
        "✍️ 請輸入您的問題：", 
        value=st.session_state.user_input,
        key="input_widget",
        height=100, 
        placeholder="在這裡輸入您想問的任何問題...", 
        help="您可以用任何語言提問，AI將嘗試理解並回應"
    )
    
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        # 當按下按鈕時，執行submit_message函數
        if st.button("🚀 發送問題", on_click=submit_message, use_container_width=True):
            pass  # 實際動作在回調函數中執行

# 處理新消息和生成AI回應
if "new_message_submitted" in st.session_state and st.session_state.new_message_submitted:
    # 清除標記
    st.session_state.new_message_submitted = False
    
    # 顯示思考中的動畫
    with st.spinner("AI 正在思考中..."):
        # 顯示思考動畫
        thinking_placeholder = st.empty()
        col1, col2, col3 = thinking_placeholder.columns([1, 2, 1])
        with col2:
            try:
                # 使用計數器確保唯一性
                thinking_key = f"thinking_{st.session_state.audio_counter}"
                st_lottie(lottie_bot, height=150, key=thinking_key)
            except Exception:
                st.markdown("⏳ **AI正在處理您的請求...**")
        
        # 發送請求到OpenAI API
        try:
            chat_messages = []
            for msg in st.session_state.messages:
                chat_messages.append({"role": msg["role"], "content": msg["content"]})
            
            # 使用新的客戶端方法
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_messages,
                temperature=0.7,
                max_tokens=1000
            )
            ai_response = response.choices[0].message.content
            
            # 將回應儲存到session_state，以備後續使用
            st.session_state.last_ai_response = ai_response
            
            # 添加AI回應到聊天記錄
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            ai_response = f"抱歉，處理您的請求時發生錯誤: {str(e)}"
            st.error(f"錯誤: {str(e)}")
            st.session_state.last_ai_response = ai_response
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # 清除思考動畫
        thinking_placeholder.empty()
    
    # 增加audio_counter計數器
    st.session_state.audio_counter += 1
    
    # 更新聊天紀錄顯示
    display_chat_messages()
    
    # 語音合成部分
    with st.spinner("正在生成語音..."):
        voice_placeholder = st.empty()
        col1, col2, col3 = voice_placeholder.columns([1, 2, 1])
        with col2:
            try:
                # 使用計數器確保唯一性
                animation_key = f"voice_generating_{st.session_state.audio_counter}"
                st_lottie(lottie_voice, height=150, key=animation_key)
            except Exception:
                st.markdown("🔊 **正在生成語音...**")
        
        try:
            # 使用最新的回應生成語音
            current_ai_response = st.session_state.last_ai_response
            tts = gTTS(current_ai_response, lang=lang, slow=False, lang_check=True)
            
            # 使用計數器創建唯一的臨時檔案名
            audio_count = st.session_state.audio_counter
            temp_file_path = f"temp_audio_{audio_count}.mp3"
            
            # 保存音訊檔案
            tts.save(temp_file_path)
            
            with open(temp_file_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                
                # 清除語音動畫
                voice_placeholder.empty()
                
                # 顯示語音播放器，使用計數器確保每次都重新載入
                audio_key = f"audio_response_{audio_count}"
                st.markdown(f"<h3 style='text-align: center;'>🔊 語音回應 #{audio_count}</h3>", unsafe_allow_html=True)
                
                # 使用HTML5 audio元素，添加唯一ID
                md = f"""<div style="display: flex; justify-content: center;">
                     <audio id="audio_{audio_count}" controls autoplay="true" style="width: 100%; max-width: 500px;">
                     <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                     您的瀏覽器不支援音訊元素。</audio></div>
                     <script>
                     // 確保音訊元素載入後自動播放
                     setTimeout(function() {{
                         var audio = document.getElementById('audio_{audio_count}');
                         if(audio) {{
                             audio.play();
                         }}
                     }}, 300);
                     </script>
                     """
                st.markdown(md, unsafe_allow_html=True)
            
            # 清理臨時檔案
            try:
                os.remove(temp_file_path)
            except:
                pass  # 如果刪除失敗，忽略錯誤
                
        except Exception as e:
            voice_placeholder.empty()
            st.error(f"無法生成語音: {str(e)}")
else:
    st.warning("⚠️ 請輸入您的問題！")
