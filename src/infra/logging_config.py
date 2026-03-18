from __future__ import annotations

import logging
from logging.config import dictConfig


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structured": {
                    "format": (
                        '{"timestamp":"%(asctime)s",'
                        '"level":"%(levelname)s",'
                        '"logger":"%(name)s",'
                        '"message":"%(message)s"}'
                    ),
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "structured",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        },
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
