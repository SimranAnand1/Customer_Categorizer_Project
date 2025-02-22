FROM python:3.8.5-slim-buster

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN pip install certifi

RUN pip install evidently

CMD ["python3","app.py"]