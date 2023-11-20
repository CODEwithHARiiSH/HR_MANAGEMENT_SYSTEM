from genvcard import *

def test_getdata():
    path = 'sample_csv/testcsv.csv'
    assert get_data(path) == [["Warren","Tammy","Information officer","tammy.warre@romero.org","(794)913-7421"],
["Rodgers","Cheryl","Microbiologist","chery.rodge@cameron-sanders.com","634-332-7960"]]
    

def test_getvcard():
    data = [1,"Warren","Tammy","Information officer","tammy.warre@romero.org","(794)913-7421"]
    adress = "abs"
    assert gen_vcard(data,adress) == ("""BEGIN:VCARD
VERSION:2.1
N:Warren;Tammy
FN:Tammy Warren
ORG:Authors, Inc.
TITLE:Information officer
TEL;WORK;VOICE:(794)913-7421
ADR;WORK:;;abs
EMAIL;PREF;INTERNET:tammy.warre@romero.org
REV:20150922T195243Z
END:VCARD
""" , "tammy.warre@romero.org" )
