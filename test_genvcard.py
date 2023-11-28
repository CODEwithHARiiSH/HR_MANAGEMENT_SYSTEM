from genvcard import *

def test_getdata():
    path = 'sample_csv/testcsv.csv'
    assert get_data(path) == [["Warren","Tammy","Information officer","tammy.warre@romero.org","(794)913-7421"],
["Rodgers","Cheryl","Microbiologist","chery.rodge@cameron-sanders.com","634-332-7960"]]
    

def test_getvcard():
    data = [[1,"Warren","Tammy","Information officer","tammy.warre@romero.org","(794)913-7421"]]
    adress = "abs"
    assert gen_vcard(data,adress) == ("""BEGIN:VCARD
VERSION:2.1
N:Tammy;Warren
FN:Warren Tammy
ORG:Authors, Inc.
TITLE:Information officer
TEL;WORK;VOICE:(794)913-7421
ADR;WORK:;;abs
EMAIL;PREF;INTERNET:tammy.warre@romero.org
REV:20150922T195243Z
END:VCARD
""" , "Warren" )
    
def test_getleave_datalen6(caplog):
    data = [[2,1,"Warren","tammy.warre@romero.org","Information officer",10]]
    
    assert get_leave_data(data) == """
LEAVE DATA
ID:1
NAME:Warren
EMAIL:tammy.warre@romero.org
DESIGNATION:Information officer
LEAVES TAKEN:2
TOTAL LEAVES:10
REMAINING LEAVES:8

To export this to a file use export command
"""

def test_getleave_datalen5(caplog):
    data = [[1,"Warren","tammy.warre@romero.org","Information officer",10]]
    
    assert get_leave_data(data) == """
LEAVE DATA
ID:1
NAME:Warren
EMAIL:tammy.warre@romero.org
DESIGNATION:Information officer
LEAVES TAKEN:0
TOTAL LEAVES:10
REMAINING LEAVES:10

To export this to a file use export command
"""