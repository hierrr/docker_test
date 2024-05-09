from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import time
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

def slack_message(text):
    token = os.getenv("SLACK_TOKEN")
    channel = os.getenv("SLACK_CHANNEL") 
    requests.post("https://slack.com/api/chat.postMessage", headers={"Authorization": "Bearer "+token}, data={"channel": channel,"text": text})

try:
    # Set up Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")

    # Initialize webdriver with service
    service = Service('/download/chromedriver-linux64/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to the webpage
    driver.get("https://phdkim.net/")

    # Wait for the page to load
    time.sleep(2)

    # Close the popup if it exists
    try:
        popup_close_button = driver.find_element(By.CSS_SELECTOR, "body > div > div.popup.js-popup.d-active > div > button")
        popup_close_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"Error closing popup: {e}")

    # Generate filename with today's date
    date_str = datetime.datetime.now()
    filename = f"screenshot_{date_str}.png"

    # Take and save screenshot
    driver.save_screenshot(filename)

    # Cleanup: close the browser
    driver.quit()

    # slack_message_error('메인 홈페이지 채용 공고 이미지 저장 성공')
    slack_message(f"도커 테스트: 메인 홈페이지 채용 공고 이미지 저장 성공")
    print(1)

except Exception as e:
    # slack_message_error(str(e))
    slack_message(f"도커 테스트: 메인 홈페이지 채용 공고 이미지 저장 실패, {str(e)}")
