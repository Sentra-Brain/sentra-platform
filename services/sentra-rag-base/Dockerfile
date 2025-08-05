# Dockerfile for sentra-rag-base
FROM python:3.13-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /base

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1
