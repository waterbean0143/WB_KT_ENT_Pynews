import streamlit as st
import requests
from bs4 import BeautifulSoup
import pyperclip

def extract_article_content(url, api_key):
    # 1. URL에서 HTML 내용 가져오기
    response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
    html_content = response.content

    # 2. HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 3. 본문 추출
    article_content_element = soup.select_one('#skin-12 > div:nth-child(2)')
    if article_content_element is None:
        raise ValueError("Could not find article content")
    article_content = article_content_element.get_text()

    # 4. 기사 항목과 해당 항목의 URL 추출
    article_item_element = soup.select_one('#section-list > ul > li:nth-child(1) > h4 > a')
    if article_item_element is None:
        raise ValueError("Could not find article item")
    article_item = article_item_element.get_text()

    article_url = article_item_element.get('href')
    if article_url is None:
        raise ValueError("Could not find article URL")
    
    return article_content, article_item, article_url

# Streamlit layout
st.sidebar.title('OpenAI API Key')
openai_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")

st.title('Web Article Scraper')

# URL을 입력받고 기사의 본문을 출력합니다.
url = st.text_input("기사 URL을 입력하세요: ", "")

if url and openai_key:
    try:
        # Adjust URL to include https:// if not present
        if not url.startswith('https://'):
            if url.startswith('www.'):
                url = "https://" + url  # 스키마 추가
            else:
                url = "https://www." + url  # 스키마 추가
        article_content, article_item, article_url = extract_article_content(url, openai_key)
        st.text_area('Article Content:', article_content, height=300)
        st.write('Article Item:', article_item)
        st.write('Article URL:', article_url)
        if st.button('Copy to Clipboard'):
            pyperclip.copy(article_content)
            st.success('Text Copied to clipboard')
    except Exception as e:
        st.error(f"An error occurred: {e}")
elif not openai_key:
    st.warning('Please enter your OpenAI API Key.')
