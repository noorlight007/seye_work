import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from db_manage import create_new_property


senegal_links= ["https://sabluximmobilier.com/?advanced_contystate=senegal&filter_search_action%5B0%5D=appartements&property_status=&submit=Recherche&elementor_form_id=18618",
                "https://sabluximmobilier.com/page/2/?advanced_contystate=senegal&filter_search_action%5B0%5D=appartements&property_status&submit=Recherche&elementor_form_id=18618",
                "https://sabluximmobilier.com/?advanced_contystate=senegal&filter_search_action%5B0%5D=plateaux-de-bureau&property_status&submit=Recherche&elementor_form_id=18618",
                "https://sabluximmobilier.com/page/2/?advanced_contystate=senegal&filter_search_action%5B0%5D=plateaux-de-bureau&property_status&submit=Recherche&elementor_form_id=18618",
                "https://sabluximmobilier.com/?advanced_contystate=senegal&filter_search_action%5B%5D=terrains&property_status=&submit=Recherche&elementor_form_id=18618",
                "https://sabluximmobilier.com/page/2/?advanced_contystate=senegal&filter_search_action%5B0%5D=terrains&property_status&submit=Recherche&elementor_form_id=18618",
                "https://sabluximmobilier.com/?advanced_contystate=senegal&filter_search_action%5B%5D=villa&property_status=&submit=Recherche&elementor_form_id=18618",
                "https://sabluximmobilier.com/page/2/?advanced_contystate=senegal&filter_search_action%5B0%5D=villa&property_status&submit=Recherche&elementor_form_id=18618"]

def scrape_sablux_properties(url):
    # Set up headless Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("chromedriver.exe")  # Update the path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the webpage
    driver.get(url)

    # Wait for the content to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "listing_ajax_container"))
    )

    # Get page source and close the driver
    page_source = driver.page_source
    driver.quit()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")
    listings = soup.find("div", {"id": "listing_ajax_container"}).find_all("div", class_="property_listing")

    # Extract property details
    properties = []
    for listing in listings:
        # Extract price
        price_span = listing.find("div", class_="listing_unit_price_wrapper")
        price = price_span.text.strip() if price_span else "N/A"

        # Extract property link
        property_link = listing.get("data-link", "N/A")

        # Extract property type
        property_type_div = listing.find("div", class_="action_tag_wrapper")
        property_type = property_type_div.text.strip() if property_type_div else "N/A"

        # Extract property status
        property_status_div = listing.find("div", class_="ribbon-inside")
        property_status = property_status_div.text.strip() if property_status_div else "N/A"

        # Extract property name
        property_name_tag = listing.find("h4").find("a")
        property_name = property_name_tag.text.strip() if property_name_tag else "N/A"


        create_new_property(property_name, property_type, property_status, price, property_link)

# Example Usage
url = "https://sabluximmobilier.com/?advanced_contystate=senegal&filter_search_action%5B0%5D=appartements&property_status=&submit=Recherche&elementor_form_id=18618"
scrape_sablux_properties(url)