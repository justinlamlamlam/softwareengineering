#webScraper.py
#does webScraping

import analysis

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db_schema import db, dbinit, User, Company, Company_tag, Company_tracked, Story, Notification
from flask_mail import Mail, Message

from flask import Flask, render_template, request, session, redirect
app = Flask(__name__)
mail = Mail(app)

from datetime import datetime
from dateutil.relativedelta import relativedelta
import re 

def webScraper():

    model = analysis.init()

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

        times = driver.find_elements(By.XPATH,"//div[contains(@class'OSrXXb rbYSKb')]")

        companyStories = Story.query.filter_by(companyname=company.companyname)

        for result,time in zip(results,times):
            link = result.get_attribute('href')
            headline = result.text.split('\n')[1]
            inDB = 0
            for c in companyStories:
                if c.url == link:
                    #app.logger.info("article already in database") 
                    inDB = 1
                #app.logger.info(c.headline)
                #app.logger.info(headline)
                #app.logger.info("similarity score: ")
                #app.logger.info(analysis.text_similarity(c.headline,headline)[0])
                if analysis.text_similarity(c.headline,headline)[0] > 0.6:
                   #app.logger.info("same story already in database")
                   inDB = 1
                #else:
                    #app.logger.info("story not in db")
            if inDB == 0:
                #app.logger.info("can add to db")
                date = datetime.now()

                if "hours ago" in time.text:
                    date = date - relativedelta(hours=int(time.text[0:2]))
                elif "days ago" in time.text:
                    date = date - relativedelta(days=int(time.text[0:2]))
                elif "months ago" in time.text:
                    date = date - relativedelta(months=int(time.text[0:2]))

                date = date.strftime('%Y-%m-%d')

                story = Story(company.companyname,link,headline,date,round(analysis.analyse(model,headline)[0],2))
                db.session.add(story)
                check_story(story)

    db.session.commit()
    driver.close()

#Checks to see if the users need to get notices for a story
def check_story(story):

    if story.impact > 0.5 or story.impact < -0.5:

        companyname = story.companyname

        company_tracked = Company_tracked.query.filter_by(companyname=companyname)

        users = []

        for i in company_tracked:
            users.append(i.userid)
        
        for user_id in users:

            useremail = User.query.filter_by(id=user_id).first().email
 
            msg = Message("Important Notice",
                    sender=("MarketMood","u2200657@live.warwick.ac.uk"),
                    body=("The company you tracked: " + companyname.upper() + " has a new story that could have a major impact on it, go on MarketMood to see more details."),
                    #recipients=['u2200657@live.warwick.ac.uk'])
                    recipients=[useremail]) #This would be the actual code

            #mail.send(msg) #sends the mail PLEASE CHANGE THE EMAIL IN THE DATABSE FIRST

            notification = Notification(user_id,story.id)
            db.session.add(notification)

            db.session.commit()
        
        