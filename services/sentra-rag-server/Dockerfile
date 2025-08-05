ARG BASE_IMAGE=sentra-rag-base:latest
FROM ${BASE_IMAGE}

WORKDIR /app

# Copy and install core packages
COPY core/sentra-core /core/sentra-core
COPY core/sentra-rag /core/sentra-rag
RUN pip install -e /core/sentra-core
RUN pip install -e /core/sentra-rag

# Install rag-server-specific requirements
COPY services/sentra-rag-server/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/sentra-rag-server /app

CMD ["python", "-m", "sentra_rag_server.main"]