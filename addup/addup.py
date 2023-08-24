import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import pandas as pd
import urllib3
import openai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

urllib3.disable_warnings()

SCRAP_FILE = 'addup_scrap.csv'
SUMMARY_FILE = 'addup_summary.csv'

def makePgNum(num):
    if num == 1:
        return num
    elif num == 0:
        return num + 1
    else:
        return num + 9 * (num - 1)

def makeUrl(search, start_pg, end_pg):
    if start_pg == end_pg:
        start_page = makePgNum(start_pg)
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(start_page) + "&sort=0&pd=1"
        return [url]
    else:
        urls = []
        for i in range(start_pg, end_pg + 1):
            page = makePgNum(i)
            url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(page) + "&sort=0&pd=1"
            urls.append(url)
        return urls

def news_attrs_crawler(articles, attrs):
    attrs_content = []
    for i in articles:
        attrs_content.append(i.attrs[attrs])
    return attrs_content

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

def articles_crawler(url):
    original_html = requests.get(url, headers=headers, verify=False)
    html = BeautifulSoup(original_html.text, "html.parser")
    url_naver = html.select("div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
    url = news_attrs_crawler(url_naver, 'href')
    return url

def main():
    st.title("네이버 기사 크롤링 및 요약 애플리케이션")

    with st.expander("네이버 기사 크롤링"):
        search = st.text_input("검색할 키워드를 입력해주세요:")
        page = st.number_input("크롤링할 시작 페이지를 입력해주세요.", value=1)
        page2 = st.number_input("크롤링할 종료 페이지를 입력해주세요.", value=1)

        if st.button("크롤링 시작"):
            url = makeUrl(search, page, page2)
            news_titles = []
            news_url = []
            news_contents = []
            news_dates = []

            for i in url:
                urls = articles_crawler(i)
                news_url.extend(urls)

            news_url_1 = []
            news_url_1.extend(news_url)

            final_urls = [url for url in news_url_1 if "news.naver.com" in url]

            for i in tqdm(final_urls):
                news = requests.get(i, headers=headers, verify=False)
                news_html = BeautifulSoup(news.text, "html.parser")
                title = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
                if title is None:
                    title = news_html.select_one("#content > div.end_ct > div > h2")

                # 뉴스 본문 가져오기
                content = news_html.select_one("article#dic_area")
                if content is None:
                    content = news_html.select_one("div#articleBodyContents")
                if content is None:
                    content = news_html.select_one("div.article_body_contents")
                if content is None:
                    content = "Content not found"

                content = ''.join(str(content))
                pattern1 = '<[^>]*>'
                title = re.sub(pattern=pattern1, repl='', string=str(title))
                content = re.sub(pattern=pattern1, repl='', string=content)
                pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
                content = content.replace(pattern2, '')

                news_titles.append(title)
                news_contents.append(content)

                try:
                    html_date = news_html.select_one("div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
                    news_date = html_date.attrs['data-date-time']
                except AttributeError:
                    news_date = news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
                    news_date = re.sub(pattern=pattern1, repl='', string=str(news_date))
                news_dates.append(news_date)

            df = pd.DataFrame({
                'index': range(1, len(news_titles) + 1),
                'date': news_dates,
                'title': news_titles,
                'link': final_urls,
                'contents': news_contents
            })
            df.to_csv(SCRAP_FILE, index=False)
            st.write("데이터가 addup_scrap.csv로 저장되었습니다.")
    # 메일 발송 섹션
    with st.expander("메일 발송"):
        email_list = st.text_area("이메일 목록 (쉼표로 구분):")
        if st.button("메일 발송"):
            # ... (메일 발송 코드)

if __name__ == "__main__":
    main()
이제 각 CSV 파일의 첫 
