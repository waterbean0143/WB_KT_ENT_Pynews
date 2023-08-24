import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import csv
import openai
import os # os 모듈을 추가합니다.

openai.api_key = "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"

def read_csv(file_path):
data = []
with open(file_path, "r") as csvfile:
reader = csv.reader(csvfile)
next(reader) # 첫 번째 행(헤더)은 건너뜁니다.
for row in reader:
date = row[0]
subject = row[1]
body = row[2]
link = row[3]
tags = row[4]

summarized_body = gpt_summarize(body)

row_data = f"""
<tr>
<td>{date}</td>
<td>{subject}</td>
<td>{summarized_body}</td>
<td><a href="{link}">링크 바로가기</a></td>
<td>{tags}</td>
</tr>
"""
data.append(row_data)

table = f"""
<table border="1" style="border-collapse: collapse; width: 100%;">
<tr>
<th style="width: 12%;">날짜</th>
<th style="width: 20%;">제목</th>
<th style="width: 50%;">요약된 본문</th>
<th style="width: 10%;">링크</th>
<th style="width: 8%;">태그</th>
</tr>
{"".join(data)}
</table>
"""

return table

def gpt_summarize(text):
system_instruction = "assistant는 user의 입력을 bullet point로 3줄로 요약해준다.각 bullet point가 끝날 때마다 한 줄씩 바꾸어준다."

messages = [{"role": "system", "content": system_instruction},{"role":"user","content":text}]

response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
result = response['choices'][0]['message']['content']
return result

def send_email(subject, body, to_email, attachment_path):
from_email = ""
password = ""

msg = MIMEMultipart()
msg["From"] = from_email
msg["To"] = ", ".join(to_email)
msg["Subject"] = subject

body_part = MIMEText(body, "html")
msg.attach(body_part)

# 첨부 파일의 원본 이름을 사용합니다.
with open(attachment_path, "rb") as file:
original_filename = os.path.basename(attachment_path)
part = MIMEApplication(file.read(), Name=original_filename)
part["Content-Disposition"] = f"attachment; filename={original_filename}"
msg.attach(part)

smtp_server = "smtp.naver.com"
smtp_port = 587
try:
smtp_conn = smtplib.SMTP(smtp_server, smtp_port)
smtp_conn.starttls()
smtp_conn.login(from_email, password)
smtp_conn.sendmail(from_email, to_email, msg.as_string())
print("이메일이 성공적으로 발송되었습니다.")
except smtplib.SMTPException as e:
print("이메일 발송 중 오류가 발생했습니다:", e)
finally:
smtp_conn.quit()

if __name__ == "__main__":
subject = "[파이뉴스] 트렌드 공유"
file_path = "/Users/dowankim/Downloads/ai-news.csv"
attachment_path = "/Users/dowankim/Downloads/한국어그림.jpg"

body = read_csv(file_path)

to_email_list = ["dowan.kim@kt.com","sueyoung.lee@kt.com","uhyeon.shin@kt.com","hyein.kim@kt.com","waterbean.bae@kt.com"]

for to_email in to_email_list:
send_email(subject, body, [to_email], attachment_path)
