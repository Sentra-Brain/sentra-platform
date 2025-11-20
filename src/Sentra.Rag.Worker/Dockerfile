ARG BASE_IMAGE=sentra-rag-base:latest
FROM ${BASE_IMAGE}

WORKDIR /app

# Copy and install core packages
COPY ../packages/sentra-domain /packages/sentra-domain
COPY ../packages/sentra-shared /packages/sentra-shared
COPY ../packages/sentra-infra /packages/sentra-infra
COPY ../packages/sentra-rag /packages/sentra-rag
RUN pip install -e /packages/sentra-domain
RUN pip install -e /packages/sentra-shared
RUN pip install -e /packages/sentra-infra
RUN pip install -e /packages/sentra-rag

# Install worker-specific requirements
COPY src/Sentra.Rag.Worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/Sentra.Rag.Worker /app

CMD ["python", "-m", "sentra_rag_worker.main"]