from bs4 import BeautifulSoup
import pandas as pd 
import requests
from splinter import Browser
import tweepy
from config import consumer_key, consumer_secret, access_token, access_token_secret
import time

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

def init_browser():
    executable_path = {"executable_path": "/Users/erincullen/Downloads/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

url_jpl = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
url_nasa = "https://mars.nasa.gov/news/"
target_user = "@marswxreport" 
url_facts = "https://space-facts.com/mars/"
url_hemi = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"


def scrape():
    browser = init_browser()
    mars_data= {}

    #scrape Nasa for News
    url_nasa = "https://mars.nasa.gov/news/"
    browser.visit(url_nasa)
    soup = BeautifulSoup(browser.html, "html.parser")
    news = soup.find(class_="item_list")
    headline = news.find(class_="content_title").text
    news = news.find(class_="article_teaser_body").text

    #Mars Featured Image Scraper
    browser.visit(url_jpl)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)
    browser.click_link_by_partial_text('more info')
    time.sleep(5)
    
    soup = BeautifulSoup(browser.html, "html.parser")
    results = soup.find('article')
    ext = results.find("figure", class_='lede').a['href']
    base = "https://www.jpl.nasa.gov"
    featured_image_url = base + ext

    #Mars Weather Scrape Twitter
    results = api.user_timeline(target_user)  
    weather =[]
    
    #Remove non-weather based tweets
    for r in results: 
        if 'Sol'in r['text']:
            weather.append(r['text'])
        else:
            pass
    mars_weather = weather[0]

    #Mars Table Scraper
    tables = pd.read_html(url_facts)
    df = tables[0]
    table=df.to_html(index=False)

    #Scrape hemisphere data
    hemisphere_data = []
    browser.visit(url_hemi)
    soup = BeautifulSoup(browser.html, "html.parser")
    titles = soup("h3")
    for t in titles: 
        browser.click_link_by_partial_text(t.text)
        soup = BeautifulSoup(browser.html, "html.parser")
        url = soup.find(class_="downloads").a['href']
        hemisphere_data.append({"title":t.text,"image_url":url})
        browser.visit(url_hemi)

    #Create a Mars dictionary
    mars_data = {
        "hemispheres": hemisphere_data, 
        "table" : table,
        "weather" : mars_weather,
        "featured_img_url" : featured_image_url,
        "headline" : headline,
        "news" : news
    }
    browser.quit()
    return mars_data
    