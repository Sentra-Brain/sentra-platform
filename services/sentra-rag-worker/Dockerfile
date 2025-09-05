ARG BASE_IMAGE=sentra-rag-base:latest
FROM ${BASE_IMAGE}

WORKDIR /app

# Copy and install core packages
COPY packages/sentra-core /packages/sentra-core
COPY packages/sentra-rag /packages/sentra-rag
RUN pip install -e /packages/sentra-core
RUN pip install -e /packages/sentra-rag

# Install worker-specific requirements
COPY services/sentra-rag-worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/sentra-rag-worker /app

CMD ["python", "-m", "sentra_rag_worker.main"]