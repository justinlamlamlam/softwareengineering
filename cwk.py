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
from datetime import datetime
#import numpy
from jinja2 import Template
from datetime import datetime
import math

import webScraper
import stock

# create the Flask app
from flask import Flask, render_template, request, session, redirect
app = Flask(__name__)
mail = Mail(app)

# select the database filename
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set up a 'model' for the data 
from db_schema import db, dbinit, User, Company, Company_tag, Company_tracked, Story, Notification

# init the database so it can connect with our app
db.init_app(app)

#Adds a random 8 letter+number code as the secret key 
characters = string.ascii_letters + string.digits
code = ''.join(random.choice(characters) for i in range(8))
app.secret_key = code


# change this to False to avoid resetting the database every time this app is restarted
resetdb = False
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

        #webScraper.webScraper() #won't be called here in final version but not sure where yet

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
            return render_template("login.html",message="Incorrect password")

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
            return render_template('register.html',message="Invalid Email or Username/Email already associated with an account")
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
            
            return render_template('register.html',message="Verification code incorrect")

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

    companies_raw = Company.query.all()
    companies = []
    company_recommendation = []

    tracked_companies = Company_tracked.query.filter_by(userid = session['id'])
    tracked = []
    for i in tracked_companies:
        tracked.append(i.companyname)
    
    company_recommendation.append(0)
    for i in companies_raw:
        companies.append(i)
        company_recommendation.append(recommendation(i.companyname))
    
    print(company_recommendation)
    notices = notification()
    
    return render_template('companies.html',companies=companies,tracked=tracked,notices=notices,company_recommendation=company_recommendation)

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
    stories_sorted = []

    for i in stories:
        stories_sorted.append(i)
    
    stories_sorted.sort(key=sort_story_bydate,reverse=True)

    if request.method != "POST":
        stories_sorted = stories_sorted[:5]
    
    seemore = True
    if request.method == "POST":
        seemore = False

    notices = notification()
    reputation = current_reputation(company.companyname)

    today_date = datetime.today().strftime('%Y-%m-%d')
    fig = stock.get_stock_fig(company.stock_symb, specific_dates_range=("2024-01-01", today_date), stories=stories)

    return render_template('company.html',company=company,tracked=tracked,stories=stories_sorted,notices=notices, reputation=reputation,fig=fig.to_html(full_html=False),seemore=seemore)

#Home page
@app.route('/home.html', methods=['POST','GET'])
def home():
    
    notices = notification()
    companies_tracked = Company_tracked.query.filter_by(userid = session['id'])
    tracked = []

    stories = []

    for i in companies_tracked:

        temp = Company.query.filter_by(companyname=i.companyname).first()
        tracked.append(temp)
        story = Story.query.filter_by(companyname=i.companyname)
        for entry in story:
            stories.append(entry)

    stories.sort(key=sort_story_bydate,reverse=True)
    
    stories = stories[:5]

    companies = Company.query.all()
    companylist = []
    untrackedcompanies = []

    for i in companies:
        companylist.append(i)
    
    
    for element in companylist:
        if element not in tracked:
            untrackedcompanies.append(element.companyname)
    
    untrackedcompanies.sort(key=recommendation,reverse=True)
    recommendedcompanies = []

    for i in range (3):

        temp = Company.query.filter_by(companyname=untrackedcompanies[i]).first()
        recommendedcompanies.append(temp)
    


    return render_template('home.html',notices=notices,stories=stories,recommendedcompanies=recommendedcompanies)

#Function to help sort story by date
def sort_story_bydate(story):

    date = datetime.strptime(story.timestamp, '%Y-%m-%d')

    return date

#When tracking a company
@app.route('/trackcompany.html', methods=['POST','GET'])
def trackcompany():
    companyname = request.values.get('companyname')

    db.session.add(Company_tracked(session['id'],companyname))
    db.session.commit()

    if request.method == 'GET':
        company_id = request.values.get('companyid')
        
        return company(company_id)

    else:
        return companies()

#When untracking a company
@app.route('/untrackcompany.html', methods=['POST','GET'])
def untrackcompany():
    companyname = request.values.get('companyname')
    query = Company_tracked.query.filter_by(userid = session['id'],companyname = companyname).first()

    db.session.delete(query)
    db.session.commit()

    if request.method == 'GET':
        company_id = request.values.get('companyid')
        
        return company(company_id)

    else:
        return companies()

#Function to retrieve all notifications from database
def notification():

    notifications = Notification.query.filter_by(userid = session['id'])
    notices = []
    
    for entry in notifications:
        story = Story.query.filter_by(id = entry.storyid).first()
        companyname = story.companyname
        impact = story.impact
        date = datetime.strptime(story.timestamp, '%Y-%m-%d')
        if date.day == datetime.now().day:
            time = "Today"
        else:
            time = str(datetime.now() - date)
            time = time[:time.find(",")] + " ago"


        notice = "There is a new story about " + companyname + " with an impact of " + str(impact) + " (" + time + ")"
        notices.append(notice)
    
    return notices

#Function to get current public opinion on company
def current_reputation(companyname):

    stories = Story.query.filter_by(companyname=companyname)
    reputation = 0
    #lamba is the rate of decay, the higher the faster, meaning new stories will have higher impact on reputation
    lambda_value = 0.01
    counter = 0


    for i in stories:
        date = datetime.strptime(i.timestamp, '%Y-%m-%d')
        days_ago = (datetime.now() - date).days

        #Exponential decay function to take in the factor of how recent the stories are
        reputation = reputation + (i.impact * math.exp(-lambda_value * days_ago))
        counter+=1
    
    reputation = reputation/counter
    reputation = round(reputation,2)


    return reputation

#Recommendation function
def recommendation(companyname1):
    track_company=Company_tracked.query.filter_by(userid=session["id"])
    tracked=[]
    storytimestamp = []
    x=0

    tag1= Company_tag.query.filter_by(companyname=companyname1)

    for i in track_company:
        tracked.append(i.companyname)
    for i in range (len(tracked)):
        tag = Company_tag.query.filter_by(companyname=tracked[i])

        for k in tag1:
            for j in tag:
                if k.tag == j.tag:
                    x=x+1

    story = Story.query.filter_by(companyname=companyname1)
    for i in story:
        storytimestamp.append(i)

    storytimestamp.sort(key=sort_story_bydate,reverse=True)
    if len(storytimestamp)< 5:
        y=365
    else:
        today=datetime.now()
        storytimestamp5th=storytimestamp[4].timestamp
        date = datetime.strptime(storytimestamp5th, '%Y-%m-%d')
        y=(today-date).days

    z=current_reputation(companyname1)

    '''
    a = 2
    b = 1.2
    c = 0.5
    d = 2
    e = 0.5
    f = 2

    B=math.log(y,d)
    z=abs(z)

    C=math.log(z,f)
    S=(a*(b**x))+(c/B)+(e/C)

    return S'''

    a=0.6
    b=2
    c=5
    d=2
    e=1
    f=3
    B=math.log(y,d)
    F=(a*(b**x))
    G=(c/B)
    E=(e/c)
    if z < -0.8 or z > 0.8:
        E=5
    if y==1:
        G=5
    if z < 0:
        z=abs(z)
        S=F+G+E
    else :
        S=F+G-E

    return S
