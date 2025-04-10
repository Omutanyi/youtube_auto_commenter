import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv

load_dotenv()

CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
VIDEO_URL = os.getenv("VIDEO_URL")
COOKIES_FILE = os.getenv("COOKIES_FILE")
REPLY_TEXT = os.getenv("REPLY_TEXT")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

def save_cookies(driver, path):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print("Cookies saved.")

def load_cookies(driver, path):
    with open(path, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            if 'sameSite' in cookie:
                del cookie['sameSite'] 
            driver.add_cookie(cookie)
    print("Cookies loaded.")

def login_if_needed():
    driver.get("https://studio.youtube.com")
    if os.path.exists(COOKIES_FILE):
        driver.get("https://studio.youtube.com") 
        time.sleep(30)
        load_cookies(driver, COOKIES_FILE)
        driver.refresh()
        time.sleep(30)
    else:
        print("Please log in manually...")
        time.sleep(60)
        save_cookies(driver, COOKIES_FILE)

def auto_reply():
    driver.get(VIDEO_URL)
    time.sleep(10)

    # Scroll to load more comments
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(30)

    reply_buttons = driver.find_elements(By.XPATH, "//ytcp-comment-button[@id='reply-button']")
    print(f"Found {len(reply_buttons)} comments to reply to.")

    for i, reply_button in enumerate(reply_buttons):
        try:
            print(f"Replying to comment {i+1}...")
            reply_button.click()
            time.sleep(2)

            textarea = driver.find_element(By.XPATH, "//textarea[@id='textarea']")
            textarea.send_keys(REPLY_TEXT)
            time.sleep(1)

            wait = WebDriverWait(driver, 10)

            send_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-comment-button[@id='submit-button']")))
            send_button.click()
            time.sleep(3)
        except Exception as e:
            print(f"Skipped comment {i+1}: {e}")
            continue

    print("✅ Done replying to comments.")
    driver.quit()

# Run 
login_if_needed()
auto_reply()
