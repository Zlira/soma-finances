###########
# BUILDER #
###########

FROM python:3.8-slim-buster as builder

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
    && apt-get -y install python3-dev libmariadbclient-dev gcc


RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheel -r requirements.txt


#########
# FINAL #
#########

FROM python:3.8-slim-buster

WORKDIR /usr/src/app

RUN apt-get update && apt-get -y install netcat mariadb-client
COPY --from=builder /usr/src/app/wheel /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]