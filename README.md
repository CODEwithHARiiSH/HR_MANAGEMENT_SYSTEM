# HR_MANAGEMENT_SYSTEM

Generates visiting cards and QRCODE for a list of employees provided in a CSV
file

This wil also act as an api backend for react frontend
For that use model.py and app.py

## Files:

1. genvcard.py
2. test_genvcard.py
3. spec.md
4. employee.csv
5. model.py
6. app.py

## USAGE

* The gensheets.py file is using for creating a csv file from list of data.
It works by command line argument.

* test_genvcard.py is for testing genvcard.py

* 1st create a csv file using gensheets.py and use that file for genvcard.py
  ( For time being use employee.csv)

### How to run genvcard.py

* python3 genvcard.py initdb : for creating table
* pythone genvcard.py import : import employee list to database
* python3 genvcard.py add : Adds leave data of employees
* python3 genvcard.py export : for creating vcard , qrcode and leave data
* python3 genvcard.py generate : for generating vcard , qrcode and leave data
* python3 genvcar.py app : for intilise api for react

### How to run gensheets.py

* python genvcard.py  -h  : For help




