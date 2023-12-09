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
def employees():
    query = db.select(Employee).order_by(Employee.id)
    users = db.session.execute(query).scalars()
    return flask.render_template("userlist.html", users = users)

def getdata(empid):
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

cache = {}
@app.route("/employees/<int:empid>")
def api_employee_details(empid):
    try:
        if empid in cache:
            print (f"returning {empid} from cache")
            return jsonify(cache[empid])
        else:
            ret = getdata(empid)
            cache[empid]=ret
            return jsonify(ret)
    except:
        flash('Failed to generate employee data')
        return redirect(url_for('employees'))


@app.route('/add_leaves/<int:empid>', methods=['GET', 'POST'])
def add_leaves(empid):
    ret = getdata(empid)
    try:
        if request.method == 'POST':
            date = request.form['date']
            reason = request.form['reason']

            leave = Leave(date=date,
                                    employee_id=empid,
                                    reason=reason)
            db.session.add(leave)
            db.session.commit()
            del cache[empid]
            flash('Leave added successfully for' + ret['fname'], 'success')
            return redirect(url_for('employees'))
    except:
        flash('Failed to add leave for ' + ret['fname'],'Already Taken')
        return redirect(url_for('employees'))


