from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json

st.set_page_config(
  page_title="yes24 수집",
  page_icon="💗",
  layout="wide",
)

if 'category_index' not in st.session_state:
	st.session_state.category_index = ''

# Yes24 베스트셀러 URL 예시
yes24 = "https://www.yes24.com/product/category/weekbestseller"
categoryNumber = st.session_state.category_index
pageNumber = 1
pageSize = 40
type = "week"
saleYear = 2026
weekNo = 1149
sex = "A"
viewMode = "thumb"

category_info = ["001","002"]
category_options = ["국내 도서","국외 도서"]
# weekNo_options = [1149,1150,1151,1152,1153,1154,1155,1156,1157]
# weekNo_options2 = [1149,1150,1151,1152,1153,1154,1155,1156,1157]


    
# if 'weekNo_index' not in st.session_state:
# 	st.session_state.weekNo_index = ''
   
selected1 = st.selectbox(label="카테고리", 
	options=category_options,
	index=None,
	placeholder="수집 대상을 선택하세요.")

# selected2 = st.selectbox(label="날짜", 
# 	options=weekNo_options,
# 	index=None,
# 	placeholder="수집 대상을 선택하세요.")

# 데이터 수집
def getData():
  try:
    url = (
      f"{yes24}?"
      f"categoryNumber={categoryNumber}&" #화면 왼쪽의 대장르 001: 국내 / 002: 외국도서
      f"pageNumber={pageNumber}&" #페이지 네이션
      f"pageSize={pageSize}&" # 한 번에 가져오는 권 수 고정 (40)
      f"type={type}&"
      f"saleYear={saleYear}&"
      f"weekNo={weekNo}&"
      f"sex={sex}&"
      f"viewMode={viewMode}"
    )
    st.text(f"URL: {url}")
    res = get(url)
    if res.status_code == 200:
      st.text(f"yes24 {selected1} 주별 베스트 수집 시작!")
      books = [] # { 도서명, 저자, 별점 }
      soup = bs(res.text, "html.parser")
      trs = soup.select("#yesBestList .itemUnit")
      for item in trs:
        title = item.select_one(".gd_name").get_text(strip=True)
        print(1)
        author_span = item.select_one("span.authPub.info_auth")
        author = author_span.select_one("a").get_text(strip=True)
        # star_span = item.select_one("span.rating_grade")
        star_span = "0"
        # star = star_span.select_one("em.yes_b").get_text(strip=True)
        star = "0"
        books.append({ "title": title, "author": author, "star": star })
      tab1, tab2, tab3 = st.tabs(["HTML 데이터", "JSON 데이터", "DataFrame"])
      with tab1:
        st.text("html 출력")
        st.html(trs)
      with tab2:
        st.text("JSON 출력")
        json_string = json.dumps(books, ensure_ascii=False, indent=2)
        st.json(body=json_string, expanded=True, width="stretch")
      with tab3:
        st.text("DataFrame 출력")
        st.dataframe(pd.DataFrame(books))
  except Exception as e:
    return 0
  return 1

if st.button(f"수집하기"):
    getData()  
    # st.session_state.weekNo_index = selected2
  # elif selected1 :
  #   st.session_state.category_index = selected1
  #   # st.session_state.weekNo_index = 1157

if selected1 :
  st.session_state.category_index = category_info[category_options.index(selected1)]


	