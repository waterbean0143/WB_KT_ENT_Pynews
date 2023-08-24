from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import sys
import urllib3

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
print("생성url: ", url)
return url
else:
urls = []
for i in range(start_pg, end_pg + 1):
page = makePgNum(i)
url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(page) + "&sort=0&pd=1"
urls.append(url)
print("생성url: ", urls)
return urls

def news_attrs_crawler(articles,attrs):
attrs_content=[]
for i in articles:
attrs_content.append(i.attrs[attrs])
return attrs_content

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

def articles_crawler(url):
original_html = requests.get(url, headers=headers, verify=False)
html = BeautifulSoup(original_html.text, "html.parser")
url_naver = html.select("div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
url = news_attrs_crawler(url_naver,'href')
return url

search = input("검색할 키워드를 입력해주세요:")
page = int(input("\n크롤링할 시작 페이지를 입력해주세요. ex)1(숫자만입력):"))
print("\n크롤링할 시작 페이지: ", page, "페이지")
page2 = int(input("\n크롤링할 종료 페이지를 입력해주세요. ex)1(숫자만입력):"))
print("\n크롤링할 종료 페이지: ", page2, "페이지")

url = makeUrl(search, page, page2)

news_titles = []
news_url = []
news_contents = []
news_dates = []

for i in url:
urls = articles_crawler(i)
news_url.append(urls)

def makeList(newlist, content):
for i in content:
for j in i:
newlist.append(j)
return newlist

news_url_1 = []
makeList(news_url_1, news_url)

final_urls = [url for url in news_url_1 if "news.naver.com" in url]

for i in tqdm(final_urls):
news = requests.get(i, headers=headers, verify=False)
news_html = BeautifulSoup(news.text, "html.parser")
title = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
if title is None:
title = news_html.select_one("#content > div.end_ct > div > h2")

# 뉴스 본문 가져오기
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

print("검색된 기사 갯수: 총 ", (page2+1-page)*10, '개')
print("\n[뉴스 제목]")
print(news_titles)
print("\n[뉴스 링크]")
print(final_urls)
print("\n[뉴스 내용]")
print(news_contents)

print('news_title: ', len(news_titles))
print('news_url: ', len(final_urls))
print('news_contents: ', len(news_contents))
print('news_dates: ', len(news_dates))

import pandas as pd

news_df = pd.DataFrame({'date':news_dates,'title':news_titles,'link':final_urls,'content':news_contents})

def make_hyperlink(value):
return '=HYPERLINK("%s", "%s")' % (value.format(value), value)

news_df = news_df.drop_duplicates(keep='first', ignore_index=True)
news_df['link'] = news_df['link'].apply(lambda x: make_hyperlink(x))
news_df.index += 1
print("중복 제거 후 행 개수: ", len(news_df))

# 데이터 프레임 저장 부분
now = datetime.datetime.now() # 현재 시간을 저장
save_path = "/Users/dowankim/Downloads/파이뉴스.csv".format(now.strftime('%Y%m%d_%H시%M분%S초'))
news_df.to_csv(save_path, encoding='utf-8-sig', index=True)
