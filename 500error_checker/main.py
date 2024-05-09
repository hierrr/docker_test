import os
from dotenv import load_dotenv
import requests
import concurrent.futures
from bs4 import BeautifulSoup
import re
from datetime import datetime

load_dotenv()

today = datetime.today().strftime("%Y-%m-%d")

def get_latest_post_id():
    url = "https://phdkim.net/board/free/list"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        href = soup.select_one("#__layout > div > main > div > div.layout.board-layout > div.left.board-free-area > div.board-list-wrap > ul > li:nth-of-type(2) > div > a")["href"]
        match = re.search(r"/board/free/(\d+)", href)
        if match:
            return int(match.group(1))
    return None

def slack_message(text):
    token = os.getenv("SLACK_TOKEN")
    channel = os.getenv("SLACK_CHANNEL") 
    requests.post("https://slack.com/api/chat.postMessage", 
                  headers={"Authorization": "Bearer "+token}, data={"channel": channel,"text": text})


def check_error(url):
    try:
        response = requests.get(url)
        if response.status_code == 500:
            return 1
    except requests.RequestException:
        return 0
    return 0

def count_500_errors_multithreaded(start, end, num_threads):
    urls = [f"https://phdkim.net/board/free/{i}" for i in range(start, end + 1)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        error_counts = list(executor.map(check_error, urls))
    return sum(error_counts)

end_range = get_latest_post_id()
start_range = get_latest_post_id() - 50

if end_range:
    num_threads = 5
    errors = count_500_errors_multithreaded(start_range, end_range, num_threads)
    slack_message(f"--\n[{today}] 아무개랩 500 에러 감시 봇\n아무개랩 게시판 id : {start_range} ~ {end_range}\n500에러 페이지 개수 : {errors}")
else:
    print("Failed to fetch the latest post ID.")