# all the import needed for the application
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug import security 
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, current_user, logout_user
from markupsafe import escape
from flask_mail import Mail, Message
from io import BytesIO
import os
from barcode import EAN13
from barcode.writer import SVGWriter
import random 
import string 

# create the Flask app
from flask import Flask, render_template, request, session, redirect
app = Flask(__name__)
mail = Mail(app)

# select the database filename
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Sets the routes to the folders where the barcodes and event images are stored
#BARCODE_FOLDER = 'static/barcode'
#app.config['BARCODE_FOLDER'] = BARCODE_FOLDER
#EVENT_FOLDER = 'static/event'
#app.config['EVENT_FOLDER'] = EVENT_FOLDER

# set up a 'model' for the data 
from db_schema import db, dbinit, User, Company, Company_tag, Company_tracked, Story, Notification

# init the database so it can connect with our app
db.init_app(app)

#Adds a random 8 letter+number code as the secret key 
characters = string.ascii_letters + string.digits
code = ''.join(random.choice(characters) for i in range(8))
app.secret_key = code


# change this to False to avoid resetting the database every time this app is restarted
resetdb = True
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()
        

#route to the index
@app.route('/', methods=['POST','GET'])
@app.route('/login.html', methods=['POST','GET'])
def login():
    
    return render_template('login.html')

#Register page
@app.route('/register.html', methods=['POST','GET'])
def register():
    
    return render_template('register.html')
  
#Companies page
@app.route('/companies.html', methods=['POST','GET'])
def company():
    
    return render_template('companies.html')

#Home page
@app.route('/index.html', methods=['POST','GET'])
def index():
    
    return render_template('index.html')



