FROM python:3.10

ENV PYTHONBUFFERED 1
ENV PYTHONPATH /opt/bot

RUN mkdir /opt/bot
WORKDIR /opt/bot
COPY ./app ./app
COPY ./main.py ./main.py
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
COPY ./.env ./.env
CMD ["python", "-u", "main.py"]