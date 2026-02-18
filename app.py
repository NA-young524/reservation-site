import streamlit as st
import pandas as pd
import os

# --- 1. 기본 설정 및 데이터 로드 ---
LIMIT_PER_DAY = 500
FILE_NAME = '26reservation.xlsx'

def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME)
        
        # 💡 핵심: 엑셀의 '2026.04.09'를 '2026-04-09'로 변환
        if not df.empty and '행사일' in df.columns:
            df['행사일_temp'] = df['행사일'].astype(str).str.strip(" .")
            # 문자열로 변환 후 .을 -로 교체
            df['행사일_re'] = df['행사일_temp'].astype(str).str.replace('.', '-', regex=False)

        
        return df
    return pd.DataFrame(columns=['행사일', '원명', '인원'])

st.set_page_config(page_title="예약 현황 관리", layout="wide")

# --- 2. 사이드바: 날짜 선택 ---
with st.sidebar:
    st.header("📅 필터 설정")
    selected_date = st.sidebar.date_input("확인할 날짜 선택")
    target_date_str = selected_date.strftime('%y.%m.%d')
    print(target_date_str)
st.title(f"📍 {target_date_str} 예약 현황")

# 데이터 불러오기
df = load_data()
current_booked = 0

if not df.empty:
    # 날짜 컬럼을 문자열로 통일 (비교를 위해)
    df['행사일'] = df['행사일'].astype(str)
    # 선택한 날짜의 인원만 합산
    print(df)
    
    current_booked = df[df['행사일_temp'] == target_date_str]['인원'].sum()
    print(current_booked)
    print(df['행사일'] == target_date_str)
remaining_seats = LIMIT_PER_DAY - current_booked

# --- 3. 컬럼 정의 (여기서 col1, col2, col3가 만들어집니다) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="현재 예약 인원", value=f"{current_booked}명")

with col2:
    # 잔여석 표시 (0보다 작아지면 초과분 표시)
    if remaining_seats < 0:
        st.metric(label="수용 가능 잔여석", value="0명", delta=f"{remaining_seats} (초과)", delta_color="inverse")
    else:
        st.metric(label="수용 가능 잔여석", value=f"{remaining_seats}명", delta=f"{remaining_seats}명 남음")

with col3:
    occupancy_rate = (current_booked / LIMIT_PER_DAY) * 100
    st.metric(label="예약률", value=f"{occupancy_rate:.1f}%")

# --- 4. 상태별 색상 띠 표시 ---
# 인원 상태에 따라 배경색 결정
if remaining_seats < 0:
    status_color = "#FF4B4B"  # 빨강 (초과)
    status_text = "❌ 예약 마감 (인원 초과)"
elif remaining_seats <= 50:
    status_color = "#FFA500"  # 주황 (임박)
    status_text = "⚠️ 예약 마감 임박"
else:
    status_color = "#28A745"  # 초록 (여유)
    status_text = "✅ 예약 가능"

st.markdown(f"""
    <div style="background-color: {status_color}; padding: 15px; border-radius: 10px; text-align: center; margin-top: 20px;">
        <h2 style="color: white; margin: 0;">{status_text}</h2>
    </div>
    """, unsafe_allow_html=True)

st.write("") # 여백
st.progress(min(max(current_booked / LIMIT_PER_DAY, 0.0), 1.0))

# --- 5. 상세 명단 표 ---
st.subheader("📋 상세 예약자 명단")
day_list = df[df['행사일'] == target_date_str]

if not day_list.empty:
    st.dataframe(day_list[['원명', '인원']], use_container_width=True)
else:
    st.info("선택한 날짜에 예약 데이터가 없습니다.")