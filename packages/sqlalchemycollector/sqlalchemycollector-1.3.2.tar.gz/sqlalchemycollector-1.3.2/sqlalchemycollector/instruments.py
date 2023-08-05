from __future__ import absolute_import, division, print_function, unicode_literals

from socket import gethostname
import logging
import os
from typing import Optional
from distutils.util import strtobool

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, SERVICE_VERSION, Attributes
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry import trace

from opentelemetry.sdk.trace.sampling import ALWAYS_ON

from sqlalchemycollector.utils.once import Once
from sqlalchemycollector.version import __version__
from sqlalchemycollector.consts import (
    METIS_REQUEST_SPAN_ATTRIBUTE_IDENTIFIER,
)
from sqlalchemycollector.exporters.file_exporter import MetisFileExporter
from sqlalchemycollector.exporters.remote_exporter import MetisRemoteExporter
from sqlalchemycollector.plan_collect_type import PlanCollectType
from sqlalchemycollector.utils.env_var import extract_additional_tags_from_env_var
from sqlalchemycollector.utils.singleton_class import SingletonMeta

METIS_INSTRUMENTATION_STR = "METIS_INSTRUMENTATION"

logger = logging.getLogger(__name__)

FILE_NAME = "metis-log-collector.log"

os.environ[
    "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST"
] = "content-type,custom_request_header"
os.environ[
    "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE"
] = "content-type,content-length,custom_request_header"

EXPLAIN_SUPPORTED_STATEMENTS = (
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
)


def add_quote_to_value_of_type_string(value):
    if isinstance(value, str):
        new_value = str(value).replace("'", "''")
        return "'{}'".format(new_value)  # pylint: disable=consider-using-f-string
    return value


def fix_sql_query(sql, params):
    """without the fix the query is not working because string is not quoted"""
    fixed_param = params
    if isinstance(params, dict):
        fixed_param = {
            key: add_quote_to_value_of_type_string(value)
            for key, value in params.items()
        }

    return sql % fixed_param


def _normalize_vendor(vendor):
    """Return a canonical name for a type of database."""
    if not vendor:
        return "db"  # should this ever happen?

    if "sqlite" in vendor:
        return "sqlite"

    if "postgres" in vendor or vendor == "psycopg2":
        return "postgresql"

    return vendor


def _build_resource(
        service_name: str,
        service_version: str,
        resource_tags: Attributes,
) -> Resource:
    attrs = {}

    if service_name:
        attrs[SERVICE_NAME] = service_name
    if service_version:
        attrs[SERVICE_VERSION] = service_version

    try:
        attrs["host.name"] = gethostname()
    except Exception as e:
        logger.exception("Cloudnt get hostname for service")

    if resource_tags:
        attrs.update(_convert_items_to_metis_tags(resource_tags))

    metis_tags_env_vars = extract_additional_tags_from_env_var()
    if len(metis_tags_env_vars) > 0:
        attrs.update(_convert_items_to_metis_tags(metis_tags_env_vars))

    return Resource.create(attrs)


def _convert_items_to_metis_tags(tags_dict: Optional[Attributes]):
    return {f'app.tag.{key}': val for key, val in tags_dict.items()}


def setup(
        service_name: str,
        service_version: Optional[str] = None,
        resource_tags: Optional[Attributes] = None,
        plan_collection_option: Optional[PlanCollectType] = PlanCollectType.ESTIMATED,
        file_name: Optional[str] = None,
        api_key: Optional[str] = None,
        dsn: Optional[str] = None):
    _is_metis_instrumentation_enable = strtobool(os.getenv(METIS_INSTRUMENTATION_STR, 'true'))
    if not _is_metis_instrumentation_enable:
        logging.debug("Metis instrumentation is disabled")
        return

    metis_interceptor = MetisInstrumentor(service_name,
                                          service_version=service_version,
                                          resource_tags=resource_tags,
                                          plan_collection_option=plan_collection_option)

    metis_interceptor.set_exporters(file_name, api_key, dsn)

    return metis_interceptor


def shutdown():
    trace_provider = trace.get_tracer_provider()

    if trace_provider is not None:
        trace_provider.shutdown()


# pylint: disable=too-few-public-methods
class MetisInstrumentor(metaclass=SingletonMeta):
    def __init__(self,
                 service_name,
                 service_version: Optional[str] = None,
                 resource_tags: Optional[Attributes] = None,
                 plan_collection_option: Optional[PlanCollectType] = PlanCollectType.ESTIMATED,
                 ):
        self.api_instrumentor_app = None
        self.set_exporters_once = Once()
        self.sqlalchemy_instrumentor = None
        self.api_instrumentor = None
        self.plan_collection_option = plan_collection_option

        resource = _build_resource(service_name, service_version, resource_tags)

        self.tracer_provider = TracerProvider(sampler=ALWAYS_ON,
                                              resource=resource)

        self.tracer = trace.get_tracer(
            "metis",
            __version__,
            tracer_provider=self.tracer_provider,
        )

    def set_exporters(self,
                      file_name: Optional[str] = None,
                      api_key: Optional[str] = None,
                      dsn: Optional[str] = None):
        is_set = self.set_exporters_once.do_once(self._set_exporters,
                                                 file_name=file_name, api_key=api_key, dsn=dsn)

        if not is_set:
            logger.warning("You've setup metis instrumentation already")

    def _set_exporters(self,
                       file_name: Optional[str] = None,
                       api_key: Optional[str] = None,
                       dsn: Optional[str] = None):
        if not file_name and not dsn:
            file_name = os.getenv("METIS_LOG_FILE_NAME", FILE_NAME)
        if file_name:
            self._add_processor(BatchSpanProcessor(MetisFileExporter(file_name)))
        if bool(dsn) != bool(api_key):
            raise ValueError("Both endpoint and api_key must be provided")
        if dsn is not None:
            self._add_processor(BatchSpanProcessor(MetisRemoteExporter(dsn, api_key)))

        if strtobool(os.getenv("DEBUG", 'False')):
            self._add_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    def _add_processor(self, processor):
        self.tracer_provider.add_span_processor(processor)

    def instrument_app(self, app, engine):
        def request_hook(
                span: Span,
                message: dict,
        ):  # pylint: disable=unused-argument
            if span and span.is_recording():
                span.set_attribute(METIS_REQUEST_SPAN_ATTRIBUTE_IDENTIFIER, True)

        if self.api_instrumentor is None:
            self.api_instrumentor = FlaskInstrumentor()
            self.api_instrumentor_app = app

        self.api_instrumentor.instrument_app(
            app,
            tracer_provider=self.tracer_provider,
            request_hook=request_hook,
        )

        engine = engine.sync_engine if hasattr(engine, 'sync_engine') and engine.sync_engine is not None else engine
        from sqlalchemycollector.alchemy_instrumentation import MetisSQLAlchemyInstrumentor

        if self.sqlalchemy_instrumentor is None:
            self.sqlalchemy_instrumentor = MetisSQLAlchemyInstrumentor()

        self.sqlalchemy_instrumentor.instrument(
            engine=engine,
            plan_collection_option=self.plan_collection_option,
            trace_provider=self.tracer_provider,
        )

    def uninstrument_app(self):
        if self.api_instrumentor is not None:
            FlaskInstrumentor.uninstrument_app(self.api_instrumentor_app)
            self.api_instrumentor.uninstrument()
            self.api_instrumentor_app = None

        if self.sqlalchemy_instrumentor is not None:
            self.sqlalchemy_instrumentor.uninstrument()
