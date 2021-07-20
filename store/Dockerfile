FROM python:3.9.1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y \
    bash \
    build-essential \
    curl \
    nano
RUN pip install --upgrade pip


RUN mkdir /main

WORKDIR /main

COPY store/requirements.txt /main/

RUN pip3 install -r requirements.txt

COPY . /main/
