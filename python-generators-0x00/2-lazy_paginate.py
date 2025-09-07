#!/usr/bin/python3
"""
This module implements a lazy pagination generator for users.
"""
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetch users from the database with pagination.
    
    Args:
        page_size: Number of records to fetch per page
        offset: Starting position for fetching records
        
    Returns:
        List of user dictionaries
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    A generator function that lazily paginates through user data.
    Only fetches the next page when needed, starting from offset 0.
    
    Args:
        page_size: Number of records to fetch per page
        
    Yields:
        A page of user records as a list of dictionaries
    """
    offset = 0
    while True:
        # Fetch the current page of results
        page = paginate_users(page_size, offset)
        
        # If the page is empty, we've reached the end of data
        if not page:
            break
            
        # Yield the current page and update offset for next page
        yield page
        offset += page_size
