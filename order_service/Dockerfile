FROM python:3.8

WORKDIR /project
RUN apt-get update
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
CMD cd app && gunicorn -c gunicorn_conf.py  wsgi:app