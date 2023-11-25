import argparse
import csv
import logging
import os ,shutil
import psycopg2
import requests


logger = None

def parse_args():

    parser = argparse.ArgumentParser(prog="gen_vcard.py", description="Generates vCards and QR codes from a CSV file and stores in a PostgreSQL database.")
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")
    # initdb
    parser_initdb = subparsers.add_parser("initdb", help="Initialize the PostgreSQL database and create table")
    parser_initdb.add_argument("-s", "--dbname", action="store",help="Data base name", type = str ,default= "your_db")
    # load csv
    parser_load = subparsers.add_parser("load", help="Load CSV file into the PostgreSQL database")
    parser_load.add_argument("-i","--ipfile", help="Name of input csv file")
    parser_load.add_argument("-t" , "--tablename", help="Specify your table name" , type=str , default="employee")
    parser_load.add_argument("-s", "--dbname", action="store",help="Data base name", type = str ,default= "your_db")
    parser_load.add_argument("-e", "--employee_id", help="specify employee id", type=int, action="store")
    parser_load.add_argument("-d", "--date", help="specify data", type=str, action="store")
    parser_load.add_argument("-r", "--reason", help="specify reason for leave", type=str, action="store")
    # create vcard
    parser_vcard= subparsers.add_parser("create", help="Initialize creating vcard and qrcode")
    parser_vcard.add_argument("-s", "--dbname", action="store",help="Data base name", type = str ,default= "your_db")
    parser_vcard.add_argument("-d", "--dimension", help="Change dimension of QRCODE", type = str ,default= "200")
    parser_vcard.add_argument("-b", "--qr_and_vcard", help="Get qrcode along with vcard, Default - vcard only", action='store_true')
    parser_vcard.add_argument("-l", "--leaves", help="Get leaves count as a text file", action='store_true')
    parser_vcard.add_argument("-e", "--employee_id", help="Specify employee id", type=int, action="append")
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

        
def create_table(connection_params):
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    try:
        with open("sql_querries/employees.sql", "r") as insert_file:
            insert_query = insert_file.read()
            cursor.execute(insert_query)
        connection.commit()
        logger.info("Table created successfully.")

    except Exception as e:
        logger.error(f"Error: {e}")
        connection.rollback()
        raise
    
    finally:
        if connection:
            cursor.close()
            connection.close()

#makes data from csv file to a list
def get_data(gensheet):
    data = []
    with open(gensheet, 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data

def insert_data_to_employees(data, connection_params):
    try:
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()
        for row in data:
            cursor.execute("""
                INSERT INTO employees (first_name, last_name, designation, email, phone)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (row[0], row[1], row[2], row[3], row[4]))
            employee_id = cursor.fetchone()
            logger.debug("Inserted data for employee with ID: %s", employee_id)
        logger.info("Inserted data into employees successfully.")
        connection.commit()
        cursor.close()
        connection.close()
    except psycopg2.Error as e:
        logger.error("Error inserting data into the employees: %s", e)

def insert_data_into_leaves(connection_params,id,date,reason):
    try:
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()
        data = fetch_data_from_leaves(connection_params,id)
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
        logger.debug("Inserted data for employee with ID: %s", employee_id)
        logger.info("Inserted data into leaves successfully.")
        connection.commit()
        cursor.close()
        connection.close()
    except psycopg2.Error as e:
        logger.error("Error inserting data into the leaves: %s", e)

def fetch_data_from_employees(connection_params,id):
    try:
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM employees where id = {id};")
        data = cursor.fetchall()
        return data
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

def fetch_data_from_leaves(connection_params,employee_id):
    try:
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()
        cursor.execute(f"""select count (e.id) as count, e.id,e.first_name , e.email,e.designation ,d.no_of_leaves from employees e 
                            join leaves l on e.id = l.employee_id join designation d on e.designation = d.designation 
                              where e.id={employee_id} group by e.id,e.first_name,e.email,d.no_of_leaves;""")
        data = cursor.fetchall()
        if data:
            return data
        else:
            cursor.execute(f"""select e.id ,e.first_name , e.email,e.designation ,d.no_of_leaves from employees e 
            join designation d on e.designation = d.designation where e.id={employee_id} group by e.id,e.first_name,e.email,d.no_of_leaves;""")
            data = cursor.fetchall()
            return data
            
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
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

#generate content for leave count
def gen_leave_count(data):
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
                logger.debug("Done generating leaves count for %s",name) 
            elif len(data) == 5:
                id,name , email,designation,total_leaves = data
                count = 0
                remaining = total_leaves - count
                writer.writerow([id,name,email,designation,count,total_leaves,remaining])
                logger.debug("Done generating leaves count for %s",name) 

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

#write content to file        
def write_vcard_only(data,id):
    vcard , fname = gen_vcard(data,id)
    if not os.path. exists("OUTPUT"):
        os.makedirs("OUTPUT")
    file = open(f"OUTPUT/{fname}.vcf" ,'w')
    file.write(vcard)
    logger.debug("line: Generated vcard for %s",fname)
         
def write_vcard_and_qr(data,id,dimension):
    vcard , fname = gen_vcard(data,id)
    if not os.path. exists("OUTPUT"):
        os.makedirs("OUTPUT")
    file = open(f"OUTPUT/{fname}.vcf" ,'w')
    file.write(vcard)
    generate_qrcode(data,dimension,id)
    logger.debug("Generated and qrcode %s", fname)
     
#checks for csv file
def is_csv_file(filename):
    return filename.lower().endswith('.csv')
#checks file exists
def file_exists(filename):
    if not os.path.exists(filename) or not os.path.isfile(filename):
        logger.error("%s file not exists",filename)
        exit(1)
   
def main():
    args = parse_args()
    setup_logging(args)
    if args.subcommand == "initdb":
        connection_params = {"database": args.dbname}
        create_table(connection_params)
    elif args.subcommand == "load":
             connection_params = {"database": args.dbname }
             if args.ipfile:
                file_exists(args.ipfile) #checks if file exists
                if not is_csv_file(args.ipfile): #checks for csv file
                    logger.error("Please provide valid file format, example file with .csv format")
                    exit(1)
                data = get_data(args.ipfile)
                insert_data_to_employees(data,connection_params)
             elif args.tablename == "leaves":
                insert_data_into_leaves(connection_params,args.employee_id,args.date,args.reason)
    elif args.subcommand == "create":
            connection_params = {"database": args.dbname }
            if args.all:
                employee_id = [i for i in range (1,51)]
            else:
                employee_id = args.employee_id
            if args.qr_and_vcard:
                for i in employee_id:
                    data_from_db = fetch_data_from_employees(connection_params,i)
                    if args.dimension.isnumeric():
                        write_vcard_and_qr(data_from_db,employee_id,args.dimension) 
                    else:
                        logger.warning("""
                          You entered dimension %s is not valid,
                          please enter valid number,
                          example: numeric value between 100 to 500""",args.dimension)
                logger.info("Done generating vcard and qrcode")
            elif args.leaves:
                leave_data = []
                for i in employee_id:
                    data_from_leaves = fetch_data_from_leaves(connection_params,i)
                    for i in data_from_leaves:
                        leave_data.append(i)
                    gen_leave_count(leave_data)
                logger.info("Done creating leave data")
            else:
                for i in employee_id:
                    data_from_db = fetch_data_from_employees(connection_params,i)
                    write_vcard_only(data_from_db,args.employee_id)
                logger.info("Done generating vcard only")
    
if __name__ == "__main__":
    main()