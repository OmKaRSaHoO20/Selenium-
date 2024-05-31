from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import datetime
import socket
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
CORS(app)

# MongoDB client should be initialized once
client = MongoClient("mongodb+srv://omkarsahoodev20:DzqdCW1der2wiHGv@blogsapp.jilhaz8.mongodb.net/")
db = client["gymguardian"]
collection = db["trending_topics_schema"]

# Twitter credentials
twitter_username = '@Saho0569'
twitter_password = 'damntastic'

# Twitter login function
def login_to_twitter(driver):
    driver.get('https://twitter.com/login')
    wait = WebDriverWait(driver, 20)

    # Wait for the username input field to be clickable and then send username
    username_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[autocomplete="username"]')))
    username_input.send_keys(twitter_username)

    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-175oi2r.r-sdzlij.r-1phboty.r-rs99b7.r-lrvibr.r-ywje51.r-184id4b.r-13qz1uu.r-2yi16.r-1qi8awa.r-3pj75a.r-1loqt21.r-o7ynqc.r-6416eg.r-1ny4l3l')))
    next_button.click()
    
    # Enter password
    password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[autocomplete="current-password"]')))
    password_input.send_keys(twitter_password)
    
    # Click login
    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]')))
    login_button.click()
    
    time.sleep(5)

def scrape_trending_topics(driver):
    driver.get('https://x.com/home')
    time.sleep(5)

    # Ensure we find the "Trending now" section
    trending_section = driver.find_element(By.XPATH, '//section[@aria-labelledby="accessible-list-0"]')
    trends = trending_section.find_elements(By.XPATH, './/span[@dir="ltr"]')

    top_trends = [trend.text for trend in trends[:5]]

    # Get current date and time
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Get IP address
    ip_address = socket.gethostbyname(socket.gethostname())

    template_document = {
        "Topics": [{"Topic": trend} for trend in top_trends],
        "Date": current_date,
        "Time": current_time,
        "IP": ip_address
    }

    # Update or insert the document in MongoDB
    collection.update_one({}, {"$set": template_document}, upsert=True)

    return top_trends

# Function to update trending topics
def update_trending_topics():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        login_to_twitter(driver)
        trends = scrape_trending_topics(driver)
        print("Top 5 Trending Topics:")
        for i, trend in enumerate(trends, start=1):
            print(f"Trend {i}: {trend}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

@app.route('/api/trending_topics', methods=['GET'])
def get_trending_topics():
    # Update trending topics before retrieving them
    update_trending_topics()
    
    trending_topics = collection.find_one()
    if trending_topics:
        # Convert ObjectId to string
        trending_topics['_id'] = str(trending_topics['_id'])
        return jsonify(trending_topics), 200
    else:
        return jsonify({"error": "No trending topics found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
