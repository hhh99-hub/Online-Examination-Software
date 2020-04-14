from flask import * # flask module that includes the flask requirements needed
import pyrebase # pyrebase is a module that interacts with the Firebase API to parse commands and queries to Firebase
import json # JSON module to perform translation to/from JSON, since we're dealing with JavaScript Objects also

# The config data structure that holds the Firebase configuration
config = {
    "apiKey": "AIzaSyANNhQ9l-Ptm0ICI4EWxsCW84q52xo_AeE",
    "authDomain": "full-marks-7f03b.firebaseapp.com",
    "databaseURL": "https://full-marks-7f03b.firebaseio.com",
    "projectId": "full-marks-7f03b",
    "storageBucket": "full-marks-7f03b.appspot.com",
    "messagingSenderId": "586975054480",
    "appId": "1:586975054480:web:dbf2bcf6d919940ca5e615",
    "measurementId": "G-30ZTMVX2HF"
}

# pyrebase includes buiilt in functions to work with the firebase API, so most of the heavy work is done for us.

# Initalising the firebase app to use services
firebase = pyrebase.initialize_app(config)

# Initialising the different cloud services within firebase
storage = firebase.storage() # Storage bucket for storing files other than normal text, such as images, videos, etc
db = firebase.database() # Real Time database for storing data. Real Time so firebase updates as you push data, no need to refresh database webpage if being viewed
auth = firebase.auth() # Authentication service, provides authentication for different users of the application, and also handling creating/logging in new users with email/password
# role = None
# uid = None
# session = ''
# termsAccepted = None
app = Flask(__name__)
app.secret_key = 'a'

'''
''@app.route'' is an app decorator used to manage the flow of website. Inside the arguments is the custom 'url' that you can create, with '/' being the index route. 
Call the arguments if you are calling from outside of the app.py file, such as within JavaScript, or when you are using the ''redirect'' function which directs to a
url. The url is now the arguments within the ''@app.route'' function. This is also known as the ''route'' of the webpage

The function below the route is the ''view'' of the webpage. It is the content that is going to be served. Flask uses view functions to control what is going to served
to the webpage, which is why all commands are wrapped in functions. The first view function below the route is the view function linked to that route, so you could
easily have 2 or more routes above the view function, one after the other, to link to that specific view function
'''

# The route that is loaded up when first coming to the website.
@app.route('/')
def home():
    print("Hello")
    if not session.get('logged in'):
        return redirect(url_for('login'))
    elif session.get('logged in') and session.get('role') == "admin":
        return redirect(url_for('AdminDashboard'))
    elif session.get('logged in') and session.get('role') == "examiner":
        return redirect(url_for('examiner'))
    elif session.get('logged in') and session.get('role') == "tech":
        return render_template('tech')
    else:
        return render_template('student')
    return redirect(url_for('login'))

# login_register.html
@app.route('/login')
def login():
    return render_template('login_register.html')

# You can parse over form data directly by including the 'methods' argument, followed by the form methods being used
# If you choose register within the above page, the below ''sub route'' will be called, handling that data passed.
@app.route('/login/handleRegistrationData', methods=['POST'])
def handleRegistrationData():
    req = request.get_json() # Since we know that data is being sent as JSON, we need to convert it to a data structure that python understands, which is dictionaries
    try:
        user = createUser(req['email'], req['password'], req['SID'], 'student')
    except Exception as e: # pyrebase unfortunately does not include error handling, but we can take advantage of the exception that is thrown and store the error object that Firebase throws back
        print(e)
        try:
            error = json.loads(str(e)[str(e).index(']')+2:]) # If the error is a Firebase error, it throws back a specfic 'JSON' object, so we need to translate it to JSON for JavaScript
        except Exception as e: # Else, it could be any other Error, so we need to capture it and handle it
            print(e)
            return make_response({"message": str(e)}, 500)
        return make_response(error, 511)
    return make_response({"success" : True}, 200)

# If you choose login within the login page, the below ''sub route'' will be called, handling that data passed. 
@app.route('/login/handleLoginData', methods=['POST'])
def handleLoginData():
    # if request.form['password'] == link to db here and request.form['email'] == link to db here:
        # uid = db.child('users').child(student['userId']).child('UID').get().val()
        # role = db.child('users').child(student['userId']).child('UID').get().val()
    #     if role == "student":
    #         termsAccepted = False
    #     session['logged in'] = True
    # else:
    #     flash('Incorrect Password and Email Combination')
    # return home()
    req = request.get_json()
    try:
        user = signIn(req['email'], req['password'])
    #     if role == "student":
    #         termsAccepted = False
    #     session['logged in'] = True
    except Exception as e:
        print(e)
        try:
            error = json.loads(str(e)[str(e).index(']')+2:])
        except Exception as e: 
            print(e)
            return make_reponse({"message": str(e)}, 500)
        return make_response(error, 511)
    return make_response({"success" : True}, 200)

# ImageCapture.html
@app.route('/ImageCapture')
def imageCapture():
    return render_template('ImageCapture.html')

# index.html
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# personalDetails.html
@app.route('/personalDetails')
def personalDetails():
    return render_template('personalDetails.html')

# button.html
@app.route('/button')
def button():
    return render_template('button.html')

# ExaminerLogin.html
@app.route('/ExaminerLogin')
def ExaminerLogin():
    return render_template('ExaminerLogin.html')

# # admin.html
# @app.route('/admin', methods=['POST'])
# def admin():
#     if not session.get('logged in') or session.get('role') != 'admin':
#         return redirect(url_for('home'))
#     return render_template('admin.html')

# admin.html
@app.route('/admin', methods=['POST','GET'])
def admin():
    if not session.get('logged in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
    elif request.method == 'POST':
        req = request.get_json()
        user = createUser(req['email'], req['password'], req['userRole'], req['userRole'])
        return redirect(url_for('AdminDashboard'))
    return render_template('admin.html')

@app.route('/AdminDashboard')
def AdminDashboard():
    if not session.get('logged in') or session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('AdminDashboard.html')

# # admin.html with adding users
# @app.route('/admin/create-user', methods=['GET', 'POST'])
# def adminCreateUser():
#     if request.method == 'POST' or request.method == 'GET':
#         req = request.get_json()
#         user = createUser(req['email'], req['password'], 'Please enter your user ID', req['userRole'])
#         auth.current_user = None
#         return redirect(url_for('AdminDashboard'))

# examiner.html
@app.route('/examiner')
def examiner():
    return render_template('examiner.html')

# exams.html
@app.route('/exams')
def exams():
    return render_template('exams.html')

# exams2.html
@app.route('/exams2')
def exams2():
    return render_template('exams2.html')

# quiz.html
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# timetable.html
@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

# createExam.html
@app.route('/createExam', methods=['POST', 'GET'])
def createExam():
    if request.method == 'POST':
        try:
            req = request.get_json()
            db.child('exams').child(req['examCode']).set({
                'examName': req['examName']
            })
            questions = req['questions']
            i = 1
            for question in questions:
                db.child('exams').child(req['examCode']).child('q'+str(i)).set({'question' : question['question']})
                if 'answer' in question.keys():
                    db.child('exams').child(req['examCode']).child('q'+str(i)).set({
                        'answer' : int(question['answer']),
                        'mcqAnswers' : question['mcqAnswers']
                    })
                i+=1
        except Exception as e:
            print(e)
            try:
                error = json.loads(str(e)[str(e).index(']')+2:])
            except Exception as e:
                print(e)
                return make_response({'message': 'Unknown error has occurred'}, 500)
            return make_response(error, 500)
        return make_response({'success': True}, 200)
    return render_template('createExam.html')

# Helper method to create a student account
def createUser(email, password, uid, userRole):
    auth.create_user_with_email_and_password(email, password)
    user = signIn(email, password)
    db.child('users').child(user['userId']).set({
        'UID': uid,
        'userRole': userRole
    })
    return user

# Helper method to sign in a student
def signIn(email, password):
    user = auth.sign_in_with_email_and_password(email, password)
    user = auth.refresh(user['refreshToken'])
    print(user['userId'])
    session['uid'] = db.child('users').child(user['userId']).child('UID').get().val()
    session['role'] = db.child('users').child(user['userId']).child('userRole').get().val()
    session['logged in'] = True
    return user

# Run the application and start it in debugging mode to display errors
if __name__=="__main__":
    app.run(debug=True)

# Destroy current session
@app.route("/logout", methods=['GET'])
def logout():
    session['logged in'] = False
    session.pop('role', None)
    session.pop('uid', None)
    return redirect(url_for('home')) 