FROM python:3.6

RUN apt update && apt install -y ffmpeg

RUN mkdir /app /app/settings /app/tmp
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./*.py ./

ENTRYPOINT [ "python" ]
CMD [ "./tweet-insta-stories.py" ]