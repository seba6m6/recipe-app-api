FROM python:3.7-alpine
MAINTAINER Sebastian M

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requierements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user
