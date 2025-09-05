FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install shared library
COPY services/sentra-mcp/requirements.txt /app/requirements.txt
COPY packages/sentra-core /packages/sentra-core
RUN pip install -e /packages/sentra-core

# Install requirements (editable install)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the service code
COPY services/sentra-mcp /app

EXPOSE 8200
EXPOSE 5681

CMD ["python", "-m", "sentra_mcp.server"]
