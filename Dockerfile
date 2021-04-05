ROM python:3.9
LABEL Description=""

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
 && apt-get install -y ffmpeg \
 && apt-get install -y git

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt \
 && rm -rf /requirements.txt

RUN mkdir temp

RUN git clone 'https://github.com/aliparlakci/bulk-downloader-for-reddit.git' temp
WORKDIR temp
RUN git checkout v2 \
 && pip install .

COPY . /bdfr-html
WORKDIR /bdfr-html


RUN mkdir input && mkdir html

ENTRYPOINT ["python", "bdfrToHTML.py"]




