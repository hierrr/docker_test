# 베이스 이미지로 Ubuntu 20.04.6 LTS (Focal Fossa) 사용
FROM ubuntu:20.04

# 대화형 프롬프트 비활성화
ARG DEBIAN_FRONTEND=noninteractive

# 작업 디렉토리 설정
WORKDIR /counselor

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    python3.8-venv \
    cron \
    wget \
    gnupg \
    tzdata \
    unzip

# 한국 시간대 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Chrome 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable=124.0.6367.155-1

# VIM 설치
RUN apt-get install -y vim


# 현재 디렉토리의 파일을 컨테이너 내부의 /counselor 디렉토리로 복사
COPY . /counselor

# Chrome driver 다운로드
RUN mkdir -p /download
# RUN wget -N https://chromedriver.storage.googleapis.com/124.0.6367.155/chromedriver_linux64.zip -P /download
RUN wget -N https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.155/linux64/chromedriver-linux64.zip -P /download
RUN unzip /download/chromedriver-linux64.zip -d /download
RUN chmod +x /download/chromedriver-linux64/chromedriver

# # Chromedriver 경로를 PATH에 추가
# ENV PATH="/download/chromedriver-linux64:${PATH}"

# 가상환경 생성
RUN python3.8 -m venv venv

# 가상환경 활성화
ENV PATH="/counselor/venv/bin:$PATH"

# requirements.txt 파일을 이용하여 종속성 설치
RUN pip3 install -r requirements.txt

# 환경변수 파일 (.env) 복사
COPY .env /counselor/.env

# 서버 실행
CMD ["python3.8", "/counselor/app.py"]