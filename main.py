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

# MongoDB credentials
client = MongoClient("mongodb+srv://omkarsahoodev20:DzqdCW1der2wiHGv@blogsapp.jilhaz8.mongodb.net/")
db = client["gymguardian"]
collection = db["trending_topics_schema"]

# Twitter credentials
twitter_username = '@Saho0569'
twitter_password = 'damntastic'

# Main function to update trending topics using Selenium
def main():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        login_to_twitter(driver)
        trends = get_trending_topics(driver)
        print("Top 5 Trending Topics:")
        for i, trend in enumerate(trends, start=1):
            print(f"Trend {i}: {trend}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

# Twitter login function
def login_to_twitter(driver):
    driver.get('https://twitter.com/login')
    wait = WebDriverWait(driver, 20)

    # Waiting for the username input field to be clickable and then send username
    username_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[autocomplete="username"]')))
    username_input.send_keys(twitter_username)

    # Clicking on next button for password input
    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.css-175oi2r.r-sdzlij.r-1phboty.r-rs99b7.r-lrvibr.r-ywje51.r-184id4b.r-13qz1uu.r-2yi16.r-1qi8awa.r-3pj75a.r-1loqt21.r-o7ynqc.r-6416eg.r-1ny4l3l')))
    next_button.click()
    
    # Enter password
    password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[autocomplete="current-password"]')))
    password_input.send_keys(twitter_password)
    
    # Click login
    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="LoginForm_Login_Button"]')))
    login_button.click()
    
    time.sleep(5)

# Scrape trending topics
def get_trending_topics(driver):
    driver.get('https://x.com/home')
    time.sleep(5)

    # Ensure we find the "Trending now" section
    trending_section = driver.find_element(By.XPATH, '//section[@aria-labelledby="accessible-list-0"]')
    trends = trending_section.find_elements(By.XPATH, './/span[@dir="ltr"]')

    top_trends = [trend.text for trend in trends[:5]]

    # Current Date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Current time 
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Get IP address
    ip_address = socket.gethostbyname(socket.gethostname())

    template_document = {
        "Topics": [],
        "Date": current_date,
        "Time": current_time,
        "IP": ip_address
    }

    for trend in top_trends:
        topic_object = {
            "Topic": trend
        }
        template_document["Topics"].append(topic_object)

    collection.update_one({}, {"$set": template_document}, upsert=True)

    return top_trends

# Route to get trending topics to be fetchable on frontend
@app.route('/api/trending_topics', methods=['GET'])
def get_trending_topics_route():
    main() 
    trending_topics = collection.find_one()
    if trending_topics:
        # Convert ObjectId to string
        trending_topics['_id'] = str(trending_topics['_id'])
        return jsonify(trending_topics), 200
    else:
        return jsonify({"error": "No trending topics found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
