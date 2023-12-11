import flask
from flask import jsonify, redirect,request,render_template, url_for ,flash
from db import *
from sqlalchemy.sql import func

app = flask.Flask("hrms")
app.secret_key = 'hrms'
db = SQLAlchemy(model_class=HRDBBase)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/employees")
def employees_list():
    query = db.select(Employee).order_by(Employee.fname)
    users = db.session.execute(query).scalars()
    return flask.render_template("userlist.html", users = users)

@app.route("/ids")
def get_empid():
    query = db.select(Employee.id).order_by(Employee.fname)
    ids = db.session.execute(query).fetchall()
    ids = [{'id':id} for id, in ids]
    return jsonify(ids)

def get_employees(empid):
        query = db.select(Employee).where(Employee.id == empid)
        user = db.session.execute(query).scalar()
        query_for_leaves = db.select(func.count(Employee.id)).join(Leave, Employee.id == Leave.employee_id).filter(Employee.id == empid)
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
    except:
        flash('Failed to generate employee data')
        return redirect(url_for('employees_list'))


@app.route('/add_leaves/<int:empid>', methods=['GET', 'POST'])
def add_leaves(empid):
    ret = get_employees(empid)
    try:
        if request.method == 'POST':
            date = request.form['date']
            reason = request.form['reason']

            leave = Leave(date=date,
                                    employee_id=empid,
                                    reason=reason)
            db.session.add(leave)
            db.session.commit()
            flash('Leave added successfully for' + ret['fname'], 'success')
            return redirect(url_for('employees_list'))
    except:
        flash('Failed to add leave for ' + ret['fname'],'Already Taken')
        return redirect(url_for('employees_list'))


