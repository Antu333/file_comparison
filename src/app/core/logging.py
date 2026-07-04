import logging
import logging.config
from pathlib import Path

# -----------------------------------------------------------------------------
# Log directory
# -----------------------------------------------------------------------------

LOGS_DIR = Path(__file__).resolve().parents[3] / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "brief": {
            "format": "%(asctime)s | %(levelname)-8s | %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "brief",
            "stream": "ext://sys.stdout",
        },

        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(LOGS_DIR / "app.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
        },

        "error_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "ERROR",
            "formatter": "standard",
            "filename": str(LOGS_DIR / "error.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
        },
    },

    "loggers": {
        # ---------------------------------------------------------------------
        # Your application
        # Every module under src.* will inherit this logger.
        # Example:
        #   logger = logging.getLogger(__name__)
        # ---------------------------------------------------------------------
        "src": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },

        # ---------------------------------------------------------------------
        # Uvicorn
        # ---------------------------------------------------------------------
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },

        "uvicorn.error": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },

        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },

        # ---------------------------------------------------------------------
        # Third-party libraries
        # ---------------------------------------------------------------------
        "httpx": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },

        "google": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },

    # -------------------------------------------------------------------------
    # Root logger
    # -------------------------------------------------------------------------
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}


def setup_logging() -> None:
    """Configure application logging."""
    logging.config.dictConfig(LOGGING_CONFIG)

    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Logging initialized")
    logger.info("Log directory: %s", LOGS_DIR)
    logger.info("=" * 70)