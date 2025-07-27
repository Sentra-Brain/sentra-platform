FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app:/shared"

COPY services/shared/sentra-shared /shared
RUN pip install -e /shared

COPY services/sentra-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY services/sentra-api /app

ENV PYTHONPATH="/app:/shared"

EXPOSE 8100
EXPOSE 5678

RUN echo $PYTHONPATH && ls -la /shared && ls -la /app

CMD ["python", "-m", "sentra_brain_api.main"]
