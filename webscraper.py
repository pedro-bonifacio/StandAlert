from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from re import findall
from pyvirtualdisplay import Display
from time import sleep


def extract_numbers(s):
    return int(''.join(findall(r'\d+', s)))

def scrape_urls(url_list):
    # display = Display(visible=True, size=(1600, 1200))
    # display.start()
    driver = webdriver.Chrome()
    extracted_data = []  # List to store results

    try:
        for url in url_list:
            driver.get(url)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
            except:
                print(f"Timeout loading {url}")
                continue

            soup = BeautifulSoup(driver.page_source, "html.parser")

            if not soup.find("h2", class_="e4b361b0 ooa-1jjzghu"):
                sleep(4)
                continue

            listings_info = [{'name': elem.text} for elem in soup.find_all("h2", class_="e4b361b0 ooa-1jjzghu")]
            mileage_and_year = [elem.text for elem in soup.find_all("dd", class_="ooa-1cl0af6 e1gy25k12")]
            prices = [elem.text for elem in soup.find_all("h3", class_="ecit9451 ooa-1n2paoq")]
            urls = [elem.a['href'] for elem in soup.find_all("h2", class_="e4b361b0 ooa-1jjzghu")]

            for i in range(len(listings_info)):
                listings_info[i]['mileage'] = extract_numbers(mileage_and_year[i*4])
                listings_info[i]['year'] = extract_numbers(mileage_and_year[3+ i*4])
                listings_info[i]['price'] = extract_numbers(prices[i])
                listings_info[i]['url'] = urls[i]

            extracted_data += listings_info
            sleep(4)

    finally:
        driver.quit()

    return extracted_data
