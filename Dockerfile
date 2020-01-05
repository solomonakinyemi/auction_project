FROM python:3.7

MAINTAINER Solomon Akinyemi <solomon.akinyemi@gmail.com>
COPY . /auction_project

WORKDIR /auction_project

RUN python3 -mvenv auction_venv

#RUN . auction_venv/bin/activate

#CMD pip install --upgrade pip 

#CMD pip install -r requirements.txt

CMD tail -f /dev/null
