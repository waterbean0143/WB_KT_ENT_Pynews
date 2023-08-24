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

def gpt_summarize(text):
    system_instruction = "assistant는 user의 입력을 bullet point로 3줄로 요약해준다. 각 bullet point가 끝날 때마다 한 줄씩 바꾸어준다."
    messages = [{"role": "system", "content": system_instruction}, {"role": "user", "content": text}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    result = response['choices'][0]['message']['content']
    return result

def send_email(subject, body, to_email, from_email, password):
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = ", ".join(to_email)
    msg["Subject"] = subject

    body_part = MIMEText(body, "html")
    msg.attach(body_part)

    smtp_server = "smtp.naver.com"
    smtp_port = 587
    try:
        smtp_conn = smtplib.SMTP(smtp_server, smtp_port)
        smtp_conn.starttls()
        smtp_conn.login(from_email, password)
        smtp_conn.sendmail(from_email, to_email, msg.as_string())
        st.write("이메일이 성공적으로 발송되었습니다.")
    except smtplib.SMTPException as e:
        st.write("이메일 발송 중 오류가 발생했습니다:", e)
    finally:
        smtp_conn.quit()

# Streamlit UI for Summarization and Email Section
with st.expander("기사 요약 및 메일 발송"):
    # Load the scraped data
    try:
        df = pd.read_csv(SCRAP_FILE)
        st.write(df)
        
        if st.button("기사 요약"):
            # Summarize each article
            df['contents'] = df['contents'].apply(gpt_summarize)
            
            # Save the summarized articles
            df.to_csv(SUMMARY_FILE, index=False)
            st.write("기사가 요약되어 addup_summary.csv로 저장되었습니다.")
            
            # Display the summarized articles
            st.write(df)
            
        # Sending emails
        if st.button("메일 발송"):
            subject = "기사 요약 결과"
            from_email = st.text_input("당신의 이메일 주소:")
            password = st.text_input("당신의 이메일 패스워드:", type='password')
            to_email = st.text_input("받는 사람의 이메일 주소 (','로 구분하여 여러 명에게 보낼 수 있습니다.)").split(',')
            
            body = df.to_html()
            send_email(subject, body, to_email, from_email, password)
            
    except FileNotFoundError:
        st.write(f"{SCRAP_FILE} 파일이 존재하지 않습니다. 먼저 기사를 크롤링해주세요.")

if __name__ == "__main__":
    main()
