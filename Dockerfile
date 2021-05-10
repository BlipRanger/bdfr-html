FROM python:3.9

RUN apt-get update
RUN apt-get install ffmpeg -y

COPY ./requirements.txt requirements.txt
COPY ./bdfrToHTML.py bdfrToHTML.py
COPY ./style.css style.css
COPY ./start.py start.py

ENV BDFR_FREQ=15
ENV BDFR_IN=/input
ENV BDFR_OUT=/output
ENV BDFR_RECOVER_COMMENTS=True
ENV BDFR_ARCHIVE_CONTEXT=True
ENV BDFR_LIMIT=1100

EXPOSE 5000
EXPOSE 7634

RUN pip install -r requirements.txt

RUN mkdir input
RUN mkdir output
RUN mkdir config

CMD python start.py