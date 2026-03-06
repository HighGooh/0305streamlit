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

url = "https://mapi.ticketlink.co.kr/mapi/ranking/genre/daily?categoryId=20&categoryId2=16&categoryId3=0&menu=RANKING"

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
