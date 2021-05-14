FROM python:3.9

RUN apt-get update
RUN apt-get install ffmpeg -y


WORKDIR /bdfrh
COPY ./bdfrtohtml/ ./bdfrtohtml
COPY ./templates/ ./templates
COPY ./start.py ./start.py

ENV BDFR_FREQ=15
ENV BDFR_IN=/input
ENV BDFR_OUT=/output
ENV BDFR_RECOVER_COMMENTS=True
ENV BDFR_ARCHIVE_CONTEXT=True
ENV BDFR_LIMIT=1100
ENV RUN_BDFR=False
ENV BDFRH_DELETE=False
ENV BDFRH_LOGLEVEL=INFO

EXPOSE 5000
EXPOSE 7634

RUN pip install -r requirements.txt

RUN mkdir input
RUN mkdir output
RUN mkdir config

CMD python start.py