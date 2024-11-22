import os
import base64
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from dbhelper import Databasehelper

app = Flask(__name__)
columns = ['idno','lastname','firstname','course', 'level']
uploadfolder = 'static/images/studentimage'
table = 'studentdata'
db = Databasehelper()

app.secret_key = "@#@#@#"
app.config['UPLOAD_FOLDER']=uploadfolder

@app.route('/updatestudent/<idno>', methods=['POST'])
def updatestudent(idno):
    lastname:str = request.form['lastname']
    firstname:str = request.form['firstname']
    course:str = request.form['course']
    level:str = request.form['level']
    db.update_record(table=table, idno=idno,lastname=lastname,firstname=firstname, course=course, level=level)
    flash('Student Successfully Updated!')
    return redirect(url_for('studentlist'))

@app.route('/deletestudent/<idno>')
def deletestudent(idno):
    db.delete_record(table=table, idno=idno)
    flash('Student Successfully Deleted!', 'success')
    return redirect(url_for('studentlist'))

def idno_exist(idno:str):
    records:list = db.getall_records(table=table)
    for student in records:
        if student['idno'] == idno:
            return True
    return False

@app.route('/studentlist')
def studentlist():
    return render_template('studentlist.html',slist=db.getall_records(table=table),columns=columns)

@app.route('/saveinfo', methods=['POST'])
def saveinfo():
    # Extract form data
    idno = request.form.get('my_idno')
    lastname = request.form.get('my_lastname')
    firstname = request.form.get('my_firstname')
    course = request.form.get('my_course')
    level = request.form.get('my_level')
    image_data = request.form.get('image_data')  # Base64 image data

    print("Form Data:", idno, lastname, firstname, course, level)


    if not idno_exist(idno):
        print(idno,lastname,firstname,course,level)
       
        # Add student info to Database
        ok:bool = db.add_record(table=table,idno=idno,lastname=lastname,firstname=firstname,course=course,level=level,image=saveimage(idno=idno,lastname=lastname,image_data=image_data))
        print(saveimage(idno=idno,lastname=lastname,image_data=image_data))
        if ok:
            flash("Student Information and Image Successfully Saved!", 'success')
        else:
            flash("Student Information and Image Failed to save", 'error')
        return redirect('/')
    flash('IDNO Already Exists!', 'error')
    return redirect(url_for('index'))


def saveimage(idno:str,lastname:str,image_data:str)->str:
    # Decode the base64 image data
    image_data = image_data.split(",")[1]  # Remove the prefix
    image_data = base64.b64decode(image_data)

    # Create the filename: e.g., '1001_Ypil.jpeg'
    filename = f"{idno}_{lastname}.jpeg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Save the image to the upload folder
    with open(filepath, "wb") as f:
        f.write(image_data)
    return filename



@app.route('/')
def index():
    return render_template('index.html',columns=columns)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
