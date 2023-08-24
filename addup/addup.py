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

urllib3.disable_warnings()

def makePgNum(num):
    if num == 1:
        return num
    elif num == 0:
        return num+1
    else:
        return num+9*(num-1)

def makeUrl(search, start_pg, end_pg):
    if start_pg == end_pg:
        start_page = makePgNum(start_pg)
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(start_page) + "&sort=0&pd=1"
        return url
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
    urls = news_attrs_crawler(url_naver, 'href')
    return urls

def main():
    st.title("네이버 기사 크롤링 및 요약 애플리케이션")

    # 네이버 기사 크롤링 섹션
    with st.expander("네이버 기사 크롤링"):
        # ... (이전 코드와 동일)
        if st.button("크롤링 시작"):
            # ... (크롤링 코드)
            # 데이터를 CSV로 저장
            df = pd.DataFrame({
                'index': range(1, len(news_titles) + 1),
                'date': news_dates,
                'title': news_titles,
                'link': final_urls,
                'contents': news_contents
            })
            df.to_csv(SCRAP_FILE, index=False)
            st.write("데이터가 [addup_scrap].csv로 저장되었습니다.")

    # 기사 요약 섹션
    with st.expander("기사 요약"):
        if st.button("기사 요약"):
            # ... (요약 코드)
            # 요약된 데이터를 CSV로 저장
            summary_df = pd.DataFrame({
                'index': range(1, len(news_titles) + 1),
                'date': news_dates,
                'title': news_titles,
                'link': final_urls,
                'contents': summarized_contents
            })
            summary_df.to_csv(SUMMARY_FILE, index=False)
            st.write("데이터가 [addup_summary].csv로 저장되었습니다.")
            st.write(summary_df)

    # 메일 발송 섹션
    with st.expander("메일 발송"):
        email_list = st.text_area("이메일 목록 (쉼표로 구분):")
        if st.button("메일 발송"):
            # ... (메일 발송 코드)

if __name__ == "__main__":
    main()
이제 각 CSV 파일의 첫 
