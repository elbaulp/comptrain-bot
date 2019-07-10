FROM python:3

ADD app.py /

RUN pip install python-telegram-bot bs4 requests schedule

CMD [ "python", "./app.py" ]
