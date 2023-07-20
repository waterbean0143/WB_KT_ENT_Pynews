import streamlit as st
import requests
from bs4 import BeautifulSoup
import pyperclip
from transformers import pipeline
from urllib.parse import urljoin
import openai

# requirements.txt에 필요한 내용[streamlit 배포시 필요]
# -> 일반 환경에서는 해당 라이브러리를 pip install [패키지명]으로 설치 필요
# streamlit
# requests
# bs4
# pyperclip
# transformers==4.10.3
# tensorflow==2.12
# openai==0.27.0


def extract_article_list(url):
    # 1. URL에서 HTML 내용 가져오기
    response = requests.get(url)
    html_content = response.content

    # 2. HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 3. 기사 제목 추출
    article_titles = []
    title_elements = soup.select('#section-list > ul > li > h4.titles')
    for title_element in title_elements:
        article_title = title_element.get_text()
        article_titles.append(article_title)

    # 4. 기사 링크 추출
    article_links = []
    link_elements = soup.select('#section-list > ul > li > h4 > a')
    for link_element in link_elements:
        article_link = link_element.get('href')
        article_url = urljoin(url, article_link)  # 절대 경로로 변환
        article_links.append(article_url)

    # 5. 기사 본문 추출
    article_contents = []
    for link in article_links:
        article_content = extract_article_content(link)
        article_contents.append(article_content)

    return article_titles, article_links, article_contents


def extract_article_content(url):
    # 1. URL에서 HTML 내용 가져오기
    response = requests.get(url)
    html_content = response.content

    # 2. HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 3. 본문 추출
    article_content_element = soup.select_one('#snsAnchor > div')
    if article_content_element is None:
        raise ValueError("Could not find article content")
    article_content_paragraphs = article_content_element.find_all('p')
    article_content = "\n".join([p.get_text() for p in article_content_paragraphs])

    return article_content


def summarize_text(text, api_key):
    # System instruction: "The assistant should summarize the user's input into 30 characters."
    system_instruction = "The assistant should summarize the user's input into 30 characters in Korean."

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": text}
    ]

    openai.api_key = api_key
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    summary = response['choices'][0]['message']['content']

    return summary


# Streamlit layout
# st.sidebar.title('OpenAI API Key')
# openai_key = st.sidebar.text_input("Enter your OpenAI API Key:", value="", type="password", key="openai_key_input")

openai_key = "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"

st.title('WB_ArticleScraper')

# URL 선택 옵션
option = st.selectbox('URL 입력 방식', ['인공지능신문(aitimes) AI 산업군 - 제목형', '직접 입력'])

if option == '인공지능신문(aitimes) AI 산업군 - 제목형':
    url = "https://www.aitimes.kr/news/articleList.html?page=1&total=3382&sc_section_code=S1N4&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&box_idxno=&sc_multi_code=&sc_is_image=&sc_is_movie=&sc_user_name=&sc_order_by=E"
else:
    url = st.text_input("뉴스 기사 리스트 URL을 입력하세요: ", "")

if url:
    try:
        # Adjust URL to include https:// if not present
        if not url.startswith('https://'):
            if url.startswith('www.'):
                url = "https://" + url  # 스키마 추가
            else:
                url = "https://www." + url  # 스키마 추가
        article_titles, article_links, article_contents = extract_article_list(url)
        for title, link, content in zip(article_titles, article_links, article_contents):
            st.markdown(f'[{title}]({link})')
            st.text_area('Article Content:', content, height=300)
            if st.button('GPT로 요약하기', key=f"{title}_summarize"):
                summarization_model = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="tf", device=0)
                prompt = "summarize: " + content[:600]  # Adjust the character limit as needed
                summary = summarize_text(prompt, openai_key)
                st.write('Summary:')
                st.markdown(f"- {summary}")
                if st.button('Copy Summary to Clipboard', key=f"{title}_summary_copy"):
                    pyperclip.copy(summary)
                    st.success('Summary Copied to clipboard')
            if st.button('Copy Content to Clipboard', key=f"{title}_content_copy"):
                pyperclip.copy(content)
                st.success('Content Copied to clipboard')
            st.write('---')
    except Exception as e:
        st.error(f"An error occurred: {e}")
