import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Optionally remove for debugging
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path='/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service)
    return driver

def accept_cookies(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()
        print("Cookies accepted.")
        time.sleep(1)  # Allow for UI updates
    except TimeoutException:
        print("Cookie button not found or not clickable.")

def close_email_alert_overlay(driver, email_alert_closed):
    if not email_alert_closed:
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='close']"))
            )
            close_button.click()
            print("Email alert overlay closed.")
            return True  # Update the flag indicating the overlay has been closed
        except TimeoutException:
            print("Email alert overlay not found or not clickable at the moment.")
    return email_alert_closed

def fetch_jobs(base_url, preferences, max_pages=None):
    search_query = preferences['search_query'].replace(' ', '+')
    location = preferences['location'].replace(' ', '+')
    url = f"{base_url}/jobs?q={search_query}&l={location}"
    driver = setup_driver()
    driver.get(url)
    accept_cookies(driver)  # Accept cookies immediately after page load
    wait = WebDriverWait(driver, 20)
    jobs = []
    email_alert_closed = False
    page_count = 0  # Initialize page count

    try:
        while True:
            job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.css-5lfssm")))
            job_cards = [card for card in job_cards if card.find_elements(By.CSS_SELECTOR, "td.resultContent")]

            for job_card in job_cards:
                job_info = process_job_card(job_card, preferences)
                if job_info:
                    jobs.append(job_info)

            page_count += 1  # Increment the page count
            if max_pages and page_count >= max_pages:
                print(f"Reached max pages limit: {max_pages}")
                break  # Break the loop if the maximum page limit is reached

            try:
                next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")))
                next_button.click()
                print(f"Moving to page {page_count + 1}...")
                email_alert_closed = close_email_alert_overlay(driver, email_alert_closed)
                time.sleep(random.randint(5, 15))  # Mimic human browsing delays
            except ElementClickInterceptedException:
                accept_cookies(driver)  # Try accepting cookies again if needed
                email_alert_closed = close_email_alert_overlay(driver, email_alert_closed)
                next_button.click()  # Attempt to click again
            except TimeoutException:
                print("No more pages to navigate.")
                break

    finally:
        driver.quit()

    jobs.sort(key=lambda x: (-x['keyword_count'], x['job_title']))
    for job in jobs:
        print(f"Job Title: {job['job_title']}, Company: {job['company_name']}, Location: {job['location']}, Keywords: {job['keyword_count']}")

def process_job_card(job_card, preferences):
    try:
        # Flexible and conditional checks for job title and extracting URL
        title_elements = job_card.find_elements(By.CSS_SELECTOR, "h2.jobTitle > a")
        if title_elements:
            job_title = title_elements[0].find_element(By.CSS_SELECTOR, "span[title]").get_attribute('title').lower()
            job_url = title_elements[0].get_attribute('href')
        else:
            job_title = "Job title not found"
            job_url = "URL not found"
        
        # Attempt to find the company name with a more flexible approach
        company_elements = job_card.find_elements(By.CSS_SELECTOR, "[data-testid='company-name']")
        company_name = company_elements[0].text if company_elements else "Company name not found"
        
        # Similar approach for location
        location_elements = job_card.find_elements(By.CSS_SELECTOR, "[data-testid='text-location']")
        location = location_elements[0].text if location_elements else "Location not found"
        
        # Getting job descriptions
        job_description_elements = job_card.find_elements(By.CSS_SELECTOR, "div[role='presentation'] .css-9446fg > ul > li")
        job_descriptions = " ".join([desc.text.lower() for desc in job_description_elements])

        # Combined text for omit keyword check
        combined_text = job_title + " " + job_descriptions

        # Check if the combined text contains any of the omit keywords
        if any(omit_keyword.lower() in combined_text for omit_keyword in preferences['omit_keywords']):
            print(f"Omitted Job: {job_title} - Contains omit keyword")
            return None  # Skip this job card if it contains any omit keywords

        keyword_count = sum(pref.lower() in combined_text for pref in preferences["prefer_keywords"])

        print(f"Debug: Job Title - {job_title}")
        print(f"Debug: Company Name - {company_name}")
        print(f"Debug: Location - {location}")
        print(f"Debug: Job Descriptions - {job_descriptions}")
        print(f"Debug: URL - {job_url}")

        return {"job_title": job_title, "company_name": company_name, "location": location, "keyword_count": keyword_count, "url": job_url}
    except Exception as e:
        print(f"Error processing job card: {e}")
        return None












if __name__ == "__main__":
    user_preferences = {
        'search_query': input("Enter the job title you want to search for (e.g., 'python software engineer'): "),
        'location': input("Enter the location for the job search (e.g., 'London'): "),
        'omit_keywords': ["senior", "principal", "staff"],
        'prefer_keywords': ["entry level", "junior", "python"]
    }
    fetch_jobs("https://www.indeed.co.uk", user_preferences, max_pages=3)
