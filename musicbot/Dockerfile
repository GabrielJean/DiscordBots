# Multi-stage build for musicbot
FROM python:3.14-slim AS build

RUN apt-get update && apt-get install -y git ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.14-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=build /install /usr/local

# Copy bot files into container
COPY . /app
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

CMD ["python3", "main.py"]

