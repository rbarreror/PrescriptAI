import logging

from prescriptai_ml.config.settings import get_db_settings

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """"Provides a reusable database connection using SQLAlchemy engine."""

    def __init__(self):
        self._settings = get_db_settings()

    def connect(self):
        """Create a SQLAlchemy engine and return a connection context manager."""
        from sqlalchemy import create_engine

        engine = create_engine(self._settings.connection_url)
        logger.info("Database connection created.")
        return engine.connect()
