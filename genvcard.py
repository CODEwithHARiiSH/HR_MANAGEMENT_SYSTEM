import csv
import os
#get data from csv file(csv file passed as an argument)

def get_data(gensheet):
    data = []
    with open(gensheet, 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data
    
def gen_vcard(data):
        lname , fname , designation , email , phone = data
        content = f"""Name: {fname}
Full Name: {fname} {lname}
ORG:Authors, Inc.
TITLE: {designation}
TEL;WORK;VOICE: {phone}
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET: {email}
REV:20150922T195243Z
"""
        return content , email
        
def write_vcard(vc_count):
    data = get_data(gensheet)
    for i in range(int(vc_count)):
        vcard , email = gen_vcard(data[i])
        file = open(f"vcard/{email}.txt" ,'w')
        file.write(vcard)
        
def make_newdirs():
    os.makedirs("vcard")      
        























