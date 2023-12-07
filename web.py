import flask
from flask import jsonify, redirect,request,render_template, url_for
from db import *
from sqlalchemy.sql import func

app = flask.Flask("hrms")
db = SQLAlchemy(model_class=HRDBBase)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/employees")
def employees():
    query = db.select(Employee).order_by(Employee.fname)
    users = db.session.execute(query).scalars()
    return flask.render_template("userlist.html", users = users)


@app.route("/employees/<int:empid>")
def api_employee_details(empid):
    query = db.select(Employee).where(Employee.id == empid)
    user = db.session.execute(query).scalar()
    query_for_leaves = db.select(func.count(Employee.id)).join(Leave, Employee.id == Leave.employee_id).filter(Employee.id == empid)
    leave = db.session.execute(query_for_leaves).scalar()
    ids_q = db.select(Employee.id).order_by(Employee.id)
    ids = db.session.execute(ids_q).fetchall()
    ids = [id for id, in ids]
    first_id = ids[0]
    last_id = ids[len(ids)-1]
    dates_q = db.select(Leave.date).where(Leave.employee_id == empid)
    dates = db.session.execute(dates_q).fetchall()
    dates = [date for date, in dates]
    ret = {"fname" : user.fname,
           "lname" : user.lname,
           "title" : user.designation.designation,
           "email" : user.email,
           "phone" : user.phone,
           "max_leave":user.designation.max_leaves,
           "leave" : leave,
           "first_id":first_id,
           "last_id":last_id,
           "id":user.id
           }

    return jsonify(ret)


@app.route('/add_leaves/<int:empid>', methods=['GET', 'POST'])
def add_leaves(empid):
    query_for_employee = db.select(Employee).where(Employee.id == empid)
    user = db.session.execute(query_for_employee).scalar()
    if request.method == 'POST':
            date = request.form['date']
            reason = request.form['reason']

            leave = Leave(date=date,
                                    employee_id=empid,
                                    reason=reason)
            db.session.add(leave)
            db.session.commit()
            return redirect(url_for('employee_details', empid=empid))
 

