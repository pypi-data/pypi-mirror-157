import time
import logging
import prometheus_client
from flask import request, Response
from timeit import default_timer
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import multiprocess, CollectorRegistry


logger = logging.getLogger(__name__)


class ApiMonitor(object):
    """call prometheus client to generate metrics， expandable
    :parameter
    app_name: monitored app name, format: /asmapi/v1
    """
    def __init__(self, app_name=None):
        # constructing basic information
        if app_name is None:
            logger.error("Incomplete parameters， please give the parameters as required.")
            return
        self.app_name = app_name
        # a list for filtering app name
        self.filter_paths = [app_name, app_name + "/", app_name + "/swagger.json"]
        self.filter_method = ["OPTIONS"]
        self.content_type_latest = "text/plain; version=0.0.2; charset=utf-8"

        # call the interface of prometheus
        self.registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(self.registry)
        self.define_metrics()

    def define_metrics(self):
        """Define different metrics here， if you need to expand, here"""
        self.http_request_total = Counter(
            'request_count_total',
            'Total number of HTTP requests',
            ['app_name', 'method', 'endpoint', 'status'],
            registry=self.registry)
        self.request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            " HTTP request duration in seconds",
            ("app_name", "method", "endpoint", "status"),
            registry=self.registry
        )
        self.request_latency = Histogram(
            'request_latency_seconds', 'Request latency',
            ['app_name', 'endpoint'],
            registry=self.registry
        )

        self.request_in_progress = Gauge(
            'flask_requests_in_progress_total', 'Requests in progress',
            ['app_name', 'endpoint', 'method']
        )
        self.request_response_time = Gauge(
            'flask_requests_last_response_time', 'Response time',
            ['app_name', 'endpoint', 'method']
        )
        # add a metrics of api request size bytes  use summary
        self.response_size_bytes = Summary(
            'flask_response_size_bytes', 'Response size bytes',
            ("app_name", "method", "endpoint", "status"),
            registry=self.registry
        )

    def filter_request(self):
        if self.app_name not in request.path or request.path in self.filter_paths or request.method in self.filter_method:
            return 1
        return 0

    def start_timer(self):
        if self.filter_request():
            return
        request.prom_start_time = default_timer()
        request.start_time = time.time()
        self.request_in_progress.labels(self.app_name, request.path, request.method).inc()

    def stop_timer(self, response):
        if self.filter_request():
            return response
        resp_time = time.time() - request.start_time
        self.request_latency.labels(self.app_name, request.path).observe(resp_time)
        self.request_response_time.labels(self.app_name, request.path, request.method).set(resp_time)
        self.request_in_progress.labels(self.app_name, request.path, request.method).dec()
        # add metrics for request duration in a second
        total_time = max(default_timer() - request.prom_start_time, 0)
        self.request_duration_seconds.labels(self.app_name, request.method, request.path, response.status_code).observe(total_time)
        self.response_size_bytes.labels(self.app_name, request.method, request.path, response.status_code).observe(response.data.__sizeof__())
        return response

    def record_request_data(self, response):
        if self.filter_request():
            return response
        self.http_request_total.labels(self.app_name, request.method, request.path, response.status_code).inc()
        return response

    def setup_metrics(self, app):
        app.before_request(self.start_timer)
        app.after_request(self.record_request_data)
        app.after_request(self.stop_timer)

        @app.route('/metrics')
        def metrics():
            return Response(prometheus_client.generate_latest(self.registry), mimetype=self.content_type_latest)
