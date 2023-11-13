import csv

def get_data():
    data = []
    with open("gensheets.csv", 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data
