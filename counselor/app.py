from flask import Flask, request, jsonify, g
import requests
from threading import Thread
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import sqlite3
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv()

app = Flask(__name__)
slack_token = os.getenv('SLACK_TOKEN')


DATABASE = 'logs.db'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                message TEXT
            )
        ''')
    return db

def send_message_to_slack(user_id, message):
    try:
        client_web = WebClient(token=slack_token)
        response = client_web.chat_postMessage(channel=user_id, text=message)#,response_type="in_channel")
        logger.info(f"Message sent to user {user_id}: {message}")
    except SlackApiError as e:
        logger.error(f"Error sending message to user {user_id}: {e}")

def delete_message(channel_id, message_ts):
    try:
        client_web = WebClient(token=slack_token)
        response = client_web.chat_delete(
            channel=channel_id,
            ts=message_ts
        )
        if not response["ok"]:
            logging.error(f"Failed to delete message: {response['error']}")
    except SlackApiError as e:
        logging.error(f"Error deleting message: {e}")


@app.route('/slack/actions', methods=['POST'])
def handle_actions():
    payload = json.loads(request.form['payload'])
    logger.info(f"Payload: {payload}")
    
    callback_id = payload['callback_id']
    user_id = payload['user']['id']
    channel_id = payload['channel']['id']
    message_ts = payload['message_ts']
    
    logger.info(f"Channel ID: {channel_id}")
    logger.info(f"Message Timestamp: {message_ts}")
    
    if callback_id == 'contents_approval':
        action = payload['actions'][0]['value']
        if action != 'reject':
            data = json.loads(action)
            title = data['title']
            content = data['content']
            
            # 승인 버튼 클릭 시 동작할 함수 호출
            logger.info(f"handle_actions > approve_action called")
            approve_action(title, content)
            logger.info(f"컨텐츠 업로드가 승인되었습니다. Title: {title}, Content: {content}")
        else:
            # 거절 버튼 클릭 시 동작할 함수 호출
            reject_action(user_id)
            logger.info("컨텐츠 업로드가 거절되었습니다.")
    
    
    return '', 200

def upload_post(title, content):
    # 웹드라이버 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')  # 창 크기 설정 추가
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 로그인
        logger.info(f"upload_post: try to upload post")
        driver.get("https://stage.phdkim.net/login?next=%2Fboard%2Fwrite")
        logger.info(f"upload_post: homepage open")
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > main > div > div > div.input-box > div:nth-child(1) > input")))
        email = "palusomni20@gmail.com"
        email_input.send_keys(email)
        logger.info(f"upload_post: email input")
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > main > div > div > div.input-box > div:nth-child(2) > div > input")))
        password = "Pal0911!!"
        password_input.send_keys(password)
        logger.info(f"upload_post: password input")
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-login.btn-fill.--active")))
        button.click()
        logger.info(f"upload_post: logged in")

        # 로그인 후 다음 페이지 로딩 대기
        WebDriverWait(driver, 10).until(EC.url_contains("https://stage.phdkim.net/board/write"))

        # 라디오 버튼 클릭 대기 및 클릭
        radio_button_css = "#__layout > div > main > div > div.board-write-box > div.write-box > div.board-list > div.visible-pc > div > label:nth-child(1) > span.path"
        radio_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, radio_button_css)))
        radio_button.click()
        logger.info(f"upload_post: write page open")

        # write 페이지 요소 선택 및 입력
        title_css = "#__layout > div > main > div > div.board-write-box > div.write-box > div.title-area > input"
        title_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, title_css)))
        title_element.clear()
        title_element.send_keys(title)
        logger.info(f"upload_post: title input")

        contents_css = "#__layout > div > main > div > div.board-write-box > div.write-box > textarea"
        contents_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, contents_css)))
        contents_element.clear()
        contents_element.send_keys(content)
        logger.info(f"upload_post: content input")

        submit_button_css = "#__layout > div > main > div > div.board-write-box > div.write-box > div.editing-area > div.right.visible-pc > button"
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button_css)))
        submit_button.click()
        logger.info(f"upload_post: post uploaded")

        # 시간 지연 추가

    except Exception as e:
        print(f"오류 발생: {str(e)}")

    finally:
        driver.quit()


def send_interactive_message_stage(title, content):
    try:
        client = WebClient(token=slack_token)
        channel_id = "bot_stage"  # 채널 ID로 대체해야 함
        message = {
            "channel": channel_id,
            "text": f"Title: {title}\nContent: {content}",
            "attachments": [
                {
                    "fallback": "승인 또는 거절을 선택해주세요.",
                    "callback_id": "contents_approval",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "approve",
                            "text": "승인",
                            "type": "button",
                            "value": json.dumps({"title": title, "content": content})
                        },
                        {
                            "name": "reject",
                            "text": "거절",
                            "type": "button",
                            "value": "reject"
                        }
                    ]
                }
            ]
        }
        response = client.chat_postMessage(**message)
        logger.info(f"Interactive message sent to channel {channel_id}")
    except SlackApiError as e:
        logger.error(f"Error sending interactive message to channel {channel_id}: {e}")

@app.route('/contents_upload', methods=['POST'])
def handle_contents_upload():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    logger.info(f'Received contents upload request with title: {title} and content: {content}')
    
    db = get_db()
    db.execute("INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)", 
               (datetime.now().isoformat(), 'INFO', f'Contents upload request with title: {title} and content: {content}'))
    db.commit()
    
    # 인터랙티브 메시지 전송
    send_interactive_message_stage(title, content)
    
    return jsonify({"status": "success"})

def approve_action(title, content):
    # 승인 버튼 클릭 시 동작할 코드 작성
    logger.info(f"approve_action > upload_post called")
    upload_post(title, content)

def reject_action(user_id):
    # 거절 버튼 클릭 시 동작할 함수
    message = "거절되었습니다."
    send_message_to_slack(user_id, message)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')