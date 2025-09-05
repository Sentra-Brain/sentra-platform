FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install core library
COPY packages/sentra-core /packages/sentra-core
RUN pip install -e /packages/sentra-core

# Copy and install engine library
COPY packages/sentra-runtime /packages/sentra-runtime
RUN pip install -e /packages/sentra-runtime

# Copy and install API requirements
COPY services/sentra-api/requirements.txt /app/requirements.txt

# Install requirements (editable install)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the service code
COPY services/sentra-api /app

EXPOSE 8100
EXPOSE 5678

CMD ["python", "-m", "sentra_brain_api.main"]
