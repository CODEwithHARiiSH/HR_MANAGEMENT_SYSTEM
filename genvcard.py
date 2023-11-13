import csv
from sys import argv

script, gensheet= argv
#get data from csv file(csv file passed as an argument)

def get_data(gensheet):
    data = []
    with open(gensheet, 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data
