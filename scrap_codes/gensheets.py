import csv
import faker
from sys import argv
import random

script, gensheet , count= argv

def generate_data(count):
    f = faker.Faker()
    names = []
    for i in range(int(count)):
        record = []
        lname = f.last_name()
        fname = f.first_name()
        domain = f.domain_name()
        designation = 'none'
        email = f"{fname[:5].lower()}.{lname[:5].lower()}@{domain}"
        phone = f.phone_number()
        record = [lname, fname, designation, email, phone]
        names.append(record)
    return names

def get_csvfile(names):
    with open(f'{gensheet}', 'w', newline='') as file:
        writer = csv.writer(file)
        for i in names:
            writer.writerow(i)

if __name__ == "__main__":
    names=generate_data(count)
    get_csvfile(names)
