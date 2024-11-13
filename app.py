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



def idno_exist(idno:str):
    records:list = db.getall_records(table=table)
    for student in records:
        if student['idno'] == idno:
            return True
    return False

@app.route('/studentlist')
def studentlist():
    return render_template('studentlist.html',slist=db.getall_records(table=table))

@app.route('/saveinfo', methods=['POST'])
def saveinfo():
    # Extract form data
    idno = request.form.get('my_idno')
    lastname = request.form.get('my_lastname')
    firstname = request.form.get('my_firstname')
    course = request.form.get('my_course')
    level = request.form.get('my_level')
    image_data = request.form.get('image_data')  # Base64 image data

    if not idno_exist(idno):
        print(idno,lastname,firstname,course,level)

        # Decode the base64 image data
        image_data = image_data.split(",")[1]  # Remove the prefix
        image_data = base64.b64decode(image_data)

        # Create the filename: e.g., '1001_Ypil.jpeg'
        filename = f"{idno}_{lastname}.jpeg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the image to the upload folder
        with open(filepath, "wb") as f:
            f.write(image_data)

        # Add student info to Database
        ok:bool = db.add_record(table=table,idno=idno,lastname=lastname,firstname=firstname,course=course,level=level,image=filename)
        if ok:
            flash("Student Information and Image Successfully Saved!", 'success')
        else:
            flash("Student Information and Image Failed to save", 'error')
        return redirect('/')
    flash('IDNO Already Exists!', 'error')
    return redirect(url_for('index'))
    

@app.route('/')
def index():
    return render_template('index.html',columns=columns)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
