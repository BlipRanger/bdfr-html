FROM python:3.9

RUN apt-get update
RUN apt-get install ffmpeg -y


WORKDIR /bdfrh
COPY ./bdfrtohtml/ ./bdfrtohtml
COPY ./templates/ ./templates
COPY ./start.py ./start.py
COPY ./requirements.txt ./requirements.txt
COPY ./config.yml ./config.yml


EXPOSE 5000
EXPOSE 7634

RUN pip install -r requirements.txt

RUN mkdir input
RUN mkdir output
RUN mkdir config

CMD python start.py