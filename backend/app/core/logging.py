import logging
import sys
from app.config.settings import settings


def setup_logging() -> None:
    """Configures application-wide logging formats and handlers.

    Formats logs as JSON when running in production/staging environments,
    and as clean human-readable logs in development.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Base logging configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers (to avoid duplication)
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Determine formatter based on LOG_FORMAT config
    if settings.LOG_FORMAT.lower() == "json":
        # Production JSON Formatter
        import json

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_data = {
                    "timestamp": self.formatTime(record, self.datefmt),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "filename": record.filename,
                    "lineno": record.lineno,
                }
                # Inject extra parameters if present
                if hasattr(record, "correlation_id"):
                    log_data["correlation_id"] = record.correlation_id  # type: ignore
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)

        formatter = JsonFormatter()
    else:
        # Development Text Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(name)s:%(filename)s:%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Mute noisy library logging
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Expose standard logger getter helper
def get_logger(name: str) -> logging.Logger:
    """Returns a logger instance with the given name."""
    return logging.getLogger(name)
