FROM python:3.9.1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install --no-install-recommends -y bash
RUN apt-get install --no-install-recommends -y build-essential
RUN apt-get install --no-install-recommends -y curl
RUN apt-get install --no-install-recommends -y nano

WORKDIR /store

COPY requirements.txt /store/

RUN pip3 install -r requirements.txt

COPY . /store/
