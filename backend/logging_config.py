import logging
import json
import sys
import os
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects suitable for cloud log aggregation
    (Datadog, Grafana Loki, CloudWatch, Google Cloud Logging).
    """

    # Standard attributes present on LogRecord that we don't want in 'extra'
    STANDARD_ATTRS = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message"
    }

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Extract any custom context passed via extra={...}
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in self.STANDARD_ATTRS and not key.startswith("_"):
                extra_fields[key] = value

        if extra_fields:
            log_entry["context"] = extra_fields

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(level=None, json_format=None):
    """
    Configures structured logging across the application.
    - level: Can be string ('DEBUG', 'INFO', etc.) or logging constant. Defaults to LOG_LEVEL env var or INFO.
    - json_format: True for JSON formatting; defaults to LOG_FORMAT=json env var.
    """
    if level is None:
        level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
    elif isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    if json_format is None:
        json_format = os.environ.get("LOG_FORMAT", "text").lower() == "json"

    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    # Configure root logger
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
    return root

