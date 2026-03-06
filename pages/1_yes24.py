from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json
import time
from mariadb_crud import save, saveMany, findAll
import plotly.express as px

st.set_page_config(
  page_title="yes24 수집",
  page_icon="💗",
  layout="wide",
)

def getWeekNo():
  try:
    weekNos = []
    weeks = []
    url = "https://www.yes24.com/product/category/weekbestseller?categoryNumber=001&pageNumber=1&pageSize=24&type=week"
    res = get(url)
    if res.status_code == 200:
      soup = bs(res.text, "html.parser")
      data = soup.select('select#scope_week option')
      for i in data:
        weekNo = i.get('value')
        week = i.get_text(strip=True)
        weekNos.append(weekNo)
        weeks.append(week)
      #  weekNo = data.select('option')
    return (weekNos, weeks)
  except Exception as e:
    return 0


if 'category_index' not in st.session_state:
	st.session_state.category_index = ''

if 'week_index' not in st.session_state:
	st.session_state.week_index = ''

# Yes24 베스트셀러 URL 예시
yes24 = "https://www.yes24.com/product/category/weekbestseller"
categoryNumber = st.session_state.category_index
pageNumber = 1
pageSize = 40
type = "week"
saleYear = 2026
weekNo = st.session_state.week_index
sex = "A"
viewMode = "list"

category_info = ["001","002"]
category_options = ["국내 도서","국외 도서"]
weekNum = getWeekNo()
weekNos = weekNum[0]
weeks = weekNum[1]


    
# if 'weekNo_index' not in st.session_state:
# 	st.session_state.weekNo_index = ''
   
selected1 = st.selectbox(label="카테고리", 
	options=category_options,
	index=None,
	placeholder="수집 대상을 선택하세요.")

selected2 = st.selectbox(label="날짜", 
	options=weeks,
	index=None,
	placeholder="수집 대상을 선택하세요.")


if selected1 and selected2 :
  st.session_state.category_index = category_info[category_options.index(selected1)]
  st.session_state.week_index = weekNos[weeks.index(selected2)]

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
      for i, item in enumerate(trs, start=1):
        # 초기화
        title = "제목 없음"
        author = "작가 미상"
        star = 0
        saleNum = 0
        reviews = 0

        # title
        title_span = item.select_one(".gd_name").get_text(strip=True)
        if title_span:
           title = title_span

        # author
        author_span = item.select_one("span.authPub.info_auth")
        author_test = author_span.select_one("a")
        author = author_test.get_text(strip=True) if author_test else author_span.get_text(strip=True)

        # saleNum
        sale = item.select_one(".saleNum")
        if sale:
           saleNum = int(sale.get_text(strip=True).replace("판매지수 ", "").replace(",", ""))

        # reviews
        review = item.select_one(".txC_blue")
        if review:
          reviews = int(review.get_text(strip=True).replace(",", ""))

        # star
        star_span = item.select_one("span.rating_grade")
        if star_span:
          star = star_span.select_one("em.yes_b").get_text(strip=True)
        
        books.append({ "category": selected1, "weekNo" : st.session_state.week_index, "rank": i, "title": title, "author": author, "star": float(star), "saleNum": saleNum, "reviews": reviews })
      
      # db에 저장
      st.text("데이터 수집 완료!")
      sql1 = f"""
            select 1
            """
      sql2 = f"""
          INSERT INTO edu.`books` 
          (`category`, `weekNo`, `rank`, `title`, `author`, `star`, `saleNum`, `reviews`)
          VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s)
          ON DUPLICATE KEY UPDATE
              category=VALUES(category),
              weekNo=VALUES(weekNo),
              rank=VALUES(rank),
              title=VALUES(title),
              author=VALUES(author),
              star=VALUES(star),
              saleNum=VALUES(saleNum),
              reviews=VALUES(reviews)
          """
      values = [(row["category"], row["weekNo"], row["rank"], row["title"], row["author"], row["star"], row["saleNum"], row["reviews"]) for row in books]
      saveMany(sql1, sql2, values)
      st.text("데이터 저장 완료!")

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
    return print(e)
  return 1

def makeChart():
  sql = f"SELECT * FROM books WHERE `weekNo` = '{st.session_state.week_index}' and `category` = '{selected1}'"
  data = findAll(sql)
  if data:
    df = pd.DataFrame(data)
    # 숫자형 데이터 변환 (콤마 제거 및 타입 변경)
    if df['saleNum'].dtype == 'object':
      df['saleNum'] = df['saleNum'].str.replace(',', '').astype(int)
    df['star'] = pd.to_numeric(df['star'])
    df['reviews'] = pd.to_numeric(df['reviews'])

    # --- 레이아웃 설정 ---
    st.title(f"📚 {selected1} 카테고리 분석 리포트")
    st.caption(f"기준 주차: {selected2}")
    
    col1, col2 = st.columns(2)

    with col1:
        # 차트 1: 도서별 판매량 TOP 10 (막대 차트)
        # 순위가 낮을수록(1위) 판매량이 높으므로 순위순 정렬
        fig_bar = px.bar(
            df.sort_values("rank").head(10),
            x="rank",
            y="saleNum",
            text="title",
            title="TOP 10 도서 판매량 현황",
            labels={"rank": "순위", "saleNum": "판매량"},
            color="saleNum",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # 차트 2: 리뷰 대비 별점 분포 (버블 차트)
        # 원의 크기가 클수록 판매량이 높음을 의미
        fig_bubble = px.scatter(
            df,
            x="reviews",
            y="star",
            size="saleNum",
            color="title",
            hover_name="title",
            title="리뷰 수 vs 별점 (원 크기=판매량)",
            labels={"reviews": "리뷰 수", "star": "별점"}
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    # --- 하단 상세 데이터 ---
    st.divider()
    st.subheader("📋 전체 도서 목록")
    st.dataframe(
        df[["rank", "title", "author", "saleNum", "star", "reviews"]].sort_values("rank"),
        hide_index=True,
        use_container_width=True,
        column_config = {
          "rank": "순위",
          "title": "도서명",
          "author": "저자",
          "saleNum": "판매량",
          "star": "별점",
          "reviews": "리뷰 수"
        }
    )
  else:
    st.info("해당 주차 및 카테고리에 검색된 데이터가 없습니다.")

# 1. 버튼 레이아웃 (세 번째 spacer 컬럼으로 버튼을 왼쪽으로 밀착)
btn_col1, btn_col2 = st.columns([1, 1])

# 수집 버튼 클릭 처리
with btn_col1:
    if st.button("수집하기"):
        if selected1 and selected2:
            # 버튼을 눌렀을 때 실행할 로직을 세션 상태에 저장하거나 직접 실행
            # 하지만 여기서 바로 st.write를 하면 컬럼 안에 갇히게 됩니다.
            st.session_state.run_type = "collect"
        else:
            st.warning("메뉴를 선택해주세요")

# 차트 버튼 클릭 처리
with btn_col2:
    if st.button("차트그리기"):
        st.session_state.run_type = "chart"

# ---------------------------------------------------------
# 2. 결과 출력 영역 (컬럼 블록 밖에서 실행 -> 전체 너비 사용)
# ---------------------------------------------------------
st.divider() # 시각적 구분을 위한 선

if "run_type" in st.session_state:
    if st.session_state.run_type == "collect":
        # getData() 내부의 st.text("데이터 수집 완료!") 등이 전체 너비로 나옵니다.
        getData() 
        
    elif st.session_state.run_type == "chart":
        # 차트 역시 화면 전체 너비를 사용하여 시원하게 그려집니다.
        makeChart()


  #   # 데이터 타입 변환 (DB에서 가져온 값은 문자열일 수 있으므로 숫자로 변환)
  #   df['star'] = pd.to_numeric(df['star'])
  #   # 카테고리별 평균 계산
  #   avg_df = df.groupby('rank')[['star']].mean()
  #   st.subheader("📊 국내 도서 / 해외 도서 평균 별점")
  #   st.bar_chart(avg_df)
  #  else:
  #    st.warning("조회된 데이터가 없습니다.")
      
# btn1, btn2, spacer = st.columns([1,1,15])
# with btn1:
#   if st.button(f"수집하기"):
#     if selected1 and selected2 :
#       getData()  
#     else : st.warning("메뉴를 선택해주세요")
#     # st.session_state.weekNo_index = selected2
#   # elif selected1 :
#   #   st.session_state.category_index = selected1
#   #   # st.session_state.weekNo_index = 1157

# with btn2:
#   if st.button("차트그리기"):
#       makeChart()


	