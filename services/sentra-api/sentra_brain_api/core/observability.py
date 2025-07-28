"""
OpenTelemetry instrumentation setup for Sentra Brain API
"""
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')


def setup_tracing():
    """Setup OpenTelemetry tracing"""
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    service_name = os.getenv("OTEL_SERVICE_NAME", "sentra-api")
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "service.namespace": "sentra",
    })
    
    # Configure tracer
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    # OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    logger.info(f"OpenTelemetry tracing configured with endpoint: {otel_endpoint}")
    return tracer


def setup_metrics():
    """Setup Prometheus metrics endpoint"""
    metrics_port = int(os.getenv("METRICS_PORT", "8080"))
    try:
        start_http_server(metrics_port)
        logger.info(f"Prometheus metrics server started on port {metrics_port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")


def instrument_app(app):
    """Instrument FastAPI app with OpenTelemetry"""
    try:
        # Setup tracing
        tracer = setup_tracing()
        
        # Setup metrics
        setup_metrics()
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
        
        # Instrument requests
        RequestsInstrumentor().instrument()
        
        # Instrument SQLAlchemy
        SQLAlchemyInstrumentor().instrument()
        
        # Instrument psycopg2
        Psycopg2Instrumentor().instrument()
        
        logger.info("OpenTelemetry instrumentation completed")
        
    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry instrumentation: {e}")


def add_correlation_id_middleware(app):
    """Add correlation ID middleware for request tracing"""
    import uuid
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    from contextvars import ContextVar
    
    correlation_id_var: ContextVar[str] = ContextVar('correlation_id')
    
    class CorrelationIdMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            correlation_id = request.headers.get('x-correlation-id', str(uuid.uuid4()))
            correlation_id_var.set(correlation_id)
            
            # Add to current span
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute('correlation_id', correlation_id)
            
            response = await call_next(request)
            response.headers['x-correlation-id'] = correlation_id
            
            # Update metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            return response
    
    app.add_middleware(CorrelationIdMiddleware)
    logger.info("Correlation ID middleware added")


def get_correlation_id():
    """Get current correlation ID"""
    try:
        from contextvars import ContextVar
        correlation_id_var: ContextVar[str] = ContextVar('correlation_id')
        return correlation_id_var.get("unknown")
    except Exception:
        return "unknown"