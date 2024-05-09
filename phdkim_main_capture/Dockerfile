# 베이스 이미지로 Ubuntu 20.04.6 LTS (Focal Fossa) 사용
FROM ubuntu:20.04

# 대화형 프롬프트 비활성화
ARG DEBIAN_FRONTEND=noninteractive

# 작업 디렉토리 설정
WORKDIR /phdkim_main_capture

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

# 현재 디렉토리의 파일을 컨테이너 내부의 /phdkim_main_capture 디렉토리로 복사
COPY . /phdkim_main_capture

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
ENV PATH="/phdkim_main_capture/venv/bin:$PATH"

# requirements.txt 파일을 이용하여 종속성 설치
RUN pip3 install -r requirements.txt

# 환경변수 파일 (.env) 복사
COPY .env /phdkim_main_capture/.env

# 크론탭 설정
RUN echo "5 11 * * * /phdkim_main_capture/venv/bin/python /phdkim_main_capture/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/phdkim_main_capture_cron
RUN chmod 0644 /etc/cron.d/phdkim_main_capture_cron
RUN crontab /etc/cron.d/phdkim_main_capture_cron

# 크론 데몬 실행
CMD ["cron", "-f"]