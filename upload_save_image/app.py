from flask import Flask,render_template,request,redirect,url_for
from dbhelper import *

app = Flask(__name__)

@app.route("/savestudent",methods=['POST'])
def savestudent()->None:
    idno:str = request.form['idno']
    lastname:str = request.form['lastname']
    firstname:str = request.form['firstname']
    course:str = request.form['course']
    level:str = request.form['level']
    ok:bool = savestudent('students',idno=idno,lastname=lastname,firstname=firstname,course=course,level=level)
    return redirect("/")


@app.route("/")
def index()->None:
    data:list = getall_records('students')
    return render_template("index.html",students=data,pagetitle="student registration")
    
if __name__=="__main__":
    app.run(debug=True)
