FROM python:3.7

MAINTAINER Solomon Akinyemi <solomon.akinyemi@gmail.com>

COPY . /auction_project

WORKDIR /auction_project
CMD tail -f /dev/null
#WORKDIR /auction_project
#RUN . bin/activate
#WORKDIR /challenge_src
#CMD python ./auction_v2.py
