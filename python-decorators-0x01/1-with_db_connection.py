#!/usr/bin/env python3
"""
Module for database connection handling decorator
"""
import sqlite3
import functools


def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with automatic connection handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Ensure connection is closed even if an exception occurs
            conn.close()
    
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetch a user by ID from the database
    
    Args:
        conn: Database connection (injected by decorator)
        user_id: ID of the user to fetch
        
    Returns:
        User record or None if not found
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


if __name__ == "__main__":
    # Fetch user by ID with automatic connection handling
    user = get_user_by_id(user_id=1)
    print(user)