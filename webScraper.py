#webScraper.py
#does webScraping

import analysis

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db_schema import db, dbinit, User, Company, Company_tag, Company_tracked, Story, Notification

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

        times = driver.find_elements(By.XPATH,"//div[@class='OSrXXb rbYSKb LfVVr']")

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
                story = Story(company.companyname,link,headline,time.text,analysis.analyse(model,headline)[0])
                db.session.add(story)

    db.session.commit()
    driver.close()

    #more testting
    #test = Story.query.filter_by(companyname="Wells Fargo")
    #app.logger.info("All Wells Fargo Stories")
    #for t in test:
    #    app.logger.info(t.companyname)
    #    app.logger.info(t.headline)
    #    app.logger.info(t.impact)