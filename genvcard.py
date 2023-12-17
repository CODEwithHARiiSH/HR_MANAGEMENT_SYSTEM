import argparse
import configparser
import csv
from datetime import datetime
import logging
import os
import requests

import db 
import web

import sqlalchemy as sa
from sqlalchemy.sql import func

logger = None

def parse_args():

    parser = argparse.ArgumentParser(prog="gen_vcard.py", description="Employee information manager for a small company.")
    parser.add_argument("-v", "--verbose", help="Print detailed logging", action='store_true', default=False)
    parser.add_argument("-a", "--all", help="Get data of all employee during generation and export",action='store_true')
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

    # initdb
    subparsers.add_parser("initdb", help="Initialize table",description="Creates table")
    subparsers.add_parser("web", help="Initialize web",description="Initialize web")

    #import employee data
    parser_import = subparsers.add_parser("import", help="Import employee list", description="Imports list of employees into the system")
    parser_import.add_argument("employee_file", help="CSV file of employees to load", action="store")

    # load csv
    parser_load = subparsers.add_parser("add", help="Add leaves taken by the employee",description="Add leaves taken by the employee")
    parser_load.add_argument("employee_id", help="specify employee id", type=int, action="store")
    parser_load.add_argument("-d", "--date", help="Enter a date in the format %(default)s", default="2023-12-12")
    parser_load.add_argument("-r", "--reason", help="specify reason for leave", type=str, default="Not specified")

    #generate data
    parser_gen= subparsers.add_parser("generate", help="Generate vcard and employee leave data",description="Generate vcard and employee leave data")
    parser_gen.add_argument("-e", "--employee_id", help="Specify employee id", type=int, action="append")
    parser_gen.add_argument("-l", "--leaves", help="get leave data" , action="store_true")

    # export  files
    parser_export= subparsers.add_parser("export", help="Export employee data to  output folder",description="Export employee data to output folder")
    parser_export.add_argument("opfolder", help="specify the file name")
    parser_export.add_argument("-f","--opfile", help="specify the file name")
    parser_export.add_argument("-e", "--employee_id", help="Specify employee id", type=int, action="append")
    parser_export.add_argument("-d", "--dimension", help="Change dimension of QRCODE", type = str ,default= "200")
    parser_export.add_argument("-q", "--qrcode", help="Get qrcode along with vcard, Default - vcard only", action='store_true')

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

#makes data from csv file to a list
def get_data(gensheet):
    data = []
    with open(gensheet, 'r') as file:
         csvreader = csv.reader(file)
         for row in csvreader:
             data.append(row)
    return data

#adds data to table
def add_employee(data,session):
    try:
        for datas in data:
            fname , lname ,designation , email , phone = datas
            query = sa.select(db.Designation).where(db.Designation.designation==designation)
            designation = session.execute(query).scalar_one()
            logger.debug("Inserting %s", email)
            employee = db.Employee(lname=lname,
                                fname=fname,
                                designation=designation,
                                email=email,
                                phone=phone)
            session.add(employee)
            session.commit()
            logger.debug("Inserted data for : %s", fname)
        logger.info("Inserted data into employees successfully.")
    except Exception as e:
        logger.error("Error inserting data into the employees: %s", e)


def add_designation(db_url):
    db.create_all(db_url)
    with db.get_session(db_url) as session:
        designations = [
            db.Designation(designation="system engineer", max_leaves=20),
            db.Designation(designation="senior engineer", max_leaves=18),
            db.Designation(designation="junior engineer", max_leaves=12),
            db.Designation(designation="Tech lead", max_leaves=12),
            db.Designation(designation="project manager", max_leaves=15),
        ]

        session.add_all(designations)
        session.commit()


#adds leaves to table
def add_leaves(args,session):
        data = fetch_leaves(args.employee_id,session)
        for data in data:
            if len(data) == 6:
                leaves_taken = data[0]
                total_leaves = data[5]
                name = data[3]
            elif len(data) == 5:
                leaves_taken = data[0]
                total_leaves = data[4]
                name = data[2]
        if leaves_taken == total_leaves:
            logger.warning("Employee  %s has taken maximum leaves",name)
        else:
            logger.debug("Inserting %s", args.employee_id)
            leave = db.Leave(date=args.date,
                                    employee_id=args.employee_id,
                                    reason=args.reason,
            )
            session.add(leave)
            session.commit()
            logger.debug("Inserted leaves of : %s", args.employee_id)
            logger.info("Inserted data into leaves successfully.")

#fetch employee data
def fetch_employees(employee_id,session):
        query = (
                session.query(
                    db.Employee.id,
                    db.Employee.fname,
                    db.Employee.lname,
                    db.Employee.email,
                    db.Employee.phone,
                    db.Designation.designation,
                )
                .join(db.Designation, db.Employee.designation_id == db.Designation.id)
                .filter(db.Employee.id == employee_id)
        )
        data = query.all()
        return data



#fetch leave data

def fetch_leaves(employee_id,session):
        # Using SQLAlchemy ORM to perform the query
        query = (
            session.query(
                func.count(db.Employee.id),
                db.Employee.id,
                db.Employee.fname,
                db.Employee.email,
                db.Designation.designation,
                db.Designation.max_leaves
            )
            .join(db.Leave, db.Employee.id == db.Leave.employee_id)
            .join(db.Designation, db.Employee.designation_id == db.Designation.id)
            .filter(db.Employee.id == employee_id)
            .group_by(
                db.Employee.id,
                db.Employee.fname,
                db.Employee.email,
                db.Designation.designation,
                db.Designation.max_leaves
            )
        )
        data = query.all()
        if not data:
            # If data is empty, try an alternative query
            query = (
                session.query(
                    db.Employee.id,
                    db.Employee.fname,
                    db.Employee.email,
                    db.Designation.designation,
                    db.Designation.max_leaves
                )
                .join(db.Designation, db.Employee.designation_id == db.Designation.id)
                .filter(db.Employee.id == employee_id)
            )
            data = query.all()
        return data


#generate content of vcard  
def gen_vcard(data):
        for data in data:
            sl_no ,  fname , lname ,designation , email , phone = data
            content = f"""BEGIN:VCARD
VERSION:2.1
N:{lname};{fname}
FN:{fname} {lname}
ORG:Authors, Inc.
TITLE:{designation}
TEL;WORK;VOICE:{phone}
ADR;WORK:;;Hamon North21 USA
EMAIL;PREF;INTERNET:{email}
REV:20150922T195243Z
END:VCARD
"""
        return content , fname


#generate csv file for leave count
def export_leave_data(data,args):
    if not data:
        logger.warning("Not a valid employee id")
        exit(1)
    if not os.path. exists(f"{args.opfolder}"):
        os.makedirs(f"{args.opfolder}") 
    with open(f'{args.opfolder}/{args.opfile}.csv', 'w') as file:
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


def get_leave_data(data):
    if not data:
        logger.warning("Not a valid employee id")
        exit(1)
    for data in data:
        if len(data) == 6:
            count , id , name , email , designation, total_leaves = data
            remaining = total_leaves - count
        elif len(data) == 5:
            id,name , email,designation,total_leaves = data
            count = 0
            remaining = total_leaves - count
        return f"""
LEAVE DATA
------------
ID:{id}
NAME:{name}
EMAIL:{email}
DESIGNATION:{designation}
LEAVES TAKEN:{count}
TOTAL LEAVES:{total_leaves}
REMAINING LEAVES:{remaining}

To export this to a file use export command
"""
    
#generate qrcode
def generate_qrcode(data , qr_dia,args):
    content , fname = gen_vcard(data)
    endpoint = "https://chart.googleapis.com/chart"
    parameters = {
                   "cht" : "qr",
                   "chs" : qr_dia+"x"+qr_dia,
                   "chl" : content
                   }
    if not os.path. exists(f"{args.opfolder}"):
        os.makedirs(f"{args.opfolder}")
    qrcode = requests.get(endpoint , params=parameters)
    with open(f"{args.opfolder}/{fname}.png" ,'wb') as qr_pic:
        qr_pic.write(qrcode.content)
    logger.debug("line: Generated qrcode for %s",fname)


#write content to file        
def write_vcard(data,args):
    vcard , fname = gen_vcard(data)
    if not os.path. exists(f"{args.opfolder}"):
        os.makedirs(f"{args.opfolder}")
    file = open(f"{args.opfolder}/{fname}.vcf" ,'w')
    file.write(vcard)
    logger.debug("line: Generated vcard for %s",fname)

def getemployeeids(args,session):
    if args.all:
        query = session.query(db.Employee.id)
        count = query.all()
        employee_id = []
        for i in count:
            employee_id.append(i[0])
    else:
        employee_id = args.employee_id
    return employee_id

def handle_initdb(args,_,dbname):
        try:
            db_uri = f"postgresql:///{dbname}"
            db.create_all(db_uri)
            add_designation(db_uri)
            logger.info("Intialised database and created table")
        except Exception as e:
            logger.error("Error creating table : (%s)",e)

def handle_import(args,session,_):
    try:
        data = get_data(args.employee_file)
        add_employee(data,session)
    except Exception as e:
        logger.error("Import failed : (%s)",e)

def handle_add(args,session,_):
    try:
        add_leaves(args,session)
    except Exception as e:
        logger.error("Error adding data : (%s)",e)
        
def handle_generate(args,session,_):
    try:
        employee_id = getemployeeids(args,session)
        leave_data = list()
        for i in employee_id:
            data_from_db = fetch_employees(i,session)
            data_from_leaves = fetch_leaves(i,session)
            leave_data.append(data_from_leaves[0])
            print(gen_vcard(data_from_db)[0])
            logger.debug("Done generating employee vcard--%s",i)
            if args.leaves:
                print(get_leave_data(leave_data))
                logger.debug("Done generating leave data--%s",i)
        logger.info("Done generating--%s",i)
    except Exception as e:
        print("Error generating : (%s)",e)

def handle_export(args,session,_):
    employee_id = getemployeeids(args,session)
    leave_data = list()
    for i in employee_id:
        data_from_db = fetch_employees(i,session)
        data_from_leaves = fetch_leaves(i,session)
        leave_data.append(data_from_leaves[0])
        if args.opfile:
            export_leave_data(leave_data,args)
        elif args.qrcode:
            generate_qrcode(data_from_db , args.dimension,args)
        else:
            write_vcard(data_from_db,args)
    logger.info("Done")

def handle_web(args,session,dbname):
    web.app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql:///{dbname}"
    web.db.init_app(web.app)
    web.app.run(debug=True)


def main():
    args = parse_args()
    setup_logging(args)
    config = configparser.ConfigParser()
    config.read('config.ini')
    dbname = config.get('Database', 'dbname')
    db_uri = f"postgresql:///{dbname}"
    session = db.get_session(db_uri)
    handlers = {"import" : handle_import,
                "export" : handle_export,
                "initdb" : handle_initdb,
                "generate" : handle_generate,
                "add"   : handle_add,
                "web" : handle_web
                }
    handlers[args.subcommand](args,session,dbname)
    
if __name__ == "__main__":
    main()