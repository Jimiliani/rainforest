FROM python:3.9.1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN pip install --upgrade pip
RUN apt-get install --no-install-recommends -y bash
RUN apt-get install --no-install-recommends -y build-essential
RUN apt-get install --no-install-recommends -y curl
RUN apt-get install --no-install-recommends -y nano

RUN mkdir /main

WORKDIR /main

COPY store/requirements.txt /main/

RUN pip3 install -r requirements.txt

COPY . /main/
