1. OBJECTIVE:

Generates visiting cards , QRCODE or leaves count for a list of employees provided in a CSV
file


2. INPUT:

1.1. Command-Line Arguments:
    1. In command line there are three choices initdb ,import, load , generate,export.
       
       1. initdb will create table in the database. You can specify the databse name using -db command.
        For this first you need to create a user manually. And using that username you can create table directly.
         
         : initdb -h for help  
                    usage: gen_vcard.py initdb [-h]

                    Creates table

                    options:
                    -h, --help  show this help message and exit

      2. import will inser employee data from csv file to database
         
         : import -h for help
           Example:
                usage: gen_vcard.py import [-h] employee_file

                  Imports list of employees into the system

                  positional arguments:
                    employee_file  CSV file of employees to load

                  options:
                    -h, --help     show this help message and exit

          * If you sppecify csv file the data will automatically insert to employees table

       3. load will insert leave data into the table in the  database.
         
         : load -h for help
          Example:

                    Add leaves taken by the employee

                    positional arguments:
                      employee_id           specify employee id

                    options:
                      -h, --help            show this help message and exit
                      -d DATE, --date DATE  Enter a date in the format 2023-12-12
                      -r REASON, --reason REASON
                                            specify reason for leave

      * If you want to insert data to leaves use -t "leaves" then add datas 
                  for example : python3 genvcard.py 7 -d "2023-11-27" -r "fever"
    4. Generate will generate vcard and leave data.
       
       : generate -h for help
       Example: 
                  Generate vcard and employee leave data

                  options:
                    -h, --help            show this help message and exit
                    -e EMPLOYEE_ID, --employee_id EMPLOYEE_ID
                                          Specify employee id
                    -l, --leaves          get leave data

        * Default is vcard only : python3 genvcard.py generate -e <id>
        * If you give -l you will get leave count as text file : python3 genvcard.py generate  -l -e <id>
        * -b for getting qr along with vcard : python3 genvcard.py generate -b -e <id>
        * For getting multiple person's data use : python3 genvcard.py generate  -e 3 -e9 
        * For getting all employees data use : python3 genvcard.py generate -a

    5. Export employee data to  output folder.
         
         : export  -h for help
                    Export employee data to output folder

                    positional arguments:
                      opfolder              specify the file name

                    options:
                      -h, --help            show this help message and exit
                      -f OPFILE, --opfile OPFILE
                                            specify the file name
                      -e EMPLOYEE_ID, --employee_id EMPLOYEE_ID
                                            Specify employee id
                      -d DIMENSION, --dimension DIMENSION
                                            Change dimension of QRCODE
                      -q, --qrcode          Get qrcode along with vcard, Default - vcard only
                      

         code : python3 genvcard.py export <file name>

    2. Arguments: Add -h or --help for getting new arguments.
    
    3. For customizing qrcode size, it will only take numeric characters from 100 to 500
    
1.2. Csv file

     Each row in the csv_file should have the following columns

           : Williams,Annette,Psychiatrist,annet.willi@holloway.org,9305709284

             This is the last name, first name, designation, email address and
             phone number. 

    A sample input file `sample_employees.csv` is provided in the folder samplecsvs.


3. OUTPUT:

    The code will generate one vCard and QRCODE file per row in the csv_file. The filename will be the first name in the row (e.g. foo.vcf/png). 
    All the files will be in the `output` directory(vcard , qrcode and leave data).

      * This is a sample vcard file
        
                    BEGIN:VCARD
                    VERSION:2.1
                    N:Reeves;Anne
                    FN:Anne Reeves
                    ORG:Authors, Inc.
                    TITLE:Visual merchandiser
                    TEL;WORK;VOICE:666.808.0750x9935
                    ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
                    EMAIL;PREF;INTERNET:anne.reeve@davis.com
                    REV:20150922T195243Z
                    END:VCARD

        The vCard file will have email as file name.
        
        * The QRCODE will contains this data

        * The leaves count data:
          The leave data will be a csv file containing all the datas of employee

          example:   [NAME,EMAIL,DESIGNATION,LEAVES TAKEN,TOTAL LEAVES,REMAINING LEAVES]

4. EXECUTION:

The script can be executed from the command line using:
 
    python genvcard.py -h
    
    * For getting help menu
    
    example:  
            Employee information manager for a small company.

            positional arguments:
              {initdb,import,load,generate,export}
                                    Subcommands
                initdb              Initialize table
                app                 initialise api call for react
                import              Import employee list
                load                Add leaves taken by the employee
                generate            Generate vcard and employee leave data
                export              Export employee data to output folder


            options:
              -h, --help            show this help message and exit
              -v, --verbose         Print detailed logging
              -d DBNAME, --dbname DBNAME
                                    Data base name
              -a, --all             Get data of all employee during generation and export

              
5. App
  App is for initialise api for react

Default dbname is hrms


You can Change this using -u and -db commands