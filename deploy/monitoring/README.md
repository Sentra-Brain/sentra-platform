# Sentra Brain Observability Stack

This directory contains the configuration for the observability stack integrated into the Sentra Brain development environment.

## Components

### Prometheus (Metrics Collection)
- **URL**: http://localhost:9090
- **Purpose**: Collects metrics from all Sentra services
- **Configuration**: `prometheus.yml`

### Grafana (Visualization & Dashboards)
- **URL**: http://localhost:3000
- **Credentials**: admin/admin
- **Purpose**: Visualizes metrics, logs, and traces
- **Configuration**: `grafana/provisioning/`

### Loki (Log Aggregation)
- **URL**: http://localhost:3100
- **Purpose**: Centralized log storage and querying
- **Configuration**: `loki-config.yaml`

### Promtail (Log Shipping)
- **Purpose**: Ships container logs from Docker to Loki
- **Configuration**: `promtail-config.yaml`

### OpenTelemetry Collector (Telemetry Ingestion)
- **OTLP gRPC**: http://localhost:4317
- **OTLP HTTP**: http://localhost:4318
- **Metrics**: http://localhost:8888/metrics
- **Purpose**: Receives traces, metrics, and logs from instrumented applications
- **Configuration**: `otel-collector-config.yaml`

### Jaeger (Distributed Tracing)
- **URL**: http://localhost:16686
- **Purpose**: Trace visualization and analysis
- **Integration**: Receives traces from OpenTelemetry Collector

### PostgreSQL Exporter
- **Metrics**: http://localhost:9187/metrics
- **Purpose**: Exports PostgreSQL database metrics

## Services Instrumentation

### Sentra API (FastAPI)
- **Metrics**: http://localhost:8080/metrics
- **Instrumentation**: OpenTelemetry FastAPI, SQLAlchemy, Requests
- **Features**: Correlation ID tracking, distributed tracing

### Sentra RAG Worker (Python)
- **Metrics**: http://localhost:8081/metrics (mapped from container port 8080)
- **Instrumentation**: OpenTelemetry with job processing metrics
- **Features**: Job duration tracking, error counting

## Key Features

### Correlation IDs
All requests include correlation IDs that flow through:
- HTTP headers (`x-correlation-id`)
- Trace spans
- Log entries
- Metrics labels

### Metrics Available
- HTTP request rates and duration
- Database connection counts
- RAG job processing metrics
- Service health status
- Error rates

### Logs
- Structured JSON logs from all containers
- Automatic parsing and labeling
- Container-specific log streams
- Error and debug level filtering

### Traces
- End-to-end request tracing
- Database query tracing
- External service call tracing
- Error propagation tracking

## Getting Started

1. Start the development environment:
   ```bash
   cd deploy
   docker compose -f docker-compose.dev.yml up -d
   ```

2. Access the dashboards:
   - **Grafana**: http://localhost:3000 (admin/admin)
   - **Prometheus**: http://localhost:9090
   - **Jaeger**: http://localhost:16686

3. Generate some activity by using the Sentra Brain API

4. View metrics and logs in Grafana

## Dashboards

### Sentra Brain Overview
- Service health status
- HTTP request rates
- Log aggregation
- Key performance indicators

Additional dashboards can be added to `grafana/provisioning/dashboards/`.

## Development

### Adding New Metrics
1. Update the service's observability module
2. Add new Prometheus metrics
3. Update Grafana dashboards if needed

### Adding New Traces
1. Use OpenTelemetry SDK in your code
2. Create spans for important operations
3. Include relevant attributes and correlation IDs

### Debugging
- Check service logs in Grafana
- Use Jaeger for trace debugging
- Monitor metrics in Prometheus

## Configuration

All configuration files are in this directory:
- `prometheus.yml` - Prometheus scrape configuration
- `loki-config.yaml` - Loki log aggregation settings
- `promtail-config.yaml` - Log shipping configuration
- `otel-collector-config.yaml` - OpenTelemetry collector settings
- `grafana/provisioning/` - Grafana datasources and dashboards