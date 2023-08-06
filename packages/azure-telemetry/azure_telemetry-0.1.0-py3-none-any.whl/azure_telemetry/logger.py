import logging
from opencensus.trace.tracer import Tracer
from opencensus.trace import config_integration
from opencensus.ext.azure import metrics_exporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.azure.log_exporter import AzureLogHandler


def callback_function(envelope):
    envelope.tags['ai.cloud.role'] = 'Audit_AIML'
    return True


class telemetryInsights:

    def __init_(self, text):
        self.text = "This class handles logs and performance counters to Azure Monitors"

    def logHandler(key):
        logger = logging.getLogger(__name__)
        handler = AzureLogHandler(
            connection_string='InstrumentationKey={}'.format(key))
        handler.add_telemetry_processor(callback_function)
        logger.addHandler(handler)
        return logger

    def performanceCounters(key):
        exporter = metrics_exporter.new_metrics_exporter(
            enable_standard_metrics=True, connection_string='InstrumentationKey={}'.format(key))
        exporter.add_telemetry_processor(callback_function)
        exporter.shutdown()

    def tracingHandler(key):
        config_integration.trace_integrations(['requests'])
        exporter = AzureExporter(
            connection_string='InstrumentationKey={}'.format(key)
        )
        exporter.add_telemetry_processor(callback_function)
        tracer = Tracer(exporter=exporter, sampler=ProbabilitySampler(1.0))
        with tracer.span(name="IUC_Finder function Sucessfully triggered"):
            print("returned output")
