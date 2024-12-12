import mysql.connector
from utility import setup_logging
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """Establish the database connection."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                logger.info("Successfully connected to the database.")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            self.connection = None

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed.")

    def is_connected(self):
        """Check if the connection is still active."""
        return self.connection and self.connection.is_connected()
