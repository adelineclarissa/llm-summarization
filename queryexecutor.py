import pandas as pd


class QueryExecutor:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def execute_query(self, query, params=None):
        """Execute a SQL query using the provided database connection."""
        if not self.db_connection.is_connected():
            raise ConnectionError("Database connection is not established.")

        try:
            return pd.read_sql_query(
                query, self.db_connection.connection, params=params
            )
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error
