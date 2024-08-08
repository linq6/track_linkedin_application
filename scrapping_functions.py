from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# LinkedIn URLs
LOGIN_URL = 'https://www.linkedin.com/login'
JOB_URL = 'https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED'

def login(driver, USERNAME, PASSWORD):
    driver.get(LOGIN_URL)
    
    # Enter username
    username_field = driver.find_element(By.ID, 'username')
    username_field.send_keys(USERNAME)
    
    # Enter password
    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(PASSWORD)
    
    # Submit login form
    password_field.send_keys(Keys.RETURN)


def scrape_page(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    job_elements = soup.select('a.app-aware-link')
    job_title_list = []
    job_link_list = []
    for job in job_elements:
        job_title = job.text.strip()
        job_link = job.get('href')
        if len(job_title)>1:
            # print(job_title)
            job_title_list.append(job_title)

        job_link_list.append(job_link)

    company_elements = soup.find_all(class_='entity-result__primary-subtitle t-14 t-black t-normal')
    comp_name_list = []
    for comp in company_elements:
        comp_name = comp.text.strip()
        # print(comp_name)

        comp_name_list.append(comp_name)

    working_locations = soup.find_all(class_="entity-result__secondary-subtitle t-14 t-normal")
    location_list = []
    for location in working_locations:
        location_name = location.text.strip()
        location_name = location_name.split('(',2)[0]
        if location_name[-1] == ' ':
            location_name = location_name[:-1]
        location_list.append(location_name)

    l = len(comp_name_list)
    data = pd.DataFrame({'Job Title':job_title_list[-l:],'Comapny Name':comp_name_list,'Location':location_list,'Link':job_link_list[-l:]})        
    return data

def scrape_all_pages(driver):
    all_data = pd.DataFrame()

    while True:
        # Scrape the current page
        data = scrape_page(driver)
        all_data = pd.concat([all_data, data], ignore_index=True)

        try:
            # Check if there is a "Next" button and click it
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Next")]'))
            )
            next_button.click()

            # Wait for the next page to load
            time.sleep(3)
        except Exception as e:
            # If there is no "Next" button, break the loop
            print("No more pages or error occurred:", e)
            break

    return all_data