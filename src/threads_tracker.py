"""
Threads view-count tracker.

Visits a list of Threads posts with Selenium about every 10 minutes and
appends the current view count of each post to a CSV file.

Usage:
    1. Put the posts you want to track in POSTS below.
    2. Log in to Threads once in the Chrome profile set by PROFILE_DIR.
    3. Run:  python src/threads_tracker.py   (Ctrl+C to stop)
"""
import os
import random
import re
import time
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ================= Settings =================
# Replace with the posts you want to track.
POSTS = [
    {"label": "Costco",  "url": "https://www.threads.net/@<user>/post/<post_id>"},
    {"label": "London",  "url": "https://www.threads.net/@<user>/post/<post_id>"},
    {"label": "Seattle", "url": "https://www.threads.net/@<user>/post/<post_id>"},
    {"label": "news",    "url": "https://www.threads.net/@<user>/post/<post_id>"},
    {"label": "trends",  "url": "https://www.threads.net/@<user>/post/<post_id>"},
]

# Base wait of 8 minutes plus a random 0 to 4 minutes, about 10 minutes per round.
BASE_INTERVAL_MINUTES = 8

CSV_FILENAME = os.path.join("data", "threads_raw.csv")
PROFILE_DIR = os.path.expanduser("~/Threads_Profile")
# ============================================


def get_page_text(driver, url):
    """Open a post and return all visible text on the page."""
    try:
        print(f"Loading: {url}")
        driver.get(url)
        time.sleep(random.uniform(5, 10))  # let the page finish loading
        return driver.find_element(By.TAG_NAME, "body").text
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None


def main():
    os.makedirs(os.path.dirname(CSV_FILENAME), exist_ok=True)

    options = Options()
    options.add_argument(f"user-data-dir={PROFILE_DIR}")
    # options.add_argument("--headless")  # uncomment to hide the browser window

    print("Tracker started. Press Ctrl+C to stop.")
    driver = webdriver.Chrome(options=options)

    try:
        while True:
            batch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"--- New round: {batch_time} ---")

            for post in POSTS:
                label, url = post["label"], post["url"]
                text = get_page_text(driver, url)

                if text:
                    match = re.search(r"([\d\.K,]+)\s+views", text)
                    if match:
                        views = match.group(1)
                        print(f"   [ok] {label}: {views} views")
                        row = pd.DataFrame([[batch_time, label, views]],
                                           columns=["Time", "Post_Label", "Views"])
                        write_header = not os.path.isfile(CSV_FILENAME)
                        row.to_csv(CSV_FILENAME, mode="a", header=write_header, index=False)
                    else:
                        print(f"   [skip] {label}: view count not found")

                time.sleep(random.uniform(10, 20))  # short pause between posts

            sleep_s = BASE_INTERVAL_MINUTES * 60 + random.uniform(0, 4) * 60
            print(f"Round finished. Sleeping {sleep_s / 60:.1f} minutes...")
            time.sleep(sleep_s)

    except KeyboardInterrupt:
        print("Stopping tracker...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
