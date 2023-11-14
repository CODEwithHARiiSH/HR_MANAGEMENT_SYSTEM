# HR_MANAGEMENT_SYSTEM

Generates visiting cards and QRCODE for a list of employees provided in a CSV
file

## Files:

1. genvcard.py
2. test_genvcard.py
3. spec.txt
4. sample_employee.csv

## USAGE

* The gensheets.py file is using for creating a csv file from list of data.
It works by command line argument.

* test_genvcard.py is for testing genvcard.py

* 1st create a csv file using gensheets.py and use that file for genvcard.py
  ( For time being use employee.csv)

### How to run genvcard.py

* python3 genvcard.py <csv_file.csv> number of vcards to generate

### How to run gensheets.py

* python genvcard.py <csv_file> full : For generating vcards and QRCODEs for all rows.

* python genvcard.py <csv_file> <vc_count> : Will generate visiting cards and QRCODEs from starting to that number.



