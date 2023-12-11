import flask
from flask import jsonify, redirect,request,render_template, url_for
import psycopg2
import db as model
from sqlalchemy.sql import func

app = flask.Flask("hrms")
db = model.SQLAlchemy(model_class=model.HRDBBase)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/employees")
def employees_list():
    query = db.select(model.Employee).order_by(model.Employee.fname)
    users = db.session.execute(query).scalars()
    return flask.render_template("userlist.html", users = users)

@app.route("/ids")
def get_empid():
    query = db.select(model.Employee.id).order_by(model.Employee.fname)
    ids = db.session.execute(query).fetchall()
    ids = [{'id':id} for id, in ids]
    return jsonify(ids)

def get_employees(empid):
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
    try:
        return jsonify(get_employees(empid))
    except Exception as e:
        return redirect(url_for('employees_list'))


@app.route('/leaves/<int:empid>', methods=['POST'])
def add_leaves(empid):
    try:
        date = request.form['date']
        reason = request.form['reason']
        leave = model.Leave(date=date, employee_id=empid, reason=reason)
        db.session.add(leave)
        db.session.commit()
        message = {'message': "Successfully added leave"}
        return jsonify(message), 200
    
    except:
        message = {'message': "Failed to add leave check and add again"}
        return jsonify(message), 500
        





