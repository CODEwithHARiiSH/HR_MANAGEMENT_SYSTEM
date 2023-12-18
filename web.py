import flask
from flask import Response, jsonify,request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import db as model
from sqlalchemy.sql import func

app = flask.Flask("hrms")
CORS(app)
bcrypt = Bcrypt(app)
db = model.SQLAlchemy(model_class=model.HRDBBase)


@app.route("/employees")
def employees_list():
    query = db.select(model.Employee).order_by(model.Employee.fname)
    users = db.session.execute(query).scalars()
    ret=[]
    for user in users:
        ret .append({
            'id':user.id,
            'name':user.fname
        })
    return jsonify(ret)

def gen_employee_details(empid):
        query = db.select(model.Employee).where(model.Employee.id == empid)
        user = db.session.execute(query).scalar()
        query_for_leaves = db.select(func.count(model.Employee.id)).join(model.Leave, model.Employee.id == model.Leave.employee_id).filter(model.Employee.id == empid)
        leave = db.session.execute(query_for_leaves).scalar()
        ret = {"fname" : user.fname,
            "lname" : user.lname,
            "title" : user.designation.designation,
            "email" : user.email,
            "phone" : user.phone,
            "max_leave":user.designation.max_leaves,
            "leave" : leave,
            "id":user.id
            }
        return ret

@app.route("/employees/<int:empid>")
def employee_details(empid):
        return jsonify(gen_employee_details(empid))

@app.route("/registeremployee", methods=['POST'])
def add_employee():
     try:
        data = request.json
        email = data.get('email')
        designation = data.get('designation')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        phone = data.get('phone')
        query = db.select(model.Designation).where(model.Designation.designation==designation)
        designation = db.session.execute(query).scalar_one()
        employee = model.Employee(lname=first_name,
                                        fname=last_name,
                                        designation=designation,
                                        email=email,
                                        phone=phone)
        db.session.add(employee)
        db.session.commit()


        return jsonify({'message': 'Employee details added successfully'})
     except:
         return jsonify({'message': 'Failed to add Employee details'})

@app.route('/employees/<int:empid>', methods=['DELETE'])
def delete_employee(empid):
    try:
        query = db.select(model.Employee).where(model.Employee.id == empid)
        employee = db.session.execute(query).scalar()
        db.session.query(model.Leave).where(model.Leave.employee_id==empid).delete()
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': 'Employee deleted successfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Failed to delete employee'})



@app.route('/leaves/<int:empid>', methods=['POST'])
def add_leaves(empid):
    try:
        print(f"Received POST request to /leaves/{empid}")
        data = request.json
        date = data.get('date')
        reason = data.get('reason')
        leave = model.Leave(date=date, employee_id=empid, reason=reason)
        db.session.add(leave)
        db.session.commit()
        message = {'message': "Successfully added leave"}
        print("Leave added successfully")
        return jsonify(message)
    except:
        message = {'message':"Failed to add leave. Check and add again"}
        return jsonify(message)
    

@app.route('/register', methods=['OPTIONS','POST'])
def register():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight request successful'})
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        if not username:
            raise ValueError('Username cannot be empty')        
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = model.User(name= username, email = email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'message': 'true'})
    except Exception as e:
        return jsonify({'message': 'false'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    query = db.select(model.User).where(model.User.name == username)
    user = db.session.execute(query).scalar()

    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'true'})
    else:
        return jsonify({'message': 'false'})
    
@app.route('/vcard/<int:empid>')
def get_vcard(empid):
    user = gen_employee_details(empid)
    content = f"""BEGIN:VCARD
VERSION:2.1
N:{user['fname']};{user['fname']}
FN:{user['fname']} {user['fname']}
ORG:Authors, Inc.
TITLE:{user['title']}
TEL;WORK;VOICE:{user['phone']}
ADR;WORK:;;Hamon North21 USA
EMAIL;PREF;INTERNET:{user['email']}
REV:20150922T195243Z
END:VCARD
"""
    headers = {
        'Content-Type': 'text/vcard',
        'Content-Disposition': f'attachment; filename=employee_{empid}_vcard.vcf',
    }

    
    return Response(content, headers=headers)

    




        





