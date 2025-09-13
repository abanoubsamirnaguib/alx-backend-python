#!/usr/bin/env python3
"""
Module that implements an ExecuteQuery context manager
for executing database queries with automatic connection handling.
"""
import sqlite3


class ExecuteQuery:
    """
    A context manager for executing database queries.
    This class automatically handles opening and closing database connections
    and executing the given query.
    """

    def __init__(self, db_path=':memory:', query=None, params=None):
        """
        Initialize the ExecuteQuery context manager.

        Args:
            db_path (str): Path to the SQLite database file,
                          or ':memory:' for an in-memory database
            query (str): The SQL query to execute
            params (tuple): Optional parameters for the query
        """
        self.db_path = db_path
        self.query = query
        self.params = params
        self.connection = None
        self.results = None

    def __enter__(self):
        """
        Enter the context manager: establish the database connection
        and execute the query.
        
        Returns:
            list: The results of the query
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
                email TEXT NOT NULL,
                age INTEGER
            )
        ''')
        
        # Insert some sample data if the table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                [
                    ("Alice", "alice@example.com", 30),
                    ("Bob", "bob@example.com", 22),
                    ("Charlie", "charlie@example.com", 45),
                    ("David", "david@example.com", 18)
                ]
            )
            self.connection.commit()
        
        # Execute the query if provided
        if self.query:
            cursor = self.connection.cursor()
            if self.params:
                cursor.execute(self.query, self.params)
            else:
                cursor.execute(self.query)
            
            # If this is a SELECT query, store the results
            if self.query.strip().upper().startswith("SELECT"):
                self.results = [dict(row) for row in cursor.fetchall()]
            else:
                # Otherwise, commit the changes
                self.connection.commit()
                self.results = []
        
        return self.results

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


if __name__ == "__main__":
    # Use the context manager with a with statement
    with ExecuteQuery(
        query="SELECT * FROM users WHERE age > ?", 
        params=(25,)
    ) as results:
        # Print the results
        print("\nQuery Results:")
        if results:
            for row in results:
                print(row)
        else:
            print("No results found.")
    
    # The connection is automatically closed when exiting the with block
    print("\nExecution completed successfully!")