FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y \
    bash \
    build-essential \
    curl \
    nano
RUN pip install --upgrade pip

WORKDIR /app

COPY data_generator/requirements.txt /app

RUN pip3 install -r requirements.txt

COPY data_generator/app /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
