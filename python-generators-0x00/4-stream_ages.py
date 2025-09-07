import csv

def stream_user_ages():
    """Generator that yields user ages one by one from user_data.csv."""
    with open('python-generators-0x00/user_data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            age = row.get('age')
            if age is not None:
                try:
                    yield int(age)
                except ValueError:
                    continue

def calculate_average_age():
    """Calculates and prints the average age using the generator."""
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    average = total_age / count if count > 0 else 0
    print(f"Average age of users: {average}")

if __name__ == "__main__":
    calculate_average_age()
