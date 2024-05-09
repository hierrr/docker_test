# 베이스 이미지로 Ubuntu 20.04.6 LTS (Focal Fossa) 사용
FROM ubuntu:20.04

# 대화형 프롬프트 비활성화
ARG DEBIAN_FRONTEND=noninteractive

# 작업 디렉토리 설정
WORKDIR /500error_checker

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    python3.8-venv \
    cron \
    wget \
    gnupg \
    tzdata

# 한국 시간대 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Chrome 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable

# 현재 디렉토리의 파일을 컨테이너 내부의 /500error_checker 디렉토리로 복사
COPY . /500error_checker

# 가상환경 생성
RUN python3.8 -m venv venv

# 가상환경 활성화
ENV PATH="/500error_checker/venv/bin:$PATH"

# requirements.txt 파일을 이용하여 종속성 설치
RUN pip3 install -r requirements.txt

# 환경변수 파일 (.env) 복사
COPY .env /500error_checker/.env

# 크론탭 설정
RUN echo "0 11 * * * /500error_checker/venv/bin/python /500error_checker/main.py >> /var/log/cron.log" > /etc/cron.d/500error_checker_cron
RUN chmod 0644 /etc/cron.d/500error_checker_cron
RUN crontab /etc/cron.d/500error_checker_cron

# 크론 데몬 실행
CMD ["cron", "-f"]