FROM python:3.6

RUN apt update && apt install -y ffmpeg cron

WORKDIR git

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN touch /var/log/cron.log
COPY crontab /tmp/crontab
RUN crontab /tmp/crontab && rm /tmp/crontab

COPY tweet-insta-stories.py ./
COPY settings ./settings

CMD cron && tail -f /var/log/cron.log
