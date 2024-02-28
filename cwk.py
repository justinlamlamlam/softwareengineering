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
#import numpy

import analysis

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    if request.method == 'POST':

        #webScraper() #won't be called here in final version but not sure where yet

        #Gets all info from the form 
        username = request.values.get('username')
        user_password = request.values.get('user_password')
        #gets the user based on the username entered 
        user = User.query.filter_by(username=username).first()
        #If user doesnt exist 
        if user is None:
            return render_template('login.html',message="Username does not exist")
        #Checks the password in a secure way 
        if not security.check_password_hash(user.password, user_password):
            return render_template("login.html",message="Password Incorrect")

        #Sets all the session keys 
        session['id'] = user.id 
        session['username'] = user.username
        
        return home()

    else:
        return render_template('login.html')


#Register page
@app.route('/register.html', methods=['POST','GET'])
def register():
    
    if request.method == 'POST':
        username = request.values.get('username') #gets the username from the form
        user_password = request.values.get('user_password') #gets the password from the form
        confirm_password = request.values.get('confirm_password') #gets the confirm pwd from the form
        hashed = security.generate_password_hash(user_password) #hashes the password
        user_email = request.values.get('user_email') #gets the email from the form


        if confirm_password != user_password: #if the confirm password is different to the password 
            return render_template('register.html',message="Passwords do not match")
        
        db.session.add(User(username,user_email,hashed))

        try:
            db.session.commit()
            #Generates a 8 digit random code which combines numbers and letters
            characters = string.ascii_letters + string.digits
            code = ''.join(random.choice(characters) for i in range(8))
            #This is the message which will be sent to an email
            msg = Message("Verify Your Email",
                  sender=("MarketMood","u2200657@live.warwick.ac.uk"),
                  body=("Here is the code: " + code),
                  #recipients=['u2200657@live.warwick.ac.uk'])
                  recipients=[user_email]) #This would be the actual code
            mail.send(msg) #sends the mail 
            session['code'] = code #sets the session code to be code
            return render_template('verify.html',message='',username=username,user_password=user_password)

        except:
            return render_template('register.html',message="Username/Email already used")
    else:
        return render_template('register.html')
  
#route to the verify page
@app.route('/verify.html',methods=['POST','GET'])
def verify():
    if request.method == 'POST':
        #Gets all the info from the form 
        username = request.values.get('username')
        user_password = request.values.get('user_password')
        code = request.values.get('code')

        #Checks to see if the code entered is the same as the verification code
        if code == session['code']:
            #If correct then log in the user 
            return login()
        else:
            #Redirects the user back to register page, and deletes the info from the database
            users = User.query.filter_by(username=username).first()
            userid = users.id
            user = User.query.get(userid)
            db.session.delete(user)
            db.session.commit()
            
            return render_template('register.html',message="Verification Code Incorrect")

@app.route('/logout.html')
def logout():
    #Removes the id from session 
    session.pop('id',None)
    session.pop('username',None)
    session.pop('code',None)
    return login()

#Companies page
@app.route('/companies.html', methods=['POST','GET'])
def companies():

    companies = Company.query.all()
    tracked_companies = Company_tracked.query.filter_by(userid = session['id'])
    tracked = []
    for i in tracked_companies:
        tracked.append(i.companyname)
    
    notices = notification()
    
    return render_template('companies.html',companies=companies,tracked=tracked,notices=notices)

#Individual companies page
@app.route('/company<company_id>.html',methods=['POST','GET'])
def company(company_id):

    #Gets company from the company id 
    company = Company.query.filter_by(id = company_id).first()

    tracked_companies = Company_tracked.query.filter_by(userid = session['id'])
    tracked = []
    for i in tracked_companies:
        tracked.append(i.companyname)
    
    stories = Story.query.filter_by(companyname=company.companyname)
    notices = notification()

    return render_template('company.html',company=company,tracked=tracked,stories=stories,notices=notices)

#Home page
@app.route('/home.html', methods=['POST','GET'])
def home():
    
    notices = notification()

    return render_template('home.html',notices=notices)

def webScraper():

    driver = webdriver.Firefox()
    companies = Company.query.all()
    for company in companies:
        driver.minimize_window()
        url = "https://www.google.co.uk"
        driver.get(url)
        if driver.find_elements(By.ID,'L2AGLb'):
            driver.find_element(By.ID,'L2AGLb').click()
        search_input = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.NAME,"q")))
        search_input.send_keys(company.companyname)
        search_input.send_keys(Keys.RETURN)
        search_input = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.LINK_TEXT,"News")))
        driver.find_element(By.LINK_TEXT,'News').click()
        results = driver.find_elements(By.CLASS_NAME,'WlydOe')

        times = driver.find_elements(By.XPATH,"//div[@class='OSrXXb rbYSKb LfVVr']")

        companyStories = Story.query.filter_by(companyname=company.companyname)

        for result,time in zip(results,times):
            link = result.get_attribute('href')
            headline = app.logger.info(result.text.split('\n')[1])
            inDB = 0
            for c in companyStories:
                if c.url == link:
                    app.logger.info("article already in database") 
                    inDB = 1
                #if text_similarity(c.headline,headline) < 0.5:
                #   app.logger.info("same story already in database")
                #   inDB = 1
            #if inDB == 0:
                #app.logger.info("can add to db")
                #do stuff....

                #story = Story(company.companyName,link,headline,time.text,analysis(headline))
                #db.session.add(story)

    db.session.commit()
    driver.close()

#When tracking a company
@app.route('/trackcompany.html', methods=['POST','GET'])
def trackcompany():
    companyname = request.values.get('companyname')

    db.session.add(Company_tracked(session['id'],companyname))
    db.session.commit()

    companies = Company.query.all()
    tracked_companies = Company_tracked.query.filter_by(userid = session['id'])
    tracked = []
    for i in tracked_companies:
        tracked.append(i.companyname)
    
    notices = notification()

    if request.method == 'GET':
        company_id = request.values.get('companyid')
        company = Company.query.filter_by(id = company_id).first()
        stories = Story.query.filter_by(companyname=company.companyname)
        return render_template('company.html',company=company,tracked=tracked,stories=stories,notices=notices)
    else:
        return render_template('companies.html',companies=companies,tracked=tracked,notices=notices)

#When untracking a company
@app.route('/untrackcompany.html', methods=['POST','GET'])
def untrackcompany():
    companyname = request.values.get('companyname')
    query = Company_tracked.query.filter_by(userid = session['id'],companyname = companyname).first()

    db.session.delete(query)
    db.session.commit()

    companies = Company.query.all()
    tracked_companies = Company_tracked.query.filter_by(userid = session['id'])
    tracked = []
    for i in tracked_companies:
        tracked.append(i.companyname)

    notices = notification()
    
    if request.method == 'GET':
        company_id = request.values.get('companyid')
        company = Company.query.filter_by(id = company_id).first()
        stories = Story.query.filter_by(companyname=company.companyname)
        return render_template('company.html',company=company,tracked=tracked,stories=stories,notices=notices)
    else:
        return render_template('companies.html',companies=companies,tracked=tracked,notices=notices)

def notification():

    notifications = Notification.query.filter_by(userid = session['id'])
    notices = []
    
    for entry in notifications:
        story = Story.query.filter_by(id = entry.storyid).first()
        companyname = story.companyname
        impact = story.impact
        time = story.timestamp

        notice = "There is a new story about " + companyname + " with an impact of " + str(impact) + " (" + time + ")"
        notices.append(notice)
    
    return notices
