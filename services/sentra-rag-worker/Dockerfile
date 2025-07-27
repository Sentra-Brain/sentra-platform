FROM sentra-rag-base:py3.13

WORKDIR /app

COPY libs/sentra-shared /libs/sentra-shared
RUN pip install -e /libs/sentra-shared
COPY services/sentra-rag-worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/sentra-rag-worker /app

CMD ["python", "-m", "sentra_rag_worker.main"]