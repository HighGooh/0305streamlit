from bs4 import BeautifulSoup as bs
from requests import get
import pandas as pd
import streamlit as st
import json

st.set_page_config(
  page_title="interpark 수집",
  page_icon="💗",
  layout="wide",
)

# 인터파크 장르별 URL
# 뮤지컬 url
musical_url = "https://tickets.interpark.com/contents/ranking?genre=MUSICAL"
# 콘서트 url
concert_url = "https://tickets.interpark.com/contents/ranking?genre=CONCERT"
# 클래식 url
classic_url = "https://tickets.interpark.com/contents/ranking?genre=CLASSIC"
# 아동 url
kids_url = "https://tickets.interpark.com/contents/ranking?genre=KIDS"
# 연극 url
drama_url = "https://tickets.interpark.com/contents/ranking?genre=DRAMA"
# 전시 url
exhibit_url = "https://tickets.interpark.com/contents/ranking?genre=EXHIBIT"

musical_key = '@"/ranking","?period=D&page=1&pageSize=50&rankingTypes=MUSICAL",'

# 데이터 수집
def getData():
  try:
    url = musical_url
    st.text(f"URL: {url}")
    res = get(url)
    if res.status_code == 200:
      st.text("인터파크 티켓 수집 시작!")
      tickets = [] # { 장르, 티켓이름, 장소, 시작날짜, 종료날짜, 예매율 }
      soup = bs(res.text, "html.parser")
      items = soup.select("div.responsive-ranking-list_rankingItem__PuQPJ")
      genre = "MUSICAL"
      for item in items:
        tName = item.select_one("li.responsive-ranking-list_goodsName__aHHGY").get_text(strip=True)
        pName = item.select_one("li.responsive-ranking-list_placeName__9HN2O").get_text(strip=True)
        tDate = item.select_one("div.responsive-ranking-list_dateWrap__jBu5n").get_text(strip=True)
        tPercent = item.select_one("li.responsive-ranking-list_bookingPercent__7ppKT").get_text(strip=True)
        tickets.append({ "genre": genre, "tName": tName, "pName": pName, "tDate": tDate, "tPercent": tPercent })
      tab1, tab2, tab3, tab4 = st.tabs(["HTML 데이터", "json 데이터", "DataFrame", "API 데이터"])
      with tab1:
        st.text("HTML 출력")
        # st.html(items)
        st.text(items)
      with tab2:
        st.text("JSON 출력")
        # st.json(arr)
        json_string = json.dumps(tickets, ensure_ascii=False, indent=2)
        st.json(body=json_string, expanded=True, width="stretch")
      with tab3:
        st.text("DataFrame 출력")
        st.dataframe(pd.DataFrame(tickets))
      with tab4:
        st.text("API 출력")
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        json_data = json.loads(script_tag.string)
        st.json(json_data, expanded=False)
        st.html("<hr/>")
        st.text(f"{genre} 목록 출력")
        st.json(json_data.get('props', {}).get('pageProps', {}).get('fallback', {}).get(musical_key, []), expanded=False)
  except Exception as e:
    return 0
  return 1

if st.button(f"수집하기"):
  getData()
