FROM python:3.9

RUN apt-get update
RUN apt-get install ffmpeg -y


WORKDIR /bdfrh
COPY ./bdfrtohtml/ ./bdfrtohtml
COPY ./requirements.txt ./requirements.txt
COPY ./config/config.yml ./config/config.yml
COPY ./config/default_bdfr_config.cfg ./config/default_bdfr_config.cfg

EXPOSE 7634

RUN pip install -r requirements.txt

RUN mkdir input
RUN mkdir output

CMD python -m bdfrtohtml automate