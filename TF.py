import cv2
import mediapipe as mp
import streamlit as st
import numpy as np
import tempfile
import time
from PIL import Image

# 設置頁面配置為寬模式
st.set_page_config(layout="wide")

# 設置頁面標題
st.title("人臉網格檢測應用")
st.write("此應用程式使用MediaPipe進行人臉網格檢測")

# 選項卡設置
tab1, tab2, tab3 = st.tabs(["即時攝像頭", "影片處理", "圖片處理"])

# 設置MediaPipe
mpd = mp.solutions.drawing_utils
mpfm = mp.solutions.face_mesh
dspec = mpd.DrawingSpec((0, 255, 0), 1, 1)
cspec = mpd.DrawingSpec((128, 128, 128), 1, 1)
cpoint = mpfm.FACEMESH_TESSELATION

# 初始化 FaceMesh
fm = mpfm.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 處理函數
def process_image(img):
    imgrgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = fm.process(imgrgb)
    
    if results.multi_face_landmarks:
        for f_landmarks in results.multi_face_landmarks:
            mpd.draw_landmarks(
                img, 
                landmark_list=f_landmarks, 
                connections=cpoint,
                landmark_drawing_spec=dspec,
                connection_drawing_spec=cspec
            )
    
    return img

# 選項卡1：即時攝像頭
with tab1:
    st.header("即時攝像頭模式")
    st.write("使用您的攝像頭拍照並進行人臉網格檢測")
    
    camera_image = st.camera_input("啟動攝像頭")
    
    if camera_image is not None:
        bytes_data = camera_image.getvalue()
        img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # 處理圖像
        processed_img = process_image(img)
        
        # 顯示處理後的圖像
        st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), caption="處理後的圖像", use_column_width=True)

# 選項卡2：影片處理
with tab2:
    st.header("影片處理模式")
    st.write("上傳影片並進行人臉網格檢測")
    
    uploaded_video = st.file_uploader("上傳影片", type=['mp4', 'mov', 'avi', 'asf', 'm4v'])
    
    if uploaded_video is not None:
        # 保存上傳的影片到臨時文件
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())
        vf = cv2.VideoCapture(tfile.name)
        
        # 顯示原始影片的基本信息
        fps = vf.get(cv2.CAP_PROP_FPS)
        frame_count = int(vf.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        st.write(f"影片資訊: {frame_count} 幀, {fps:.2f} FPS, 時長約 {duration:.2f} 秒")
        
        # 進度條
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 設置輸出影片參數
        stframe = st.empty()
        output_frames = []
        
        # 處理進度選項
        skip_frames = st.slider("設置處理速度（跳過幀數）", 1, 10, 2)
        
        # 開始處理按鈕
        start_button = st.button("開始處理")
        stop_button = st.button("停止處理")
        
        processing = False
        
        if start_button:
            processing = True
            
            frame_counter = 0
            while vf.isOpened() and processing:
                ret, frame = vf.read()
                if not ret:
                    break
                
                # 只處理每隔skip_frames的幀
                if frame_counter % skip_frames == 0:
                    # 處理圖像
                    processed_frame = process_image(frame)
                    
                    # 顯示處理中的幀
                    stframe.image(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB), caption=f"處理中: 幀 {frame_counter}/{frame_count}", use_column_width=True)
                    
                    # 輸出處理後的幀
                    output_frames.append(processed_frame)
                    
                    # 更新進度條
                    progress = int(frame_counter / frame_count * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"處理進度: {progress}%")
                    
                    # 檢查是否需要停止
                    if stop_button:
                        processing = False
                        break
                
                frame_counter += 1
            
            vf.release()
            
            if len(output_frames) > 0:
                st.success("處理完成！")
                
                # 顯示處理後的視頻（選擇一些幀作為示例）
                st.subheader("處理結果示例")
                col1, col2, col3 = st.columns(3)
                
                indices = [0, len(output_frames)//2, len(output_frames)-1]
                cols = [col1, col2, col3]
                
                for i, col in zip(indices, cols):
                    if i < len(output_frames):
                        col.image(cv2.cvtColor(output_frames[i], cv2.COLOR_BGR2RGB), use_column_width=True)

# 選項卡3：圖片處理
with tab3:
    st.header("圖片處理模式")
    st.write("上傳圖片並進行人臉網格檢測")
    
    uploaded_file = st.file_uploader("選擇一張圖片", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # 將上傳的文件轉換為圖像
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # 創建兩列並排顯示
        col1, col2 = st.columns(2)
        
        # 顯示原始圖像
        with col1:
            st.subheader("原始圖像")
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_column_width=True)
        
        # 處理圖像並顯示
        processed_img = process_image(img.copy())
        
        with col2:
            st.subheader("處理後的圖像")
            if any(landmark in locals() for landmark in ['f_landmarks', 'results.multi_face_landmarks']):
                st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), use_column_width=True)
            else:
                st.warning("未檢測到人臉")
                st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), use_column_width=True)

# 添加說明
st.markdown("""
### 使用說明
- **即時攝像頭模式**：允許瀏覽器使用您的攝像頭，對準攝像頭並拍照。
- **影片處理模式**：上傳影片檔案，應用會處理並顯示帶有人臉網格的結果。
- **圖片處理模式**：上傳圖片，應用會處理並顯示帶有人臉網格的結果。

使用 MediaPipe 技術檢測人臉並生成面部網格。這對於面部識別、表情分析和 AR 應用很有用。
""") 
