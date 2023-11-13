from genvcard import *

def test_getdata():
    with open("gensheets.csv", 'r') as file:
         csvreader = csv.reader(file)
    assert get_data() == [["Warren","Tammy,Information officer","tammy.warre@romero.org","(794)913-7421"],
["Rodgers","Cheryl,Microbiologist","chery.rodge@cameron-sanders.com","634-332-7960"]]
    
