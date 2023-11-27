import csv

data = []
with open('employees_none.csv', 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            data.append(row)
# print(data)
designation = {
     'system engineer': 0.1,
    'senior engineer' :0.2, 
    'junior engineer' :0.4, 
    'Tech lead' : 0.15, 
    'project manager':0.15
}

l=len(data)
j=0
for key in designation:
    print(designation[key])
    rang = round(l * designation[key])
    for i in range(j,(j+rang)):
         data[i][2]=key
    j+=rang
with open('employees.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for i in data:
        writer.writerow(i)