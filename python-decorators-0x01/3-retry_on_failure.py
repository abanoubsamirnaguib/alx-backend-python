#!/usr/bin/env python3
"""
Module for database connection and retry decorators
"""
import time
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


def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function if it raises an exception
    
    Args:
        retries: Number of retry attempts (default: 3)
        delay: Delay between retries in seconds (default: 2)
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            last_exception = None
            
            while attempts <= retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    last_exception = e
                    
                    if attempts <= retries:
                        print(f"Operation failed: {str(e)}. Retrying in {delay} seconds... "
                              f"(Attempt {attempts}/{retries})")
                        time.sleep(delay)
                    else:
                        print(f"All {retries} retry attempts failed. Giving up.")
                        raise last_exception
            
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetch all users from the database with automatic retry on failure
    
    Args:
        conn: Database connection (injected by decorator)
        
    Returns:
        List of user records
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    # Attempt to fetch users with automatic retry on failure
    users = fetch_users_with_retry()
    print(users)