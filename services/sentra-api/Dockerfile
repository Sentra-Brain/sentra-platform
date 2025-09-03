FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install core library
COPY core/sentra-core /core/sentra-core
RUN pip install -e /core/sentra-core

# Copy and install engine legacy library
COPY core/sentra-engine-legacy /core/sentra-engine-legacy
RUN pip install -e /core/sentra-engine-legacy

# Copy and install engine library
COPY sentra-engine /sentra-engine
RUN pip install -e /sentra-engine

# Copy and install API requirements
COPY services/sentra-api/requirements.txt /app/requirements.txt

# Install requirements (editable install)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the service code
COPY services/sentra-api /app

EXPOSE 8100
EXPOSE 5678

CMD ["python", "-m", "sentra_brain_api.main"]
