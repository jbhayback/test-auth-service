FROM python:3.7-slim

RUN apt-get update -yqq \
    && apt-get install -yqq --no-install-recommends \
     build-essential \
     python3-dev \
     libevent-dev \
    && rm -rf /var/lib/apt/lists

ENV PYTHONUNBUFFERED 1

COPY ./api/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /usr/src/app
COPY . .

EXPOSE 8000

CMD python api/manage.py migrate && python runserver 0.0.0.0:8000
