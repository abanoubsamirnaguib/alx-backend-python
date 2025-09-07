import csv

def stream_users_in_batches(batch_size):
    """Yield batches of users from user_data.csv."""
    with open('python-generators-0x00/user_data.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        batch = []
        for row in reader:
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch


def batch_processing(batch_size):
    """Process each batch and print users over age 25."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if int(user['age']) > 25:
                print(user)
