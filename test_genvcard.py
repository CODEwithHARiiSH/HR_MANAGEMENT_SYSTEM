from genvcard import *

def test_getdata():
    path = 'testcsv.csv'
    assert get_data(path) == [["Warren","Tammy","Information officer","tammy.warre@romero.org","(794)913-7421"],
["Rodgers","Cheryl","Microbiologist","chery.rodge@cameron-sanders.com","634-332-7960"]]
    

def test_getvcard():
    data = ["Warren","Tammy","Information officer","tammy.warre@romero.org","(794)913-7421"]
    assert gen_vcard(data) == ("""Name: Tammy
Full Name: Tammy Warren
ORG:Authors, Inc.
TITLE: Information officer
TEL;WORK;VOICE: (794)913-7421
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET: tammy.warre@romero.org
REV:20150922T195243Z
""" , "tammy.warre@romero.org" )
