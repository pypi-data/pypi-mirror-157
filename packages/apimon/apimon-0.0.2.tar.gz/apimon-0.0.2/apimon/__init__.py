from . import prometheus_init

name = "apimon"

# return  function at here
__all__ = ["ApiMonitor"]

ApiMonitor = prometheus_init.ApiMonitor

