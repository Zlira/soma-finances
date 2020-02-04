###########
# BUILDER #
###########

FROM python:3.8-alpine as builder

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update \
    && apk add mariadb-dev gcc python3-dev musl-dev g++


RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheel -r requirements.txt


#########
# FINAL #
#########

FROM python:3.8-alpine

WORKDIR /usr/src/app

RUN apk update && apk add  mariadb-connector-c-dev libstdc++
COPY --from=builder /usr/src/app/wheel /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY . /usr/src/app/
