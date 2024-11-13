import os
import base64
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash

app = Flask(__name__)
columns = ['idno','full name','course', 'level']

app.secret_key = "@#@#@#"

# Define the static folder path
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/saveinfo', methods=['POST'])
def saveinfo():
    # Retrieve image data from form
    # Process other form fields as needed
    idno:str = request.form.get('my_idno')
    fullname:str = request.form.get('my_fullname')
    course:str = request.form.get('my_course')
    level:str = request.form.get('my_level')
    image_data = request.form.get('image_data')

    # Check if image data is present
    if image_data:
        # Remove the data:image/jpeg;base64, prefix
        image_data = image_data.split(",")[1]
        
        # Decode the base64 data
        image_bytes = base64.b64decode(image_data)
        
        # Save the image to the 'static/images' folder
        image_path = os.path.join('static/images', f'{idno}.jpg')
        with open(image_path, 'wb') as image_file:
            image_file.write(image_bytes)
    
    
    print(f"ID: {idno}, Name: {fullname}, Course: {course}, Level: {level}")
    
    flash('Student Information Successfully Saved!')
    return redirect(url_for('/'))
    

@app.route('/')
def index():
    return render_template('index.html',columns=columns)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
