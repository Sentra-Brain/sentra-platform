"""
OpenTelemetry instrumentation setup for Sentra RAG Worker
"""
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
JOBS_PROCESSED = Counter('rag_jobs_processed_total', 'Total RAG jobs processed', ['status'])
JOB_DURATION = Histogram('rag_job_duration_seconds', 'RAG job processing duration', ['job_type'])
ACTIVE_JOBS = Gauge('rag_active_jobs', 'Currently active RAG jobs')
DOCUMENTS_INDEXED = Counter('documents_indexed_total', 'Total documents indexed')


def setup_tracing():
    """Setup OpenTelemetry tracing for RAG worker"""
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    service_name = os.getenv("OTEL_SERVICE_NAME", "Sentra.Rag.Worker")
    
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


def instrument_worker():
    """Instrument RAG worker with OpenTelemetry"""
    try:
        # Setup tracing
        tracer = setup_tracing()
        
        # Setup metrics
        setup_metrics()
        
        # Instrument requests
        RequestsInstrumentor().instrument()
        
        logger.info("OpenTelemetry instrumentation completed for RAG worker")
        return tracer
        
    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry instrumentation: {e}")
        return None


def trace_job_processing(job_type: str, correlation_id: str = None):
    """Decorator for tracing job processing"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(f"rag.job.{job_type}") as span:
                if correlation_id:
                    span.set_attribute('correlation_id', correlation_id)
                span.set_attribute('job_type', job_type)
                
                ACTIVE_JOBS.inc()
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    JOBS_PROCESSED.labels(status='success').inc()
                    span.set_attribute('status', 'success')
                    return result
                except Exception as e:
                    JOBS_PROCESSED.labels(status='error').inc()
                    span.set_attribute('status', 'error')
                    span.set_attribute('error', str(e))
                    raise
                finally:
                    ACTIVE_JOBS.dec()
                    duration = time.time() - start_time
                    JOB_DURATION.labels(job_type=job_type).observe(duration)
                    span.set_attribute('duration_seconds', duration)
        
        return wrapper
    return decorator


def get_correlation_id_from_message(message_data):
    """Extract correlation ID from message data"""
    try:
        return message_data.get('correlation_id', 'unknown')
    except (AttributeError, TypeError):
        return 'unknown'


import time