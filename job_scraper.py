import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode for automation
    chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    service = Service(executable_path='/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service)
    return driver

def fetch_jobs(base_url, search_query, location):
    url = f"{base_url}/jobs?q={search_query.replace(' ', '+')}&l={location.replace(' ', '+')}"
    driver = setup_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 45)

    try:
        while True:
            # Wait for the job cards to load
            job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.resultContent")))
            print(f"Found {len(job_cards)} jobs on the current page.")

            for job_card in job_cards:
                process_job_card(job_card)

            try:
                # Attempt to click the next page button
                next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")))
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)  # Brief pause after scroll
                next_button.click()
                print("Moving to the next page...")
                time.sleep(random.randint(5, 15))  # Random sleep to mimic human browsing
            except ElementClickInterceptedException:
                # Attempt to close any overlays and then click the button again
                close_overlays(driver)
                next_button.click()
            except NoSuchElementException:
                print("No more pages to navigate.")
                break

    finally:
        driver.quit()

def process_job_card(job_card):
    job_title = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle > a > span[title]").get_attribute('title')
    company_name = job_card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
    location = job_card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']").text
    print(f"Job Title: {job_title}, Company: {company_name}, Location: {location}")

def close_overlays(driver):
    try:
        # Example: Close cookie banners by their common selectors
        close_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='close'], button[class*='cookie']")
        for button in close_buttons:
            button.click()
    except Exception as e:
        print("Failed to close overlay:", e)

if __name__ == "__main__":
    job_query = input("Enter the job title you want to search for (e.g., 'python software engineer'): ")
    location_query = input("Enter the location for the job search (e.g., 'London'): ")
    fetch_jobs("https://www.indeed.co.uk", job_query, location_query)