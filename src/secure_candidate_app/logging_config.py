import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        structured_fields = [
            "request_id",
            "method",
            "path",
            "status_code",
            "latency_ms",
        ]

        for field_name in structured_fields:
            field_value = getattr(record, field_name, None)

            if field_value is not None:
                log_record[field_name] = field_value

        return json.dumps(log_record)


def configure_logging() -> None:
    """Configure application logging."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)