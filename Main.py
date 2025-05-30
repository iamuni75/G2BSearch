import pandas as pd
import streamlit as st

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from G2B_Search import G2B_search_by_keywords, preG2B_search_by_keywords
from Tools import markdown_to_excel


st.set_page_config(layout="wide")

st.title("📝나라장터(G2B) 검색")
# st.markdown("> 하나의 검색어 마다 날짜 기준으로 최대 20개 까지 검색됩니다.")
# st.markdown("---")
search_status = st.empty()


# 검색 진행상태를 보여주는 콜백 함수
def progress_callback(message):
    search_status.markdown(message)
    

# 본 공고 검색 결과에 대한 항목의 마크다운을 저장하는 세션
if "main_searched_list_md" not in st.session_state:
    st.session_state["main_searched_list_md"] = ""
# 본 공고 검색 결과 개수를 저장하는 세션
if "main_searched_list_count" not in st.session_state:
    st.session_state["main_searched_list_count"] = 0

# 사전규격 검색 결과에 대한 항목의 마크다운을 저장하는 세션
if "pre_searched_list_md" not in st.session_state:
    st.session_state["pre_searched_list_md"] = ""
# 본 공고 검색 결과 개수를 저장하는 세션
if "pre_searched_list_count" not in st.session_state:
    st.session_state["pre_searched_list_count"] = 0


# 검색키워드 설정하는 사이드바 
with st.sidebar:
    
    # 체크박스 항목 리스트 설정
    # keywords_options = ["UPIS", "도시계획정보", "통합인허가", "개발행위", "IPSS", "재해취약성", "도시기후변화", "토지적성", "적성평가", "기초조사", "국토이용정보", "KLIP", "GIS", "지리정보", "공간정보", "기본계획", "관리계획", "재정비", "GIS 구축", "DB 구축", "소규모 공공시설 안전점검", "소규모 공공시설 정비계획", "소규모 공공시설 일제조사", "DB", "시스템", "개발", "정보화", "정보시스템", "SW", "플랫폼", "KRAS", "용도지구", "용도지역", "지적재조사", "연속주제도", "농업생산", "기반시설", "관정", "농업기반", "공업지역", "성장관리"]
    df = pd.read_excel("keywords.xlsx")
    keywords_options = df.iloc[:, 0].dropna().astype(str).tolist()

    for option in keywords_options:
        if option not in st.session_state:
            st.session_state[option] = True

    # 검색날짜 설정. 기본값은 어제 일자로 설정
    search_date = st.date_input("검색 시작일", date.today() - timedelta(days=1), min_value=date.today() - relativedelta(months=1))
    input_keywords = st.text_input("추가 검색어 입력", placeholder="검색어가 여러개면 콤마(,)로 구분")

    if st.button("🔍 검색 시작", use_container_width=True, key="search1"):
        # 검색결과 세션 초기화
        st.session_state["main_searched_list_md"] = ""
        st.session_state["main_searched_list_count"] = 0
        st.session_state["pre_searched_list_md"] = ""
        st.session_state["pre_searched_list_count"] = 0

        # 선택된 키워드
        selected_keywords = [k for k in keywords_options if st.session_state[k]]

        if input_keywords.strip() != "":
            # 입력한 추가 키워드를 콤마로 나누고, 앞뒤의 공백을 제거함
            added_keywords = [item.strip() for item in input_keywords.split(",")]
            # 선택된 키워드와 추가한 검색어를 조합한 최종 검색 키워드 리스트 만들기
            search_keywords = list(set(added_keywords + selected_keywords))
        else:
            search_keywords = selected_keywords
        
        # 본공고 검색 결과를 처리
        g2b_search_result = G2B_search_by_keywords(search_keywords, search_date, callback=progress_callback)
        if g2b_search_result != None:   # 검색 결과가 있을 경우
            st.session_state["main_searched_list_md"] = g2b_search_result["searched_list_md"]
            st.session_state["main_searched_list_count"] = g2b_search_result["total_count"]

        preG2b_search_result = preG2B_search_by_keywords(search_keywords, search_date, callback=progress_callback)
        if preG2b_search_result != None:   # 검색 결과가 있을 경우
            st.session_state["pre_searched_list_md"] = preG2b_search_result["searched_list_md"]
            st.session_state["pre_searched_list_count"] = preG2b_search_result["total_count"]

    st.caption("❗️키워드 당 최대 50개씩 검색됨")
    st.markdown("---")
    st.text("검색어 선택")
    # 버튼클릭 시 세션스테이트 전부 변경
    btn_select_all, btn_unselect = st.columns(2)
    if btn_select_all.button("전체선택", icon="✅", use_container_width=True):
        for option in keywords_options:
            st.session_state[option] = True

    if btn_unselect.button("전체 미선택", icon="❎", use_container_width=True):
        for option in keywords_options:
            st.session_state[option] = False

    # 전체 체크박스 표시
    for option in keywords_options:    
        st.checkbox(option, value=st.session_state[option], key=option)

    # st.button("🔍G2B 검색", use_container_width=True, key="search2")


# -----------------
# 검색결과 화면 설정
# -----------------
# 검색 진행상황 보여주는 부분 지우기
search_status.empty()
main_searched_count = st.session_state['main_searched_list_count']
pre_searched_count = st.session_state['pre_searched_list_count']
tab_pre, tab_main = st.tabs([f"사전규격({pre_searched_count}건)", f"입찰공고({main_searched_count}건)"])

with tab_pre:
    st.subheader(f"✅ 검색결과({pre_searched_count}건)")
    st.write(st.session_state["pre_searched_list_md"])


    # 마크다운을 엑셀로 다운로드하기
    if st.session_state["pre_searched_list_md"] != "":
        excel_data = markdown_to_excel(st.session_state["pre_searched_list_md"])
        st.download_button("📗엑셀 다운로드", data=excel_data, file_name="preG2b_search_result.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tab_main:
    st.subheader(f"✅ 검색결과({main_searched_count}건)")
    st.write(st.session_state["main_searched_list_md"])


    # 마크다운을 엑셀로 다운로드하기
    if st.session_state["main_searched_list_md"] != "":
        excel_data = markdown_to_excel(st.session_state["main_searched_list_md"])
        st.download_button("📗엑셀 다운로드", data=excel_data, file_name="g2b_search_result.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")