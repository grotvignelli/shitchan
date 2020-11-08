FROM python:3.8-alpine
MAINTAINER embong

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /chan
WORKDIR /chan
COPY ./chan /chan

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D embong
RUN chown -R embong:embong /vol/
RUN chmod -R 755 /vol/web
USER embong
