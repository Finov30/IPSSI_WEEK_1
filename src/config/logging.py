"""Configuration du logging."""

import json
import logging
import sys
from pathlib import Path
from typing import Any

from src.config.settings import get_settings


def setup_logging() -> None:
    """Configure le logging de l'application."""
    settings = get_settings()

    # Créer les dossiers de logs
    log_dirs = ["logs/etl", "logs/api", "logs/processing"]
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Configuration du format
    if settings.log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.log_level))

    # Configuration root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    root_logger.addHandler(console_handler)


class JsonFormatter(logging.Formatter):
    """Formatter JSON pour les logs structurés."""

    def format(self, record: logging.LogRecord) -> str:
        """Formate le log en JSON."""
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Ajouter les champs supplémentaires
        if hasattr(record, "module"):
            log_data["module"] = record.module
        if hasattr(record, "function"):
            log_data["function"] = record.function

        # Ajouter l'exception si présente
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)

