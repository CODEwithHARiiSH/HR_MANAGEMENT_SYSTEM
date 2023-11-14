import csv
import os
import requests
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

#generate qrcode

def generate_qrcode(data):
    content , email = gen_vcard(data)
    endpoint = "https://chart.googleapis.com/chart"
    parameters = {
                   "cht" : "qr",
                   "chs" : "300x300",
                   "chl" : content
                   }
    qrcode = requests.get(endpoint , params=parameters)
    with open(f"qrcode/{email}.png" ,'wb') as qr_pic:
        qr_pic.write(qrcode.content)

#write content to file        
       
def write_vcard(data,vc_count):
    for i in range(vc_count):
        vcard , email = gen_vcard(data[i])
        file = open(f"vcard/{email}.vcf" ,'w')
        file.write(vcard)
        generate_qrcode(data[i])
       
        
if __name__ == "__main__":
    if not os.path.exists("vcard"):
        os.makedirs("vcard") 
    if not os.path.exists("qrcode"):
        os.makedirs("qrcode") 
        
    if argv[2].isnumeric():
        data = get_data(argv[1])
        write_vcard(data,int(argv[2]))
        
    elif argv[2] == "full":
        data = get_data(argv[1])
        write_vcard(data,len(data))




















