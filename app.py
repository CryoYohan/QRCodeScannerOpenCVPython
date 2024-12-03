import os
import base64
from flask import Flask, render_template, redirect, url_for, request, Response,jsonify, flash, session
from dbhelper import Databasehelper
from qrmaker_v2 import QRMaker
from importlib import import_module
from flask_socketio import SocketIO, emit
from qr_scanner import QRScanner
from camera_opencv import Camera
from datetime import datetime

app = Flask(__name__)
columns = ['idno','lastname','firstname','course', 'level']
uploadfolder = 'static/images/studentimage'
table = 'studentdata'
db = Databasehelper()
admin=''
qr = QRMaker()
socketio = SocketIO(app, cors_allowed_origins="*")

app.secret_key = "@#@#@#"
app.config['UPLOAD_FOLDER']=uploadfolder

# ------------------ QR CODE SCANNER --------------------------------
qr_code_scanner = QRScanner()

def generate_frames(camera):
    while True:
        is_granted, is_denied = False, False
        image = camera.get_frame()

        result = QRScanner.read_qr_code(image)
        if len(result) == 0:
            socketio.emit(
                "scan_result",
                {"status": "scan", "message": "Please scan your QR Code"},
            ) 

        for barcode in result:
            myData = barcode.data.decode("utf-8")
            records = db.getall_records(table='studentdata')
            for data in records:
                if data['idno'] == myData:
                    socketio.emit(
                        "scan_result",
                        {"status": "granted", 
                         "message": f"Student ID : { data['idno']}",
                         "studentid": data['idno'],
                         "studentlastname": data['lastname'],
                         "studentfirstname": data['firstname'],
                         "studentcourse": data['course'],
                         "studentlevel":data['level'],
                         "image_filename": data['image'],  # Send the image filename
                        }
                    )
                    is_granted = True
                else:
                    print("Not found in the database!")
                    socketio.emit(
                        "scan_result", {"status": "denied", "message": f"Student ID : {myData}"}
                    )
                    is_denied = True
                QRScanner.add_box_to_qr_code(image, barcode)

        if is_granted:
            image = qr_code_scanner.get_access_granted_img()
            data:list = []
            records = db.getall_records(table='studentdata')
            for record in records:
                if myData == record['idno']:
                    data = record
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.add_record(table='attendancelog',idno=data['idno'],lastname=data['lastname'],firstname=data['firstname'],course=data['course'],level=data['level'],timelogged=current_datetime )
       
        elif is_denied:
            image = qr_code_scanner.get_access_denied_img()

        frame = QRScanner.encode(image)

        if is_granted or is_denied:
            for _ in range(2):
                yield (b"--frame\r\n" + b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        else:
            yield (b"--frame\r\n" + b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video")
def video():
    return Response(
        generate_frames(Camera()), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

#----------------------------------------------------------------------
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
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{idno}.jpeg")
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{idno}.png")
    try:
            # Remove the image file from static folder
            os.remove(img_path)
            os.remove(qr_path)
    except Exception as e:
        print(f"Error deleting QR code: {e}")
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
    global admin
    return render_template('studentlist.html',slist=db.getall_records(table=table),columns=columns,admin=admin,attendance_checker=False) if not session.get('name') == None else redirect(url_for('login'))

@app.route('/createqr', methods=['POST'])
def createqr():
    data = request.get_json()  # Parse JSON data from the request
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON format'}), 400
    
    idno = data.get('idno')
    if not idno:
        return jsonify({'success': False, 'error': 'ID number is required'}), 400

    # Generate the QR code
    qr_filename = f"{idno}.png"
    qr.create_qr(idno)

    # Return the QR code filename
    return jsonify({'success': True, 'qr_filename': qr_filename})

# Cancel button
@app.route('/deleteqr/<string:idno>', methods=['POST'])
def deleteqr(idno):
   return deleteqr_module(idno)



@app.route('/saveinfo', methods=['POST'])
def saveinfo():
    # Extract form data
    idno = request.form.get('my_idno')
    lastname = request.form.get('my_lastname')
    firstname = request.form.get('my_firstname')
    course = request.form.get('my_course')
    level = request.form.get('my_level')
    image_data = request.form.get('image_data')  # Base64 image data
    #qr_data = request.form.get('image_data')

    print("Form Data:", idno, lastname, firstname, course, level)


    if not idno_exist(idno):
        print(idno,lastname,firstname,course,level)
       
        # Add student info to Database
        ok:bool = db.add_record(table=table,idno=idno,lastname=lastname,firstname=firstname,course=course,level=level,image=saveimage(idno=idno,image_data=image_data))
        print(saveimage(idno=idno,image_data=image_data))
        if ok:
            flash("Student Information and Image Successfully Saved!", 'success')
        else:
            flash("Student Information and Image Failed to save", 'error')
        return redirect('studentlist')
    flash('IDNO Already Exists!', 'error')
    deleteqr(idno)
    return redirect(url_for('studentlist'))

def deleteqr_module(idno):
    # Path to the QR code file
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{idno}.png")
    
    try:
            # Remove the QR code file
            os.remove(qr_path)
            return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting QR code: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete QR code'}), 500

def saveimage(idno:str,image_data:str)->str:
    # Decode the base64 image data
    image_data = image_data.split(",")[1]  # Remove the prefix
    image_data = base64.b64decode(image_data)

    # Create the filename: e.g., '1001_Ypil.jpeg'
    filename = f"{idno}.jpeg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Save the image to the upload folder
    with open(filepath, "wb") as f:
        f.write(image_data)
    return filename

@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache,no-store,must-revalidate'
    return response 

@app.route('/logout')
def logout():
    session['name'] = None
    return redirect(url_for('attendance'))

@app.route('/registeradmin', methods=['POST'])
def registeradmin():
    username:str = request.form['username']
    password:str = request.form['password']
    db.add_record(table='admin', username=username,password=password)
    flash('Registered Sucessfully!', 'success')
    return redirect(url_for('studentlist'))

@app.route('/loginadmin', methods=['POST'])
def loginadmin():
    global admin
    username:str = request.form['username']
    admin=username
    password:str = request.form['password']
    records = db.getall_records(table='admin')
    print(records)
    print(username, password)
    for record in records:
        if record['username'] == username and record['password'] == password:
            flash(f'Welcome {username}!', 'success')
            session['name'] = username
            return redirect(url_for('studentlist'))
    else:
        flash('Invalid Credentials!', 'error')
        return redirect(url_for('login'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/granted/myData')
def grant(myData):
     return render_template('granted.html', mydata=myData) if not session.get('name') == None else render_template('login.html')

@app.route('/logs')
def logs():
    return render_template('logs.html',logs=db.getall_records(table='attendancelog'),attendance_checker=False) if not session.get('name') == None else render_template('login.html')

@app.route('/')
def attendance():
      return render_template('attendance.html',attendance_checker=True)

@app.route('/index')
def index():
    return render_template('index.html',columns=columns, attendance_checker=False) if not session.get('name') == None else render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
