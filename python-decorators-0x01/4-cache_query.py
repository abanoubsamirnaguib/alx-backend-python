#!/usr/bin/env python3
"""
Module for database connection and caching decorators
"""
import time
import sqlite3
import functools


# Global cache dictionary to store query results
query_cache = {}


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


def cache_query(func):
    """
    Decorator that caches query results to avoid redundant database calls
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with caching capability
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Extract query parameter from args or kwargs
        query = kwargs.get('query')
        if not query and args:
            query = args[0]
            
        # If no query is provided, cannot cache
        if not query:
            return func(conn, *args, **kwargs)
            
        # Check if query result is already in cache
        if query in query_cache:
            print(f"Using cached result for query: {query}")
            return query_cache[query]
            
        # Execute the function to get the result
        result = func(conn, *args, **kwargs)
        
        # Cache the result
        query_cache[query] = result
        print(f"Cached result for query: {query}")
        
        return result
    
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetch users from the database with caching
    
    Args:
        conn: Database connection (injected by decorator)
        query: SQL query to execute
        
    Returns:
        List of user records
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call will cache the result
    print("First call:")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Found {len(users)} users")
    
    # Second call will use the cached result
    print("\nSecond call:")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Found {len(users_again)} users")