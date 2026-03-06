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


Path1_option = ["10","20","30","40","50"]
Path2_option = ["0","14","15","16","17","18","19","20","21"]
Path3_option = ["0","21","22","23","24","25"]


category1_options = ["공연","스포츠","전시/행사","레저","영화(특별상영 등)"]
category2_options = ["전체","콘서트","연극","뮤지컬","클래식/무용","아동/가족","복합장르","국악","오페라"]
category3_options = ["전체","축구","야구","농구","배구","e스포츠"]


selected1_category = st.selectbox(label="카테고리", 
	options=category1_options,
	index=None,
	placeholder="수집 대상을 선택하세요.")

# 전체 카테고리 선택
if selected1_category :
  st.session_state.category1_index = Path1_option[category1_options.index(selected1_category)]
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

# 스포츠 카테고리를 골랐을 때 세부 카테고리가 생성
if selected1_category == "스포츠":
  selected3_category = st.selectbox(label="스포츠 세부 카테고리", 
    options=category3_options,
    index=None,
    placeholder="수집 대상을 선택하세요.")
  if selected3_category :
    st.session_state.category3_index = Path3_option[category3_options.index(selected3_category)]
# 세부 카테고리를 골랐을 때 url 생성
    url = (
    f"https://mapi.ticketlink.co.kr/mapi/ranking/genre/daily?"
    f"categoryId={st.session_state.category1_index}"
    f"&categoryId2={st.session_state.category3_index}"
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
      print(rankingList[1]["startDate"])
      sql1 = f"""
            select 1
            """
      sql2 = f"""
          INSERT INTO edu.`ticket` 
          (`productId`, `reserveCount`, `categoryId1`, `categoryId2`, `categoryId3`, `previousRanking`, `reserveRate`, `startDate`,`endDate`,`hallName`,`urlSuffix`,`imgUrl`,`saleStatus`)
          VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE
              reserveCount=VALUES(reserveCount),
              categoryId1=VALUES(categoryId1),
              categoryId2=VALUES(categoryId2),
              categoryId3=VALUES(categoryId3),
              previousRanking=VALUES(previousRanking),
              reserveRate=VALUES(reserveRate),
              startDate=VALUES(startDate),
              endDate=VALUES(endDate),
              hallName=VALUES(hallName),
              urlSuffix=VALUES(urlSuffix),
              imgUrl=VALUES(imgUrl),
              saleStatus=VALUES(saleStatus)
          """
      values = [(row["productId"], row["reserveCount"], row["categoryId1"], row["categoryId2"], row["categoryId3"], row["previousRanking"], row["reserveRate"], row["startDate"], row["endDate"], row["hallName"], row["urlSuffix"], row["imgUrl"], row["saleStatus"]) for row in rankingList]
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

if st.button(f"수집하기"):
  getData()
