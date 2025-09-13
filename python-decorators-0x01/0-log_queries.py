#!/usr/bin/env python3
"""
Module for SQL query logging decorator
"""
import sqlite3
import functools
from datetime import datetime


def log_queries():
    """
    Decorator that logs SQL queries before executing them
    Returns:
        The wrapped function 
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract query from arguments or keyword arguments
            query = kwargs.get('query')
            if not query and args:
                query = args[0]
            
            # Log the query with timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Query: {query}")
            
            # Execute the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


@log_queries()
def fetch_all_users(query):
    """
    Fetch all users from the database
    Args:
        query: SQL query to execute
    Returns:
        List of user records
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    # Fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")