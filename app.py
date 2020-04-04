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

app = Flask(__name__)

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
def index():
    return render_template('index.html')

# The login route when redirected to the login and regsitration page.
@app.route('/login')
def login():
    return render_template('login_register.html')

# You can parse over form data directly by including the 'methods' argument, followed by the form methods being used
# If you choose register within the above page, the below ''sub route'' will be called, handling that data passed.
@app.route('/login/handleRegistrationData', methods=['POST'])
def handleRegistrationData():
    req = request.get_json() # Since we know that data is being sent as JSON, we need to convert it to a data structure that python understands, which is dictionaries
    try:
        auth.create_user_with_email_and_password(req['email'], req['password'])
    except Exception as e: # pyrebase unfortunately does not include error handling, but we can take advantage of the exception that is thrown and store the error object that Firebase throws back
        try:
            error = json.loads(str(e)[str(e).index(']')+2:]) # If the error is a Firebase error, it throws back a specfic 'JSON' object, so we need to translate it to JSON for JavaScript
        except Exception as e: # Else, it could be any other Error, so we need to capture it and handle it
            print(e)
            return make_reponse({"message": "Unknown error occured"})
        return make_response(error, 500)
    return make_response(jsonify({"message": "Registration Successful"}), 200)


# If you choose login within the login page, the below ''sub route'' will be called, handling that data passed. 
@app.route('/login/handleLoginData', methods=['POST'])
def handlLoginData():
    req = request.get_json()
    try:
        auth.sign_in_with_email_and_password(req['email'], req['password'])
    except Exception as e:
        error = json.loads(str(e)[str(e).index(']')+2:])
        return make_response(error, error.args)
    return make_response(jsonify({"message": "Login successful"}), 200)

# Handling for the 'Image Capture' webpage
@app.route('/ImageCapture')
def imageCapture():
    return render_template('ImageCapture.html')

# Run the application and start it in debugging mode to display errors
if __name__=="__main__":
    app.run(debug=True)