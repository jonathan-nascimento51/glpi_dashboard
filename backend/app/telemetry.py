import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def init_sentry(dsn: str | None, environment: str, release: str):
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(level=None, event_level=None),
        ],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.2")),
    )


def init_otel(service_name: str, otlp_endpoint: str):
    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    RequestsInstrumentor().instrument()


def instrument_fastapi(app):
    FastAPIInstrumentor.instrument_app(app)
