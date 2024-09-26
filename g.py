import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def setup_driver():
    ''' Set up the Chrome options '''
    options = Options()
    options.add_argument("--disable-web-security")
    options.add_argument("--user-data-dir=/tmp/user-data")
    options.add_argument("--allow-running-insecure-content")
    options.headless = False  # Set to True if you don't need a GUI
    
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scroll_to_bottom(driver):
    ''' Scroll down to the bottom of the page '''
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)  # Wait for page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


'''Function to remove unnecessary characters'''
def remove_before_character(s, char):
    index = s.find(char)
    if index != -1:
        return s[index + 1:]
    return s



def extract_data(driver, url, target_count):
    driver.get(url)
    data = []
    seen_urls = set()

    # Wait until the main element is present
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))

    while len(data) < target_count:
        scroll_to_bottom(driver)
        try:
            
            # Find the main container and inner elements
            big_data = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            
            for element in big_data:
                try:
                    inner_elements = element.find_elements(By.CLASS_NAME, "hfpxzc")
                    for inner_element in inner_elements:
                        aria_label = inner_element.get_attribute("aria-label")
                        href = inner_element.get_attribute("href")
                        if aria_label and href and href not in seen_urls:
                            inner_element.click()
                            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Io6YTe")))
                            time.sleep(2)  # Ensure the detailed page is loaded

                            name = aria_label
                            address = ""
                            phone = ""
                            hours = ""
                            reviews = ""
                            websites = ""

                            try:
                                address = driver.find_element(By.CLASS_NAME, "rogA2c ")
                                address = address.find_element(By.CLASS_NAME, "Io6YTe").text
                                
                            except NoSuchElementException:
                                address = "No Address"

                            try:
                                elements = driver.find_elements(By.CLASS_NAME, 'CsEnBe')
                                for i in  range(len(elements)):
                                    if "+" in elements[i].text:

                                        ''' Ensuring we store a real phone number    '''

                                        phone = elements[i].text
                                        phone = remove_before_character(phone,'\n')
                                        testing_phone = phone.replace(' ','')
                                        testing_phone = testing_phone.replace('-','')
                                        testing_phone = testing_phone.replace('+','')
                                        if int(testing_phone):
                                            phone = remove_before_character(phone,'\n')
                
                                        else:
                                            phone = "No Phone"

                                        break
                                    else:
                                        phone = "No Phone"
                                print("Phone Number:", phone)
                            except NoSuchElementException:
                                phone = "No Phone"

                            try:
                                full_hours = driver.find_element(By.CLASS_NAME, 'ZDu9vd')
                                status = full_hours.find_element(By.CSS_SELECTOR, 'span[style="font-weight: 400; color: rgba(24,128,56,1.00);"]')
                                open_time  = full_hours.find_element(By.CSS_SELECTOR, 'span[style="font-weight: 400;"]')
                                hours = status.text +' '+ open_time.text
                                print(hours)
                            except NoSuchElementException:
                                hours = "No Hours"

                            try:
                                reviews = driver.find_element(By.CLASS_NAME,"LBgpqf")
                                reviews = reviews.find_element(By.CLASS_NAME,'F7nice')
                                reviews = reviews.find_element(By.TAG_NAME,'span').text
                            except NoSuchElementException:
                                reviews = "No Reviews"

                            try:
                                websites = driver.find_element(By.CSS_SELECTOR, "a.CsEnBe")
                                websites = websites.find_element(By.CLASS_NAME, "Io6YTe").text  
                                print(websites)
                            except NoSuchElementException:
                                websites = "No website"

                            ### checking if theres data in our various field before we append it to our list of data
                            try:
                                    data.append({
                                        "name": name,
                                        "url": href,
                                        "address": address,
                                        "phone": phone,
                                        "hours": hours,
                                        "reviews": reviews,
                                        "websites": websites
                                    })
                            except:
                                pass
                            seen_urls.add(href)
                            driver.back()  # Go back to the search results
                            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
                except:
                    pass

                    # Break the loop if we have reached the target count for this country
                    if len(data) >= target_count:
                        break

                if len(data) >= target_count:
                    break

        except NoSuchElementException as e:
            print(f"Error occurred: {e}")
            break
        except TimeoutException as e:
            print(f"Timeout occurred: {e}")
            break
    scroll_to_bottom(driver)
    return data

def main():

    driver = setup_driver()
    countries = ["restaurants in US", "restaurants in Belgium", "restaurants in Britain", "restaurants in France", "restaurants in India"]
    target_count_per_country = 5

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

if __name__ == "__main__":
    main()
