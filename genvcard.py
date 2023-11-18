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
    parser_initdb = subparsers.add_parser("initdb", help="Initialize the PostgreSQL database")
    parser_initdb.add_argument("-u", "--name", action="store",help="Add username", type = str ,default= "harish")
    parser_initdb.add_argument("-s", "--dbname", action="store",help="Data base name", type = str ,default= "your_db")
    # load csv
    parser_load = subparsers.add_parser("load", help="Load CSV file into the PostgreSQL database")
    parser_load.add_argument("ipfile", help="Name of input csv file")
    parser_load.add_argument("-t" , "--tablename", help="Specify your table name" , type=str , default="employee")
    parser_load.add_argument("-u", "--name", action="store",help="Add username", type = str ,default= "harish")
    parser_load.add_argument("-s", "--dbname", action="store",help="Data base name", type = str ,default= "your_db")
    # create vcard
    parser_vcard= subparsers.add_parser("create", help="Initialize creating vcard and qrcode")
    parser_vcard.add_argument("-u", "--name", action="store",help="Add username", type = str ,default= "harish")
    parser_vcard.add_argument("-s", "--dbname", action="store",help="Data base name", type = str ,default= "your_db")
    parser_vcard.add_argument("-t" , "--tablename", help="Specify your table name" , type=str , default="employee")
    parser_vcard.add_argument("-n", "--number", help="Number of vcard to generate", action='store', type=int, default=10)
    parser_vcard.add_argument("-m", "--max", help="Maximum number of vcard to generate", action='store_true')
    parser_vcard.add_argument("-o", "--overwrite", help="Overwrite directory",action='store_true',default=False)
    parser_vcard.add_argument("-d", "--dimension", help="Change dimension of QRCODE", type = str ,default= "200",choices=range(100,501) )
    parser_vcard.add_argument("-a", "--address", help="Change address of the vcard", type = str , default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America" )
    parser_vcard.add_argument("-b", "--qr_and_vcard", help="Get qrcode along with vcard, Default - vcard only", action='store_true')
    args = parser.parse_args()
    return args

def setup_logging(level_name):
    global logger
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

def create_database(connection_params):
    try:

        default_connection_params = {
        "user": connection_params["user"],
        "database": "postgres" 
    }

        default_connection = psycopg2.connect(**default_connection_params)
        default_cursor = default_connection.cursor()


        default_cursor.execute("COMMIT")  # Make sure we're not in a transaction block
        default_cursor.execute(f"CREATE DATABASE {connection_params['database']}")
        default_cursor.close()
        default_connection.close()

        logger.info("Database created successfully.")
    except psycopg2.Error as e:
        logger.error("Error creating database: %s", e)
        
def create_table(connection_params,table_name):
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()
    try:
        with open("employees.sql", "r") as insert_file:
            insert_query = insert_file.read().replace('%s', table_name)
            cursor.execute(insert_query)

        connection.commit()
        logger.info("Table created successfully.")

    except Exception as e:
        logger.error(f"Error: {e}")
        connection.rollback()
        raise

def insert_data_to_db(data, connection_params,table_name):
    try:
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()

        for row in data:
            cursor.execute(f"""
                INSERT INTO {table_name} (first_name, last_name, designation, email, phone)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (row[0], row[1], row[2], row[3], row[4]))
            employee_id = cursor.fetchone()
            logger.debug("Inserted data for employee with ID: %s", employee_id)
            logger.info("Inserted data successfully.")

        connection.commit()

    except psycopg2.Error as e:
        logger.error("Error inserting data into the database: %s", e)

    finally:
        if connection:
            cursor.close()
            connection.close()

def fetch_data_from_db(connection_params,table_name):
    try:
        connection = psycopg2.connect(**connection_params)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        return data
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

#makes data from csv file to a list
def get_data(gensheet):
    data = []
    with open(gensheet, 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data
    
#generate content of vcard  
def gen_vcard(data,address):
        sl_no , lname , fname , designation , email , phone = data
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
        return content , email

#generate qrcode
def generate_qrcode(data , qr_dia,address):
    content , email = gen_vcard(data,address)
    endpoint = "https://chart.googleapis.com/chart"
    parameters = {
                   "cht" : "qr",
                   "chs" : qr_dia+"x"+qr_dia,
                   "chl" : content
                   }
    qrcode = requests.get(endpoint , params=parameters)
    with open(f"qrcode/{email}.png" ,'wb') as qr_pic:
        qr_pic.write(qrcode.content)

#write content to file        
def write_vcard_only(data,vc_count,address):
    for i in range(vc_count):
        if len(data[i]) < 5:
            logger.warning("line: %d Not enough data to generate in the line", i+1)
        else:
            vcard , email = gen_vcard(data[i],address)
            file = open(f"vcard/{email}.vcf" ,'w')
            file.write(vcard)
            logger.debug("line: %d Generated vcard %s", i+1,email)
    logger.info("Done generating vcard only")  
       
def write_vcard_and_qr(data,vc_count , dimension,address):
    for i in range(vc_count):
        vcard , email = gen_vcard(data[i],address)
        file = open(f"vcard/{email}.vcf" ,'w')
        file.write(vcard)
        generate_qrcode(data[i],dimension,address)
        logger.debug("%d Generated and qrcode %s", i+1, email)
    logger.info("Done generating vcard and qrcode")   

#checks for csv file
def is_csv_file(filename):
    return filename.lower().endswith('.csv')

#checks file exists
def file_exists(filename):
    if not os.path.exists(filename) or not os.path.isfile(filename):
        logger.error("%s file not exists",filename)
        exit(1)
        
def make_dir_vcard():
    if os.path. exists("vcard"):
        shutil.rmtree("vcard")
        os.makedirs("vcard")
    else:
        os.makedirs("vcard")
    
def make_dir_qrcode():
    if os.path. exists("qrcode"):
        shutil.rmtree("qrcode")
        os.makedirs("qrcode")
    else:
        os.makedirs("qrcode")

    
def main():
    args = parse_args()
    if args.verbose:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
    
    if args.subcommand == "initdb":
        connection_params = {
        "user": args.name,
        "database": args.dbname
                             }
        create_database(connection_params)
    
    elif args.subcommand == "load":
        try:
         connection_params = {
        "user": args.name,
        "database": args.dbname
                              }
         file_exists(args.ipfile) #checks if file exists
         if not is_csv_file(args.ipfile): #checks for csv file
             logger.error("Please provide valid file format, example file with .csv format")
             exit(1)
         else:
             data = get_data(args.ipfile)
             create_table(connection_params,args.tablename)
             insert_data_to_db(data,connection_params,args.tablename)
        except Exception as e:
            logger.warning("Create one using initdb : use -h for help")

        
    elif args.subcommand == "create":
        try:
            connection_params = {
        "user": args.name,
        "database": args.dbname
                              }
            data_from_db = fetch_data_from_db(connection_params,args.tablename)

            if args.overwrite:
                if os.path. exists("vcard"):
                    shutil.rmtree("vcard")
                elif os.path. exists("qrcode"):
                    shutil.rmtree("qrcode")
            elif os.path. exists("vcard") or os.path. exists("qrcode"):
                logger.error("The folder already exist : -o for overwrite")
                exit(1)
            if args.max:
                args.number = len(data_from_db)
            elif args.qr_and_vcard:
                if args.dimension.isnumeric():
                    make_dir_vcard()
                    make_dir_qrcode()
                    write_vcard_and_qr(data_from_db,args.number,args.dimension,args.address)
                else:
                    logger.warning("""
                          You entered dimension %s is not valid,
                          please enter valid number,
                          example: numeric value between 100 to 500""",args.dimension)
            else:
                make_dir_vcard()
                write_vcard_only(data_from_db,args.number,args.address)
        except Exception as e:
            logger.warning("Create one using initdb : use -h for help")
        
 
    


      
if __name__ == "__main__":
    main()
