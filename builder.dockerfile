FROM python:3.9-alpine
WORKDIR /
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt