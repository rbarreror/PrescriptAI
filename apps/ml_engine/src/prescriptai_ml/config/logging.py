import logging
import sys
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    #module_name: Optional[str] = "prescriptai_ml",
) -> None:
    """Configure structured console logging for the application and its dependencies.

    Args:
        log_level: Minimum severity level to display (DEBUG, INFO, WARNING, ERROR).
        module_name: Root package name to bind specific handler levels.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Standard format: timestamp, log level, module name, line number, message
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Docker best practice: stream logs directly to standard output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)

    # Configure root logger or package-specific logger
    root_logger = logging.getLogger()
    
    # Avoid adding duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        root_logger.setLevel(numeric_level)
        root_logger.addHandler(console_handler)
    # else:
    #     root_logger.setLevel(numeric_level)
    #     for handler in root_logger.handlers:
    #         handler.setFormatter(formatter)
    #         handler.setLevel(numeric_level)

    # Silence overly verbose third-party loggers if necessary
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)