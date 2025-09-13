#!/usr/bin/env python3
"""
Module that demonstrates concurrent database queries using asyncio and aiosqlite.
This module executes multiple database queries concurrently using asyncio.gather.
"""
import asyncio
import aiosqlite


async def setup_database():
    """
    Setup the database with sample data for demonstration.
    
    Returns:
        str: Path to the in-memory database
    """
    db_path = ':memory:'
    
    async with aiosqlite.connect(db_path) as db:
        # Enable returning rows as dictionaries
        db.row_factory = aiosqlite.Row
        
        # Create users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER
            )
        ''')
        
        # Insert sample data
        await db.executemany(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            [
                ("Alice", "alice@example.com", 30),
                ("Bob", "bob@example.com", 22),
                ("Charlie", "charlie@example.com", 45),
                ("David", "david@example.com", 50),
                ("Eve", "eve@example.com", 38)
            ]
        )
        
        await db.commit()
    
    return db_path


async def async_fetch_users(db_path):
    """
    Asynchronously fetch all users from the database.
    
    Args:
        db_path (str): Path to the SQLite database
        
    Returns:
        list: All users in the database
    """
    print("Starting to fetch all users...")
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            # Convert rows to dictionaries
            result = [dict(row) for row in rows]
            print(f"Fetched {len(result)} users")
            return result


async def async_fetch_older_users(db_path):
    """
    Asynchronously fetch users older than 40 from the database.
    
    Args:
        db_path (str): Path to the SQLite database
        
    Returns:
        list: Users older than 40
    """
    print("Starting to fetch users older than 40...")
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            rows = await cursor.fetchall()
            # Convert rows to dictionaries
            result = [dict(row) for row in rows]
            print(f"Fetched {len(result)} users older than 40")
            return result


async def fetch_concurrently():
    """
    Execute both queries concurrently using asyncio.gather.
    
    Returns:
        tuple: A tuple containing the results of both queries
    """
    # Setup the database
    db_path = await setup_database()
    
    # Run both queries concurrently
    print("Starting concurrent database queries...")
    all_users, older_users = await asyncio.gather(
        async_fetch_users(db_path),
        async_fetch_older_users(db_path)
    )
    
    print("\nResults from concurrent queries:")
    print(f"All users ({len(all_users)}):")
    for user in all_users:
        print(f"  - {user['name']}, {user['age']} years old")
    
    print(f"\nUsers older than 40 ({len(older_users)}):")
    for user in older_users:
        print(f"  - {user['name']}, {user['age']} years old")
    
    return all_users, older_users


if __name__ == "__main__":
    print("Running concurrent database queries with asyncio.gather\n")
    asyncio.run(fetch_concurrently())
    print("\nExecution completed successfully!")