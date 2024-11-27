import mysql.connector


class DatabaseConnection:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """Establish the database connection."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("Successfully connected to the database.")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def is_connected(self):
        """Check if the connection is still active."""
        return self.connection and self.connection.is_connected()
