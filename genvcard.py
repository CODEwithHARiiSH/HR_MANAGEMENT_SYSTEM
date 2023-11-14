import csv
import os
from sys import argv

#get data from csv file(csv file passed as an argument)

def get_data(gensheet):
    data = []
    with open(gensheet, 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data
    
#generate content of vcard  
def gen_vcard(data):
        lname , fname , designation , email , phone = data
        content = f"""BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""
        return content , email

#write content to file        
def write_vcard(vc_count):
    data = get_data(gensheet)
    for i in range(int(vc_count)):
        vcard , email = gen_vcard(data[i])
        file = open(f"vcard/{email}.txt" ,'w')
        file.write(vcard)
        
#create new folder        
def make_newdirs():
    os.makedirs("vcard")      
        
def get_argv():
     script, csvfile , number_count = argv
     return csvfile , number_count
 
if __name__ == "__main__":
    gensheet , vc_count = get_argv()
    data = get_data(gensheet)
    make_newdirs()
    write_vcard(vc_count)





















