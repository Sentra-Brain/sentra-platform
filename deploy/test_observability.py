#!/usr/bin/env python3
"""
Simple test script to verify observability stack functionality
"""
import requests
import time
import json
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource


def setup_tracing():
    """Setup OpenTelemetry tracing for test script"""
    resource = Resource.create({
        "service.name": "test-script",
        "service.version": "1.0.0",
        "service.namespace": "sentra",
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    return trace.get_tracer(__name__)


def test_observability_stack():
    """Test all components of the observability stack"""
    tracer = setup_tracing()
    
    with tracer.start_as_current_span("test_observability") as span:
        span.set_attribute("test.type", "observability_verification")
        
        print("🔍 Testing Observability Stack...")
        
        # Test Prometheus
        try:
            response = requests.get("http://localhost:9090/api/v1/query?query=up", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Prometheus: {len(data.get('data', {}).get('result', []))} targets discovered")
                span.set_attribute("prometheus.targets", len(data.get('data', {}).get('result', [])))
            else:
                print(f"❌ Prometheus: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Prometheus: {e}")
        
        # Test Loki
        try:
            response = requests.get("http://localhost:3100/ready", timeout=5)
            if response.status_code == 200:
                print("✅ Loki: Ready for log ingestion")
                span.set_attribute("loki.status", "ready")
            else:
                print(f"❌ Loki: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Loki: {e}")
        
        # Test OpenTelemetry Collector
        try:
            response = requests.get("http://localhost:13133", timeout=5)
            if response.status_code == 200:
                print("✅ OpenTelemetry Collector: Health check passed")
                span.set_attribute("otel.collector.status", "healthy")
            else:
                print(f"❌ OpenTelemetry Collector: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ OpenTelemetry Collector: {e}")
        
        # Test Grafana
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Grafana: Running and accessible")
                span.set_attribute("grafana.status", "running")
            else:
                print(f"❌ Grafana: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Grafana: {e}")
        
        # Test Jaeger
        try:
            response = requests.get("http://localhost:16686/", timeout=5)
            if response.status_code == 200:
                print("✅ Jaeger: UI accessible")
                span.set_attribute("jaeger.status", "accessible")
            else:
                print(f"❌ Jaeger: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Jaeger: {e}")
        
        print("\n📊 Summary: Observability stack components tested")
        span.set_attribute("test.completed", True)


if __name__ == "__main__":
    test_observability_stack()
    print("\n⏳ Waiting for traces to be exported...")
    time.sleep(3)
    print("✅ Test completed!")