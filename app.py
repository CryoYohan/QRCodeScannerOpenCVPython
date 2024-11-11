from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
columns = ['idno','full name','course', 'level']


@app.route('/saveinfo', methods=['POST'])
def saveinfo():
    idno:str = request.form['my_idno']
    fullname:str = request.form['my_fullname']
    course:str = request.form['my_course']
    level:str = request.form['my_level']
    print(idno,fullname, course,level)
    return redirect(url_for('index'))
    

@app.route('/')
def index():
    return render_template('index.html',columns=columns)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
