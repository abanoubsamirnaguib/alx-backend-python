from seed import connect_to_prodev

def stream_users():
    connection = connect_to_prodev()
    if not connection:
        return
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        for row in cursor:
            row['age'] = int(row['age'])
            yield row
    finally:
        cursor.close()
        connection.close()
