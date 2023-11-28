import argparse
import configparser
import csv
import logging
import os
import psycopg2
import requests


logger = None

def update_config_file(dbname):
    config = configparser.ConfigParser()
    config.read('config.ini') 

    config.set('Database', 'dbname', dbname)

    with open('config.ini', 'w') as config_file:
        config.write(config_file)

def parse_args():

    # Read configuration from a file
    config = configparser.ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser(prog="gen_vcard.py", description="Employee information manager for a small company.")
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    parser.add_argument("-d", "--dbname", action="store",help="Data base name", type = str ,default=config.get('Database', 'dbname'))
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

    # initdb
    subparsers.add_parser("initdb", help="Initialize table",description="Creates table")

    #import employee data
    parser_import = subparsers.add_parser("import", help="Import employee list", description="Imports list of employees into the system")
    parser_import.add_argument("employee_file", help="CSV file of employees to load")

    # load csv
    parser_load = subparsers.add_parser("load", help="Add leaves taken by the employee",description="Add leaves taken by the employee")
    parser_load.add_argument("-e", "--employee_id", help="specify employee id", type=int, action="store")
    parser_load.add_argument("-d", "--date", help="specify data", type=str, action="store")
    parser_load.add_argument("-r", "--reason", help="specify reason for leave", type=str, action="store")

    # generate vcard,leave data , qrcode
    parser_vcard= subparsers.add_parser("export", help="Generate vcard,qrcode and employee leave data",description="Generate vcard,qrcode and employee leave data")
    parser_vcard.add_argument("-d", "--dimension", help="Change dimension of QRCODE", type = str ,default= "200")
    parser_vcard.add_argument("-b", "--qr_and_vcard", help="Get qrcode along with vcard, Default - vcard only", action='store_true')
    parser_vcard.add_argument("-l", "--leaves", help="Get leaves count as a text file", action='store_true')
    parser_vcard.add_argument("-e", "--employee_id", help="Specify employee id", type=int, action="append",default=[1,2,3,5,6,7,8,9,10])
    parser_vcard.add_argument("-a", "--all", help="Get data of all employee",action='store_true')
    args = parser.parse_args()
    return args


def setup_logging(args):
    global logger
    if args.verbose:
        level_name = logging.DEBUG
    else:
        level_name = logging.INFO
    logger = logging.getLogger("VCARDGEN")
    handler = logging.StreamHandler()
    fhandler = logging.FileHandler("run.log")
    fhandler.setLevel(logging.DEBUG)
    handler.setLevel(level_name)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    fhandler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fhandler)

        
def create_table(cursor):
    try:
        with open("sql_query/employees.sql", "r") as insert_file:
            insert_query = insert_file.read()
            cursor.execute(insert_query)
        logger.info("Table created successfully.")

    except Exception as e:
        logger.error("Error: %s",e)
        raise


#makes data from csv file to a list
def get_data(gensheet):
    data = []
    with open(gensheet, 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data


#adds data to table
def add_employee(data, cursor):
    try:
        for fname , lname ,designation , email , phone in data:
            cursor.execute("""
                INSERT INTO employees (first_name, last_name, designation, email, phone)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (fname , lname ,designation , email , phone))
            employee_id = cursor.fetchone()
            logger.debug("Inserted data for : %s", fname)
        logger.info("Inserted data into employees successfully.")
    except psycopg2.Error as e:
        logger.error("Error inserting data into the employees: %s", e)


#adds leaves to table
def add_leaves(cursor,id,date,reason):
    try:
        data = fetch_leaves(cursor,id)
        if len(data[0]) == 6:
            count , total_leaves,name = data[0][0] , data[0][5] , data[0][2]
        elif len(data[0]) == 5:
            count = 0
            total_leaves , name = data[0][4] , data[0][1]
        remaining = total_leaves - count
        if remaining == 0:
            logger.warning("%s has taken maximum allowed leaves", name)
            exit(1)
        else:
            cursor.execute("""
                INSERT INTO leaves (employee_id,leave_date,reason) VALUES (%s,%s,%s)
                RETURNING id;
            """, (id,date,reason))
        employee_id = cursor.fetchone()
        logger.debug("Inserted leaves of : %s", name)
        logger.info("Inserted data into leaves successfully.")
    except psycopg2.Error as e:
        logger.error("Error inserting data into the leaves: %s", e)


#fetch employee data
def fetch_employees(cursor,id):
    try:
        cursor.execute("SELECT * FROM employees where id = %s;",(id,))
        data = cursor.fetchall()
        return data
    except Exception as e:
        logger.error("Error fetching data: %s", e)
        raise


#fetch leave data
def fetch_leaves(cursor,employee_id):
    try:
        cursor.execute("""select count (e.id) as count, e.id,e.first_name , e.email,e.designation ,d.no_of_leaves from employees e 
                            join leaves l on e.id = l.employee_id join designation d on e.designation = d.designation 
                              where e.id=%s group by e.id,e.first_name,e.email,d.no_of_leaves;""",(employee_id,))
        data = cursor.fetchall()
        if data:
            return data
        else:
            cursor.execute(f"""select e.id ,e.first_name , e.email,e.designation ,d.no_of_leaves from employees e 
            join designation d on e.designation = d.designation where e.id=%s group by e.id,e.first_name,e.email,d.no_of_leaves;""",(employee_id,))
            data = cursor.fetchall()
            return data
            
    except Exception as e:
        logger.error("Error fetching data: %s",e)
        raise
    

#generate content of vcard  
def gen_vcard(data,address):
        sl_no ,  fname , lname ,designation , email , phone = data[0]
        content = f"""BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;{address}
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""
        return content , fname


#generate csv file for leave count
def gen_leave_data(data):
    if not data:
        logger.warning("Not a valid employee id")
        exit(1)
    if not os.path. exists("OUTPUT"):
        os.makedirs("OUTPUT") 
    with open('OUTPUT/leaves_data.csv', 'w') as file:
        writer=csv.writer(file)
        writer.writerow(['ID','NAME',"EMAIL",'DESIGNATION','LEAVES TAKEN','TOTAL LEAVES','REMAINING LEAVES'])
        for data in data:
            if len(data) == 6:
                count , id , name , email , designation, total_leaves = data
                remaining = total_leaves - count
                writer.writerow([id,name,email,designation,count,total_leaves,remaining])
                logger.debug("Done generating leaves data for %s",name) 
            elif len(data) == 5:
                id,name , email,designation,total_leaves = data
                count = 0
                remaining = total_leaves - count
                writer.writerow([id,name,email,designation,count,total_leaves,remaining])
                logger.debug("Done generating leave data for %s",name) 


#generate qrcode
def generate_qrcode(data , qr_dia,id):
    content , fname = gen_vcard(data,id)
    endpoint = "https://chart.googleapis.com/chart"
    parameters = {
                   "cht" : "qr",
                   "chs" : qr_dia+"x"+qr_dia,
                   "chl" : content
                   }
    if not os.path. exists("OUTPUT"):
        os.makedirs("OUTPUT")
    qrcode = requests.get(endpoint , params=parameters)
    with open(f"OUTPUT/{fname}.png" ,'wb') as qr_pic:
        qr_pic.write(qrcode.content)
    logger.debug("line: Generated qrcode for %s",fname)


#write content to file        
def write_vcard(data,id):
    vcard , fname = gen_vcard(data,id)
    if not os.path. exists("OUTPUT"):
        os.makedirs("OUTPUT")
    file = open(f"OUTPUT/{fname}.vcf" ,'w')
    file.write(vcard)
    logger.debug("line: Generated vcard for %s",fname)


#handle arguments
#initdb
def handle_initdb(args,cursor):
        create_table(cursor)
        update_config_file(args.dbname)

#import
def handle_import(args,cursor):
    try:
        data = get_data(args.employee_file)
        add_employee(data, cursor)
    except OSError as e:
        logger.error("Import failed - %s", e)

#load
def handle_load(args,cursor):
    try:
        add_leaves(cursor,args.employee_id,args.date,args.reason)
    except Exception as e:
        logger.error("No argument given : %s",e)

#export
def handle_export(args,cursor):
    try:
        if args.all:
            cursor.execute("SELECT count(id) FROM employees;")
            count = cursor.fetchone()
            print(count)
            employee_id = [i for i in range (1,count[0])]
        else:
            employee_id = args.employee_id
        if args.qr_and_vcard:
            for i in employee_id:
                data_from_db = fetch_employees(cursor,i)
                generate_qrcode(data_from_db,args.dimension,employee_id) 
            logger.info("Done generating qrcode")
        elif args.leaves:
            leave_data = []
            for i in employee_id:
                data_from_leaves = fetch_leaves(cursor,i)
                for i in data_from_leaves:
                    leave_data.append(i)
            gen_leave_data(leave_data)
            logger.info("Done creating leave data")
            exit(1)
        for i in employee_id:
            data_from_db = fetch_employees(cursor,i)
            write_vcard(data_from_db,args.employee_id)
        logger.info("Done generating vcard")
    except Exception as e:
        logger.error("Error generating : %s",e)


def main():
    args = parse_args()
    setup_logging(args)
    handlers = {"import" : handle_import,
                "export" : handle_export,
                "initdb" : handle_initdb,
                "load"   : handle_load}
    try:
        connection = psycopg2.connect(database=args.dbname)
        cursor = connection.cursor()
        handlers[args.subcommand](args,cursor)
        connection.commit()
        cursor.close()
        connection.close()
    except (KeyError,psycopg2.OperationalError) as e:
        logger.error("Error found : %s",e)

    
if __name__ == "__main__":
    main()