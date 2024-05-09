
import requests
def post_content(title, content):
    url = "http://172.17.0.2:5000/contents_upload" # docker ip로 변경
    data = {
        "title": title,
        "content": content
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # 요청이 성공적이지 않을 경우 예외 발생
        print("POST request succeeded.")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("POST request failed.")
        print("Error:", e)


post_content('test title' , 'test contents')