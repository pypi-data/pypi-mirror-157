"""
Logging Module
"""
import json
import logging
import sys
from typing import Any

from flask import g, has_request_context

from app import settings


class GCPStructuredLogFormatter(logging.Formatter):
    """
    Formats logging.LogRecord to GCP Structured Log
    """
    PYTHON_TO_GCP_LOG_LEVEL = {
        "CRITICAL": "CRITICAL",
        "FATAL": "CRITICAL",
        "ERROR": "ERROR",
        "WARN": "WARNING",
        "WARNING": "WARNING",
        "INFO": "INFO",
        "DEBUG": "DEBUG",
        "NOTSET": "DEBUG",
    }
    PYTHON_LOG_KEYS_TO_IGNORE = ["name", "msg", "args", "levelname", "levelno", "created", "msecs", "exc_info",
                                 "relativeCreated", "thread", "threadName", "processName", "process", "message"]

    def format(self, record: logging.LogRecord) -> str:
        message = super(GCPStructuredLogFormatter, self).format(record)
        # Generate JSON as per GCP LogEntry
        # See https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
        log = dict(
            message=message,
            severity=self.PYTHON_TO_GCP_LOG_LEVEL.get(record.levelname),
            timestamp=record.created,
        )

        for key in vars(record):
            if key not in self.PYTHON_LOG_KEYS_TO_IGNORE:
                log[key] = getattr(record, key, None)

        return self.serialize(log)

    def default_serializer(self, o: Any) -> str:
        """
        Returns the Class name of the object.
        """
        return str(type(o))

    def serialize(self, log: dict) -> str:
        """
        Serializes the log and ensures that all failure cases are handled.
        This method will serialize the dict without raising any error,
        if error occurs serializing any attribute, it will either skip it or assign a default value.
        """
        return json.dumps(log, skipkeys=True, default=self.default_serializer)


class ContextFilter(logging.Filter):
    """
    Enhances the logging.LogRecord with contextual information
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            setattr(record, "trace_id", self.trace_id())
            setattr(record, "request_id", self.request_id())
            for key, value in self.log_context().items():
                setattr(record, key, value)
        finally:
            return True

    @staticmethod
    def trace_id() -> str:
        return getattr(g, "trace_id", None) if has_request_context() else None

    @staticmethod
    def request_id() -> str:
        return getattr(g, "request_id", None) if has_request_context() else None

    @staticmethod
    def log_context() -> dict:
        return getattr(g, "log_context", dict()) if has_request_context() else dict()


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Return a new logger with GCPStructuredLogFormatter
    """
    formatter = GCPStructuredLogFormatter("%(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)

    _logger = logging.getLogger(name)
    _logger.setLevel(log_level)
    _logger.addHandler(sh)
    _logger.addFilter(ContextFilter())
    return _logger


logger = get_logger(__name__, settings.LOG_LEVEL)
