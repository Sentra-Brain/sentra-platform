FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install shared library
COPY services/sentra-mcp/requirements.txt /app/requirements.txt
COPY packages/sentra-domain /packages/sentra-domain
COPY packages/sentra-shared /packages/sentra-shared
COPY packages/sentra-infra /packages/sentra-infra
RUN pip install -e /packages/sentra-domain
RUN pip install -e /packages/sentra-shared
RUN pip install -e /packages/sentra-infra

# Install requirements (editable install)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the service code
COPY services/sentra-mcp /app

EXPOSE 8200
EXPOSE 5681

CMD ["python", "-m", "sentra_mcp.server"]
