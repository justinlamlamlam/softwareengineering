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
    
class Notification(db.Model):
    __tablename__='notification'
    userid = db.Column(db.Integer,primary_key=True)
    storyid = db.Column(db.Integer,primary_key=True)

    def __init__(self,userid,storyid):  
        self.userid=userid
        self.storyid=storyid

class Story(db.Model):
    __tablename__='stories'
    id = db.Column(db.Integer, primary_key=True)
    companyname = db.Column(db.String(20))
    url = db.Column(db.String(100))
    headline = db.Column(db.String(100))
    #Not sure how date time will be stored
    timestamp = db.Column(db.Text)
    impact = db.Column(db.Integer)

    def __init__(self,companyname,url,headline,timestamp,impact):  
        self.companyname=companyname
        self.url=url
        self.headline=headline
        self.timestamp=timestamp
        self.impact=impact

#Add data to database
def dbinit():
    all_companies = [
        #Tech
        Company("Apple",2820.00,161000,"AAPL","Tim Cook"),
        Company("Microsoft",2992.91,221000,"MSFT","Satya Nadella"),
        Company("Amazon",1750.00,1525000,"AMZN","Andy Jassy"),
        #Company("Google",1801.00,156500,"GOOG","Sundar Pichai"), there are problems with having Google specifically as a company
        Company("Meta Platforms",1206.68,67317,"META","Mark Zuckerberg"),

        #Finance
        Company("JPMorgan Chase",522.98,250355,"JPM","Jamie Dimon"),
        Company("Bank of America",268.75,213000,"BAC","Brian Moynihan"),
        Company("Wells Fargo",188.52,238698,"WFC","Charles W. Scharf"),
        Company("Morgan Stanley",100.15,80000,"0QYU","Ted Pick"),
        Company("American Express",152.16,74600,"AXP","Stephen Squeri"),

        #Customer Staples
        Company("McDonald's",213.19,150000,"MCD","Chris Kempczinski"),

        #Healthcare
        Company("UnitedHealth Group",482.78,440000,"UNH","Andrew Witty"),
        Company("Johnson & Johnson",382.22,150000,"JNJ","Joaquin Duato"),
        Company("Pfizer",155.67,83000,"PFE","Albert Bourla"),

        #Industrial
        Company("Boeing",122.98,170000,"0BOE","Dave Calhoun"),
        Company("Caterpillar Inc",158.17,113200,"CAT","Jim Umpleby"),

        #Indsutrial and tech
        Company("Tesla",636.80,140000,"TSLA","Elon Musk"),
        Company("Samsung Electronics",269.16,270372,"BC94","Kyung Kye-hyun"),
        Company("Intel",188.23,124800,"INTC","David Zinsner"),

    ]

    db.session.add_all(all_companies)

    all_tags = [

        Company_tag("Apple","Technology"),
        Company_tag("Microsoft","Technology"),
        Company_tag("Amazon","Consumer discretionary"),
        Company_tag("Google","Technology"),
        Company_tag("Meta Platforms","Technology"),
        Company_tag("JPMorgan Chase","Finance"),
        Company_tag("Bank of America","Finance"),
        Company_tag("Wells Fargo","Finance"),
        Company_tag("Morgan Stanley","Finance"),
        Company_tag("American Express","Finance"),
        Company_tag("McDonald's","Consumer discretionary"),
        Company_tag("UnitedHealth Group","Health care"),
        Company_tag("Johnson & Johnson","Health care"),
        Company_tag("Pfizer","Health care"),
        Company_tag("Boeing","Industrial"),
        Company_tag("Caterpillar Inc","Industrial"),
        Company_tag("Tesla","Industrial"),
        Company_tag("Tesla","Technology"),
        Company_tag("Samsung Electronics","Technology"),
        Company_tag("Samsung Electronics","Industrial"),
        Company_tag("Intel","Industrial"),
        Company_tag("Intel","Technology"),

    ]

    db.session.add_all(all_tags)

    hashed_password = security.generate_password_hash("123")

    ########################################################
    #CHANGE THE EMAIL BEFORE USING THE WEBSITE 
    db.session.add(User("Test","u2200657@live.warwick.ac.uk",hashed_password))

    user_id = User.query.filter_by(username="Test").first().id
    
    db.session.add(Company_tracked(user_id,"Apple"))
    db.session.add(Company_tracked(user_id,"Microsoft"))

    storiesTEST = [
        Story("Apple","https://www.forbes.com/sites/davidphelan/2024/02/25/ios-174-release-date-exactly-when-apple-will-change-the-iphone-forever/","Apple Ponders Making New Wearables: AI Glasses, AirPods With Cameras, Smart Ring","2024-02-25",0.5),
        Story("Apple","https://www.forbes.com/sites/davidphelan/2024/02/25/ios-174-release-date-exactly-when-apple-will-change-the-iphone-forever/","Apple Ponders Making New Wearables: AI Glasses, AirPods With Cameras, Smart Ring","2024-02-25",0.5)
    ]

    #db.session.add_all(storiesTEST)

    stories = Story.query.all()

    #for i in stories:
        #db.session.add(Notification(user_id,i.id))

    # commit all the changes to the database file
    db.session.commit()
