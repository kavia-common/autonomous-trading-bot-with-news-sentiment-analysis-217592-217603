import json
import logging
import sys
from typing import Any, Dict

from src.config.settings import settings


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        log: Dict[str, Any] = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
        }
        # Include extra attributes if present
        for key, value in record.__dict__.items():
            if key not in ("args", "asctime", "created", "exc_info", "exc_text", "filename",
                           "funcName", "levelname", "levelno", "lineno", "module", "msecs",
                           "message", "msg", "name", "pathname", "process", "processName",
                           "relativeCreated", "stack_info", "thread", "threadName"):
                log[key] = value
        if record.exc_info:
            log["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False)


def configure_logging() -> None:
    """Configure root logger with JSON formatter and env-driven level."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)
