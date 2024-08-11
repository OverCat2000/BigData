from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import os

def setup_driver(download_directory):
    """Set up the Selenium WebDriver with the necessary options."""
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")


    driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
    return driver

def navigate_to_url(driver, url):
    """Navigate to the given URL."""
    driver.get(url)
    time.sleep(30)  # Wait for the page to load

def select_year(driver, year):
    """Select the desired year from the dropdown menu."""
    button = driver.find_element(By.XPATH, "//button[@title='Time period']")
    button.click()
    time.sleep(5)
    label = driver.find_element(By.XPATH, f"//label[@for='selectTimePeriod_{year}']")
    label.click()

def start_export(driver):
    """Click the necessary buttons to start the export process."""
    time.sleep(5)
    export_button = driver.find_element(By.ID, "ecdc-btn-export")
    export_button.click()

    time.sleep(5)
    driver.find_element(By.ID, "cckPostponeCookies").click()

    time.sleep(5)
    radio_button = driver.find_element(By.ID, "optionsRadios1")
    radio_button.click()

    time.sleep(5)
    download_button = driver.find_element(By.ID, "ecdc-btn-export-csv")
    download_button.click()

def rename_downloaded_file(original_file_path, new_file_path):
    """Rename the downloaded file."""
    time.sleep(5)
    if os.path.exists(original_file_path):
        os.rename(original_file_path, new_file_path)
        print(f"File renamed to: {new_file_path}")
    else:
        print(f"File not found: {original_file_path}")

def main(year):
    url = "https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=31"
    download_directory = os.path.join(os.getcwd(), "data")
    original_filename = "ECDC_surveillance_data_Leptospirosis.csv"  # Replace with the actual file name
    new_filename = f"{year}.csv"  # The new name you want to give to the file

    # Construct full file paths
    original_file_path = os.path.join(download_directory, original_filename)
    new_file_path = os.path.join(download_directory, new_filename)

    # Setup WebDriver
    driver = setup_driver(download_directory)

    try:
        # Navigate and interact with the webpage
        navigate_to_url(driver, url)
        select_year(driver, year)
        start_export(driver)

        # Rename the downloaded file
        rename_downloaded_file(original_file_path, new_file_path)
    finally:
        # Ensure the browser is closed after the process
        driver.quit()

if __name__ == "__main__":
    main(2015)
