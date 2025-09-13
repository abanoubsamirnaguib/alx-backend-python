#!/usr/bin/env python3
"""
Module for database connection and transaction handling decorators
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


def transactional(func):
    """
    Decorator that ensures a function runs inside a database transaction
    If the function raises an error, the transaction is rolled back
    Otherwise, the transaction is committed
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with transaction handling
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function
            result = func(conn, *args, **kwargs)
            
            # If no exceptions, commit the transaction
            conn.commit()
            print("User email updated successfully")
            return result
        except Exception as e:
            # If an exception occurs, rollback the transaction
            conn.rollback()
            print(f"Transaction failed: {str(e)}")
            # Re-raise the exception for handling by the caller
            raise e
    
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Update a user's email address
    
    Args:
        conn: Database connection (injected by decorator)
        user_id: ID of the user to update
        new_email: New email address to set
        
    Returns:
        None
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


if __name__ == "__main__":
    # Update user's email with automatic transaction handling
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')