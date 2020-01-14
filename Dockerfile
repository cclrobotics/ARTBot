FROM python:3.8-alpine

RUN apk update && \
	apk add --virtual build-deps gcc python3-dev musl-dev zlib-dev jpeg-dev && \
	apk add postgresql-dev

ENV PYTHONDONOTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./web /usr/src/app/web
COPY ./migrations /usr/src/app/migrations

CMD flask run -h 0.0.0.0
