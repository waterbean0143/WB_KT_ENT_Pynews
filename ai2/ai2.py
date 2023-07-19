import streamlit as st
import requests
from bs4 import BeautifulSoup
import pyperclip
from transformers import pipeline

def extract_article_content(url):
    # Function to extract article content

def extract_article_list(url):
    # Function to extract article titles, links, and contents from the article list URL

# Streamlit layout
st.sidebar.title('OpenAI API Key')
openai_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")

st.title('Web Article Scraper')

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
            
            if st.button('Summarize', key=f"{title}_summarize"):
                if openai_key:
                    summarization_model = pipeline("summarization", model="t5-base", tokenizer="t5-base", device=0)
                    summary = summarization_model(content, max_length=150, min_length=30, do_sample=False)[0]["summary_text"]
                    st.write('Summary:')
                    st.markdown(f"- {summary}")
                    if st.button('Copy Summary to Clipboard', key=f"{title}_summary_copy"):
                        pyperclip.copy(summary)
                        st.success('Summary Copied to clipboard')
                else:
                    st.warning('Please enter your OpenAI API Key to use summarization.')
            
            if st.button('Copy Content to Clipboard', key=f"{title}_content_copy"):
                pyperclip.copy(content)
                st.success('Content Copied to clipboard')
            
            st.write('---')
    
    except Exception as e:
        st.error(f"An error occurred: {e}")

elif not openai_key:
    st.warning('Please enter your OpenAI API Key.')
