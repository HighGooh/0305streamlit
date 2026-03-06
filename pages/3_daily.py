from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json
from mariadb_crud import save, saveMany, findAll

st.set_page_config(
  page_title="일간(‘daily’) 랭킹 수집",
  page_icon="💗",
  layout="wide",
)

if 'category_index' not in st.session_state:
	st.session_state.category_index = ''

Path1_option = ["10"]
Path2_option = ["0","14","15","16","18","85"]


category1_options = ["공연"]
category2_options = ["전체","콘서트","연극","뮤지컬","클래식/무용","아동/가족"]


selected1_category = st.selectbox(label="카테고리", 
    options=category1_options,
    index=None,
    placeholder="수집 대상을 선택하세요.")

# 전체 카테고리 선택
if selected1_category :
  st.session_state.category1_index = Path1_option[category1_options.index(selected1_category)]
  url = (
    f"https://mapi.ticketlink.co.kr/mapi/ranking/genre/daily?"
    f"categoryId={st.session_state.category1_index}"
    f"&categoryId2=0"
    f"&categoryId3=0"
    f"&menu=RANKING"
    )
else:
  st.session_state.category1_index = 0


# 공연 카테고리를 골랐을 때 세부 카테고리가 생성
if selected1_category == "공연":
   selected2_category = st.selectbox(label="공연 세부 카테고리", 
    options=category2_options,
    index=None,
    placeholder="수집 대상을 선택하세요.")
   if selected2_category :
    st.session_state.category2_index = Path2_option[category2_options.index(selected2_category)]
# 세부 카테고리를 골랐을 때 url 생성    
    url = (
    f"https://mapi.ticketlink.co.kr/mapi/ranking/genre/daily?"
    f"categoryId={st.session_state.category1_index}"
    f"&categoryId2={st.session_state.category2_index}"
    f"&categoryId3=0"
    f"&menu=RANKING"
    )
# 세부 카테고리를 선택하지 않으면 선택한 카테고리 전체의 url 생성
   else: url = (
    f"https://mapi.ticketlink.co.kr/mapi/ranking/genre/daily?"
    f"categoryId={st.session_state.category1_index}"
    f"&categoryId2=0"
    f"&categoryId3=0"
    f"&menu=RANKING"
    )
      
# 데이터 수집
def getData():
  try:
    st.text(f"URL: {url}")
    res = get(url)
    if res.status_code == 200:
      st.text("API 데이터 수집 시작!")
      json_data = json.loads(res.text)
      rankingList = json_data.get("data", {}).get("rankingList", [])
      tab1, tab2 = st.tabs(["json 데이터", "DataFrame"])
      if st.session_state.category2_index != '0' :
        sql1 = f"""
              select 1
              """
        sql2 = f"""
            INSERT INTO edu.`ticket` 
            (`productId`, `reserveCount`, `categoryId1`, `categoryId2`, `categoryId3`, `previousRanking`, `reserveRate`,`productName`, `startDate`,`endDate`,`hallName`,`urlSuffix`,`imgUrl`,`saleStatus`)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                reserveCount=VALUES(reserveCount),
                categoryId1=VALUES(categoryId1),
                categoryId2=VALUES(categoryId2),
                categoryId3=VALUES(categoryId3),
                previousRanking=VALUES(previousRanking),
                reserveRate=VALUES(reserveRate),
                productName=VALUES(productName),
                startDate=VALUES(startDate),
                endDate=VALUES(endDate),
                hallName=VALUES(hallName),
                urlSuffix=VALUES(urlSuffix),
                imgUrl=VALUES(imgUrl),
                saleStatus=VALUES(saleStatus)
            """
        values = [(row["productId"], row["reserveCount"], row["categoryId1"], row["categoryId2"], row["categoryId3"], row["previousRanking"], row["reserveRate"], row["productName"], row["startDate"], row["endDate"], row["hallName"], row["urlSuffix"], row["imgUrl"], row["saleStatus"]) for row in rankingList]
        saveMany(sql1, sql2, values)
        st.text("데이터 저장 완료!")
      

      with tab1:
        st.text("json 출력")
        st.json(json_data.get("data", {}), expanded=False, width="stretch")
        st.html("<hr/>")
        st.text("랭킹 목록 출력")
        st.json(rankingList, expanded=False, width="stretch")
      with tab2:
        st.text("DataFrame 출력")
        st.dataframe(pd.DataFrame(rankingList))
  except Exception as e:
    return 0
  return 1

def clearData() :
  sql1 = f"""
          TRUNCATE TABLE `edu`.`ticket`
          """
  save(sql1)

btn_col1, btn_col2 , btn_col3 = st.columns([1, 1, 1])

# 수집 버튼 클릭 처리
with btn_col1:
    if st.button("수집하기"):
        if selected1_category:
            # 버튼을 눌렀을 때 실행할 로직을 세션 상태에 저장하거나 직접 실행
            # 하지만 여기서 바로 st.write를 하면 컬럼 안에 갇히게 됩니다.
            st.session_state.run_type = "collect"
        else:
            st.warning("메뉴를 선택해주세요")

# 차트 버튼 클릭 처리
with btn_col2:
    if st.button("차트그리기"):
        st.session_state.run_type = "chart"

with btn_col3:
    if st.button("수집 초기화"):
        st.session_state.run_type = "clear"

# ---------------------------------------------------------
# 2. 결과 출력 영역 (컬럼 블록 밖에서 실행 -> 전체 너비 사용)
# ---------------------------------------------------------
st.divider() # 시각적 구분을 위한 선

if "run_type" in st.session_state:
    if st.session_state.run_type == "collect":
        # getData() 내부의 st.text("데이터 수집 완료!") 등이 전체 너비로 나옵니다.
        getData() 

    elif st.session_state.run_type == "clear":
        clearData()
        st.text("수집 내용을 초기화 하였습니다")
    # elif st.session_state.run_type == "chart":
    #     # 차트 역시 화면 전체 너비를 사용하여 시원하게 그려집니다.
    #     makeChart()
