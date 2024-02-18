from flask_sqlalchemy import SQLAlchemy
from werkzeug import security 

# create the database interface
db = SQLAlchemy()

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(25))

    def __init__(self, username, email, password):  
        self.username=username
        self.email=email
        self.password=password

class Company(db.Model):
    __tablename__='company'
    id = db.Column(db.Integer, primary_key=True)
    companyname = db.Column(db.String(20), unique=True)
    networth = db.Column(db.Float)
    num_emp = db.Column(db.Integer)
    stock_symb = db.Column(db.String(20),unique=True)
    ceoname = db.Column(db.String(20))


    def __init__(self,companyname,networth,num_emp,stock_symb,ceoname):  
        self.companyname=companyname
        self.networth=networth
        self.num_emp=num_emp
        self.stock_symb=stock_symb
        self.ceoname=ceoname

class Company_tracked(db.Model):
    __tablename__='company_tracked'
    userid = db.Column(db.Integer,primary_key=True)
    companyname = db.Column(db.String(20),primary_key=True)

    def __init__(self,userid,companyname):  
        self.userid=userid
        self.companyname=companyname
        
class Company_tag(db.Model):
    __tablename__='company_tags'
    companyname = db.Column(db.String(20),primary_key=True)
    tag = db.Column(db.String(20),primary_key=True)

    def __init__(self,companyname,tag):  
        self.companyname=companyname
        self.tag=tag
    
class Story(db.Model):
    __tablename__='stories'
    id = db.Column(db.Integer,primary_key=True)
    storyid = db.Column(db.Integer,primary_key=True)

    def __init__(self,userid,storyid):  
        self.userid=userid
        self.storyid=storyid

class Notification(db.Model):
    __tablename__='notifications'
    id = db.Column(db.Integer, primary_key=True)
    companyname = db.Column(db.String(20))
    url = db.Column(db.String(50))
    #Not sure how date time will be stored
    timestamp = db.Column(db.Text)
    impact = db.Column(db.Integer)

    def __init__(self,companyname,url,timestamp,impact):  
        self.companyname=companyname
        self.url=url
        self.timestamp=timestamp
        self.impact=impact

#Add data to database
def dbinit():
    all_companies = [
        Company("Apple",2.89,161000,"AAPL","Tim Cook")

    ]

    db.session.add_all(all_companies)

    hashed_password = security.generate_password_hash("123")
    db.session.add(User("Test","jiaboj08@gmail.com",hashed_password))

    # commit all the changes to the database file
    db.session.commit()
