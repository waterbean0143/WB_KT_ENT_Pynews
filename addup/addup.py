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
        search = st.text_input("검색할 키워드를 입력해주세요:")
        page = st.number_input("크롤링할 시작 페이지를 입력해주세요:", min_value=1, max_value=100, value=1)
        page2 = st.number_input("크롤링할 종료 페이지를 입력해주세요:", min_value=1, max_value=100, value=1)
        
        if st.button("크롤링 시작"):
            urls = makeUrl(search, page, page2)
            news_urls = []
            for url in urls:
                url_list = articles_crawler(url)
                news_urls.extend(url_list)
            
            final_urls = [i for i in news_urls if "news.naver.com" in i]
            st.write("검색된 기사 링크:", final_urls)

    # 기사 요약 및 메일 발송 섹션
    with st.expander("기사 요약 및 메일 발송"):
        naver_id = st.text_input("네이버 아이디:", type="password")
        naver_pw = st.text_input("네이버 패스워드:", type="password")
        api_key = st.text_input("OpenAI API 키:", type="password")
        
        uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")
        if uploaded_file:
            data = pd.read_csv(uploaded_file)
            st.write(data)
        
        if st.button("기사 요약 및 메일 발송"):
            # 요약 및 메일 발송 코드는 여기에 추가됩니다.
            st.write("요약 및 메일 발송 완료!")

if __name__ == "__main__":
    main()
