FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install shared library
COPY services/sentra-api/requirements.txt /app/requirements.txt
COPY libs/sentra-shared /libs/sentra-shared
RUN pip install -e /libs/sentra-shared

# Install requirements (editable install)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the service code
COPY services/sentra-api /app

EXPOSE 8100
EXPOSE 5678

CMD ["python", "-m", "sentra_brain_api.main"]
