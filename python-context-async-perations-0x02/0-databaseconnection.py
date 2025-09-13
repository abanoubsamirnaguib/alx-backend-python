#!/usr/bin/env python3
"""
Module that implements a DatabaseConnection context manager
for automatically handling database connections.
"""
import sqlite3


class DatabaseConnection:
    """
    A context manager for database connections.
    This class automatically handles opening and closing database connections.
    """

    def __init__(self, db_path=':memory:'):
        """
        Initialize the database connection parameters.

        Args:
            db_path (str): Path to the SQLite database file,
                          or ':memory:' for an in-memory database
        """
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        """
        Enter the context manager: establish the database connection.
        
        Returns:
            self: The connection object that can be used to query the database
        """
        print(f"Connecting to SQLite database at {self.db_path}...")
        self.connection = sqlite3.connect(self.db_path)
        # Configure the connection to return rows as dictionaries
        self.connection.row_factory = sqlite3.Row
        
        # Create a users table if it doesn't exist (for demonstration)
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        
        # Insert some sample data if the table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                [
                    ("Alice", "alice@example.com"),
                    ("Bob", "bob@example.com"),
                    ("Charlie", "charlie@example.com")
                ]
            )
            self.connection.commit()
            
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager: close the database connection.

        Args:
            exc_type: The exception type if an exception occurred
            exc_val: The exception value if an exception occurred
            exc_tb: The traceback if an exception occurred
        """
        if self.connection:
            print("Closing SQLite database connection...")
            self.connection.close()
        
        # Return False to propagate exceptions if they occurred
        return False

    def execute_query(self, query, params=None):
        """
        Execute a SQL query on the database.

        Args:
            query (str): The SQL query to execute
            params (tuple): Optional parameters for the query

        Returns:
            list: The results of the query
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
        
        print(f"Executing query: {query}")
        cursor = self.connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # If this is a SELECT query, return the results
        if query.strip().upper().startswith("SELECT"):
            return [dict(row) for row in cursor.fetchall()]
        
        # Otherwise, commit the changes and return empty list
        self.connection.commit()
        return []


if __name__ == "__main__":
    # Use the context manager with a with statement
    with DatabaseConnection() as db:
        # Execute a query
        results = db.execute_query("SELECT * FROM users")
        
        # Print the results
        print("\nQuery Results:")
        for row in results:
            print(row)
    
    # The connection is automatically closed when exiting the with block
    print("\nExecution completed successfully!")