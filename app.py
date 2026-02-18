import streamlit as st
import pandas as pd
import os

# --- 1. 기본 설정 및 데이터 로드 ---
LIMIT_PER_DAY = 500
FILE_NAME = '26reservation.xlsx'

# 데이터 로드 함수 (캐싱 처리하여 성능 최적화)
def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_excel(FILE_NAME)
        
        # 💡 날짜 처리: 데이터 비교를 위해 문자열 변환 및 전처리
        if not df.empty and '행사일' in df.columns:
            # 엑셀의 '2026.04.09' 형태를 공백 제거 후 문자열로 유지
            df['행사일_temp'] = df['행사일'].astype(str).str.strip(" .")
            df['행사일_re'] = df['행사일_temp'].astype(str).str.replace('.', '-', regex=False)
        return df
    # 파일이 없을 경우 빈 데이터프레임 생성
    return pd.DataFrame(columns=['행사일', '원명', '인원'])

st.set_page_config(page_title="예약 현황 관리", layout="wide")

# --- 2. 사이드바: 날짜 선택 ---
with st.sidebar:
    st.header("📅 필터 설정")
    selected_date = st.date_input("확인할 날짜 선택")
    # 엑셀 형식에 맞춰 '26.04.09' 형태로 변환 (필요시 %Y로 수정 가능)
    target_date_str = selected_date.strftime('%y.%m.%d')
    
    st.divider()
    st.info(f"선택된 날짜: {target_date_str}")

st.title(f"📍 {target_date_str} 예약 현황 및 관리")

# 데이터 불러오기
df = load_data()
current_booked = 0

# 선택한 날짜에 해당하는 데이터 필터링
if not df.empty:
    current_booked = df[df['행사일_temp'] == target_date_str]['인원'].sum()

remaining_seats = LIMIT_PER_DAY - current_booked

# --- 3. 대시보드 (Metric) 표시 ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="현재 예약 인원", value=f"{current_booked}명")

with col2:
    if remaining_seats < 0:
        st.metric(label="수용 가능 잔여석", value="0명", delta=f"{remaining_seats} (초과)", delta_color="inverse")
    else:
        st.metric(label="수용 가능 잔여석", value=f"{remaining_seats}명", delta=f"{remaining_seats}명 남음")

with col3:
    occupancy_rate = (current_booked / LIMIT_PER_DAY) * 100
    st.metric(label="예약률", value=f"{occupancy_rate:.1f}%")

# --- 4. 상태별 색상 띠 및 프로그레스 바 ---
if remaining_seats < 0:
    status_color, status_text = "#FF4B4B", "❌ 예약 마감 (인원 초과)"
elif remaining_seats <= 50:
    status_color, status_text = "#FFA500", "⚠️ 예약 마감 임박"
else:
    status_color, status_text = "#28A745", "✅ 예약 가능"

st.markdown(f"""
    <div style="background-color: {status_color}; padding: 15px; border-radius: 10px; text-align: center; margin-top: 20px;">
        <h2 style="color: white; margin: 0;">{status_text}</h2>
    </div>
    """, unsafe_allow_html=True)

st.write("") 
st.progress(min(max(current_booked / LIMIT_PER_DAY, 0.0), 1.0))

# --- 5. 실시간 수정 및 저장 기능 (중심부) ---
st.divider()
st.subheader("📋 전체 예약 명단 편집")
st.caption("표 안의 내용을 직접 수정하거나 행을 추가/삭제할 수 있습니다. 수정 후 반드시 아래 '변경사항 저장' 버튼을 누르세요.")

# 전체 데이터를 에디터로 표시 (행 추가/삭제 가능)
# num_rows="dynamic"을 통해 행 추가 기능 활성화
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor")

# 저장 로직
if st.button("💾 변경사항을 엑셀 파일로 저장하기", use_container_width=True):
    try:
        # 엑셀 파일로 덮어쓰기 (기존 파일은 삭제되고 새 데이터로 생성됨)
        edited_df.to_excel(FILE_NAME, index=False)
        st.success(f"✅ '{FILE_NAME}' 파일에 성공적으로 저장되었습니다!")
        # 화면 새로고침하여 메트릭 등에 반영
        st.rerun()
    except PermissionError:
        st.error("❌ 저장 실패: 엑셀 파일이 다른 프로그램(Excel 등)에서 열려 있습니다. 파일을 닫고 다시 시도하세요.")
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

# --- 6. 상세 명단 확인 (읽기 전용 필터뷰) ---
st.divider()
st.subheader(f"🔍 {target_date_str} 상세 명단")
day_list = edited_df[edited_df['행사일'] == target_date_str]

if not day_list.empty:
    st.table(day_list[['원명', '인원']])
else:
    st.info(f"{target_date_str}에 등록된 예약 데이터가 없습니다.")
