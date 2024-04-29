from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

def setup_driver():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Set path to chromedriver as needed
    driver = webdriver.Chrome()

    # Or if you need to specify the path:
    service = Service(executable_path='/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service)
    return driver

def fetch_jobs(url):
    driver = setup_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 20)  # Increased wait time

    try:
        # Wait for the job details to be present on the page
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.resultContent")))
        job_cards = driver.find_elements(By.CSS_SELECTOR, "td.resultContent")

        print(f"Found {len(job_cards)} jobs.")

        for job_card in job_cards:
            try:
                job_title = job_card.find_element(By.CSS_SELECTOR, "h2.jobTitle > a > span[title]").get_attribute('title')

                # Extract company name using data-testid attribute
                try:
                    company_name_elem = job_card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']")
                    company_name = company_name_elem.text
                except NoSuchElementException:
                    company_name = "Company name not found"
                
                # Extract location using data-testid attribute
                try:
                    location_elem = job_card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']")
                    location = location_elem.text
                except NoSuchElementException:
                    location = "Location not found"

                # Extract job metadata description
                job_description_list = job_card.find_elements(By.CSS_SELECTOR, "div.jobMetaDataGroup ul > li")
                job_descriptions = [li.text for li in job_description_list]  # This will give you a list of all job description points

                # Join all descriptions into a single string, separated by semicolon
                job_description_text = "; ".join(job_descriptions)

                print(f"Job Title: {job_title}, Company: {company_name}, Location:{location}")
                print(f"Job Descriptions: {job_description_text}")
                print("---")
            except Exception as e:
                print("An error occurred while trying to extract job details:", e)
                continue

    finally:
        driver.quit()

fetch_jobs("https://www.indeed.com/q-software-engineer-jobs.html")
