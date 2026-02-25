import streamlit as st
import json
import os
import random
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ Thống Luyện Toán", layout="wide")

# --- CSS ĐẶC TRỊ (Giữ nguyên giao diện chuẩn) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1A1C23 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 25px !important;
        margin-bottom: 25px !important;
    }
    .stMarkdown p, span, label { color: white !important; font-size: 19px; }
    .q-title { color: #58A6FF !important; font-weight: bold; font-size: 20px; }
    
    /* ẨN LABEL RADIO THỪA */
    div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] { display: none !important; }
    
    /* CHIA CỘT ĐÁP ÁN GRID 1-2-4 */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
        gap: 15px !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > div { display: contents !important; }
    
    /* THẺ ĐÁP ÁN */
    div[data-testid="stRadio"] label {
        background-color: #21262D !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        display: flex !important;
        width: 100% !important;
    }
    
    /* NÚT NỘP BÀI CANH GIỮA */
    .stFormSubmitButton { display: flex !important; justify-content: center !important; }
    .stFormSubmitButton button {
        background-color: #238636 !important;
        color: white !important;
        padding: 15px 80px !important;
        border-radius: 30px !important;
        font-weight: bold;
    }
    
    /* NÚT LIÊN KẾT TRANG CHỦ */
    .link-button {
        display: inline-block; padding: 12px; border-radius: 8px;
        text-decoration: none; font-weight: bold; text-align: center; width: 100%;
    }
    .yt-btn { background-color: #FF0000; color: white !important; }
    .reg-btn { background-color: #007BFF; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- HÀM XỬ LÝ DỮ LIỆU ---
def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"topics": []}

def save_result(name, grade, topic_title, score, total):
    file_path = 'ket_qua_lam_bai.csv'
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    new_data = {"Thời gian": [now], "Họ tên": [name], "Lớp": [grade], "Chủ đề": [topic_title], "Điểm số": [f"{score}/{total}"]}
    df = pd.DataFrame(new_data)
    if not os.path.isfile(file_path):
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(file_path, mode='a', index=False, header=False, encoding='utf-8-sig')

def generate_quiz_from_banks(topic_data):
    selected = []
    banks = topic_data.get('question_banks', {})
    for i in range(1, 6):
        bank = banks.get(f"bank_{i}", [])
        if bank: selected.append(random.choice(bank))
    return selected

# --- QUẢN LÝ TRẠNG THÁI ---
if "current_page" not in st.session_state: st.session_state.current_page = "Home"
if "step" not in st.session_state: st.session_state.step = 1
if "quiz_list" not in st.session_state: st.session_state.quiz_list = []
if "video_q_selected" not in st.session_state: st.session_state.video_q_selected = None

data = load_data()

# --- GIAO DIỆN TRANG CHỦ ---
if st.session_state.current_page == "Home":
    st.markdown("<h1 style='text-align: center;'>🎓 HỆ THỐNG LUYỆN TOÁN</h1>", unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1: st.markdown('<a href="#" class="link-button yt-btn">📺 YouTube Bài Giảng</a>', unsafe_allow_html=True)
    with col_l2: st.markdown('<a href="#" class="link-button reg-btn">📝 Đăng Ký Học Online</a>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("📚 Chọn chủ đề học tập:")
    for topic in data.get("topics", []):
        if st.button(f"📖 {topic['title']}", key=topic['id'], use_container_width=True):
            st.session_state.current_page = topic['id']
            st.session_state.step = 1
            st.session_state.quiz_list = generate_quiz_from_banks(topic)
            v_quizzes = topic.get('video_quizzes', [])
            if v_quizzes: st.session_state.video_q_selected = random.choice(v_quizzes)
            st.rerun()

    # --- PHẦN BẢO MẬT CHO GIÁO VIÊN ---
    st.write("<br><br><br>", unsafe_allow_html=True) # Đẩy xuống dưới cùng trang
    with st.sidebar: # Đưa phần quản trị vào thanh bên trái để kín đáo
        st.write("---")
        pw = st.text_input("Quản trị viên:", type="password")
        if pw == "admin123": # <--- MẬT KHẨU CỦA BẠN Ở ĐÂY
            st.success("Xin chào thầy/cô!")
            if os.path.exists('ket_qua_lam_bai.csv'):
                res_df = pd.read_csv('ket_qua_lam_bai.csv')
                st.download_button("📥 Tải bảng điểm (Excel)", data=res_df.to_csv(index=False).encode('utf-8-sig'), file_name="bang_diem.csv")
                st.dataframe(res_df)
            else:
                st.info("Chưa có dữ liệu.")

# --- TRANG LÀM BÀI ---
else:
    topic = next((t for t in data["topics"] if t["id"] == st.session_state.current_page), None)
    if st.button("⬅️ Quay lại"):
        st.session_state.current_page = "Home"
        st.rerun()

    if st.session_state.step == 1:
        st.video(topic['video_url'])
        with st.container(border=True):
            if st.session_state.video_q_selected:
                q_v = st.session_state.video_q_selected
                st.write(f"❓ {q_v['question']}")
                ans_v = st.text_input("Trả lời:", key="v_ans").strip()
                if st.button("Xác nhận"):
                    if ans_v.lower() == str(q_v['answer']).lower():
                        st.session_state.step = 2
                        st.rerun()
                    else: st.error("Sai rồi em ơi!")
    
    elif st.session_state.step == 2:
        st.markdown(f"## 📝 {topic['title']}")
        c1, c2 = st.columns(2)
        with c1: std_name = st.text_input("👤 Họ tên:")
        with c2: std_class = st.text_input("🏫 Lớp:")

        with st.form("quiz_form"):
            user_answers = {}
            labels = ["A", "B", "C", "D"]
            for i, q in enumerate(st.session_state.quiz_list):
                with st.container(border=True):
                    st.markdown(f'<span class="q-title">Câu hỏi {i+1}:</span> {q["q"]}', unsafe_allow_html=True)
                    user_answers[i] = st.radio(f"q_{i}", [f"{labels[j]}. {opt}" for j, opt in enumerate(q['options'])], key=f"r_{i}", horizontal=True, label_visibility="collapsed", index=None)
            
            if st.form_submit_button("NỘP BÀI"):
                if not std_name or not std_class:
                    st.warning("Nhập tên và lớp em nhé!")
                elif any(user_answers[i] is None for i in range(len(st.session_state.quiz_list))):
                    st.error("Em chưa chọn hết đáp án!")
                else:
                    score = sum(1 for i, q in enumerate(st.session_state.quiz_list) if user_answers[i].split(". ", 1)[1] == q['a'])
                    save_result(std_name, std_class, topic['title'], score, len(st.session_state.quiz_list))
                    st.balloons()
                    st.success(f"Kết quả: {score}/{len(st.session_state.quiz_list)}. Đã lưu điểm!")