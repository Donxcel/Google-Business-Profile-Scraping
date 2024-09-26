import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time

def scroll_to_bottom(driver):
    ''' Scroll down to the bottom of the page '''
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep(1)  # Wait for page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_data(driver, url, target_count):
    driver.get(url)
    data = []
    seen_urls = set()

    # Wait until the main element is present
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
        # Scroll down to load more results
            # Collect all loaded data
    elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Nv2PK")))

    
    while len(data) < target_count:
        try:
            scroll_to_bottom(driver)
            # Find the main container and inner elements
            big_data = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            
            for element in big_data:
                inner_elements = element.find_elements(By.CLASS_NAME, "hfpxzc")
                for inner_element in inner_elements:
                    
                    aria_label = inner_element.get_attribute("aria-label")
                    href = inner_element.get_attribute("href")
                    inner_element.click()
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Io6YTe")))
                

                # # I have to scrolldown 
                #     scroll_to_bottom(driver)
                #     general = inner_element.find_element(By.CLASS_NAME, "rogA2c")
                #     tel_text = general.find_element(By.CLASS_NAME, "Io6YTe").text
                #     print(tel_text)
                    if aria_label and href and href not in seen_urls:
                        data.append({
                            "name": aria_label,
                            "url": href
                        })
                        seen_urls.add(href)
                    
                    # Break the loop if we have reached the target count for this country
                    if len(data) >= target_count:
                        break
        
   
            driver.execute_script("window.scrollBy(0,1000)","")               
            time.sleep(2)  # Give time for new elements to load
            
        except NoSuchElementException as e:
                print(f"Error occurred: {e}")
                break
        except TimeoutException as e:
                print(f"Timeout occurred: {e}")
                break
        

    return data

''' Set up the Chrome options '''
options = Options()
options.add_argument("--disable-web-security")
options.add_argument("--user-data-dir=/tmp/user-data")
options.add_argument("--allow-running-insecure-content")
options.headless = True  # Run Chrome in headless mode

service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

countries = ["restaurants in US", "restaurants in Belgium", "restaurants in Britain", "restaurants in France", "restaurants in India"]
target_count_per_country = 20

all_data = []

for country in countries:
    print(f'for {country}')
    url = "https://www.google.com/maps/search/" + country
    country_data = extract_data(driver, url, target_count_per_country)
    all_data.extend(country_data)
    print(f"Extracted {len(country_data)} entries for {country}")

# Print extracted data
print(json.dumps(all_data, indent=2))

# Save data to a JSON file
with open("data.json", "w") as f:
    json.dump(all_data, f, indent=2)

# Close the browser
driver.quit()
