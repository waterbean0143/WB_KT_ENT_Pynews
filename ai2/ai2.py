import streamlit as st
import requests
from bs4 import BeautifulSoup
import pyperclip

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
        article_links.append(article_link)

    # 5. 기사 본문 추출
    article_contents = []
    for link in article_links:
        article_url = f"https://www.aitimes.kr{link}"
        article_content = extract_article_content(article_url)
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


# Streamlit layout
st.title('Web Article List Scraper')

# URL을 입력받고 기사 제목, 링크, 본문을 출력합니다.
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
            st.write('Article Title:', title)
            st.write('Article Link:', link)
            st.text_area('Article Content:', content, height=300)
            if st.button('Copy to Clipboard', key=title):
                article_info = f"Title: {title}\nLink: {link}\n\n{content}"
                pyperclip.copy(article_info)
                st.success('Text Copied to clipboard')
            st.write('---')
    except Exception as e:
        st.error(f"An error occurred: {e}")
