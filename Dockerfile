FROM python:3.8-alpine

RUN apk update && \
	apk add --virtual build-deps gcc python3-dev musl-dev zlib-dev jpeg-dev && \
	apk add postgresql-dev libffi-dev curl

# set environment variables
ENV APP_HOME=/usr/src/app
ENV PYTHONDONOTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV production
ENV FLASK_APP web.app:create_app
ENV APP_SETTINGS web.settings.ProdConfig

# set working directory
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# add and install requirements
COPY ./requirements.txt $APP_HOME/requirements.txt
RUN pip install -r requirements.txt

# add app
COPY ./web $APP_HOME/web
COPY ./migrations $APP_HOME/migrations

# add and run as non-root user
RUN addgroup --gid 1024 artbot && adduser --disabled-password --gecos "" --ingroup artbot artbot
RUN chown -R artbot:artbot $APP_HOME
USER artbot

CMD gunicorn --bind 0.0.0.0:$PORT $FLASK_APP\(\)
