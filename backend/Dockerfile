FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /django

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000
