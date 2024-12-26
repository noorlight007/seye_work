import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from db_manage import create_new_property

from imp_list import return_total_list, return_luxury_list

def scrape_sablux_properties():

    # Set up headless Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--no-sandbox")  # Run in sandbox mode
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage for large pages

    total_url_list = return_total_list()
    luxury_list = return_luxury_list()
    ## under_const Properties
    for url in total_url_list:
        project_type = ""
        if "haut-de-gamme" in url:
            project_type = "Haut de gamme"
        elif "villas-economiques" in url:
            project_type = "Villas économiques"
        elif "foncier" in url:
            project_type = "Foncier"
        elif "luxe" in url:
            project_type = "Luxe"
        elif "residences-secondaires" in url:
            project_type = "Résidences secondaires"
        elif "professionnel" in url:
            project_type = "Professionnel"
        service = Service("/usr/local/bin/chromedriver")  # Update this to your chromedriver path
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

            ###  ********  ###
            driver_new = webdriver.Chrome(service=service, options=chrome_options)
            print(f"Getting content of {property_link}")
            # Open the webpage
            driver_new.get(property_link)

            # Wait for the content to load
            WebDriverWait(driver_new, 15).until(
                EC.presence_of_element_located((By.ID, "prop_ame"))
            )
            time.sleep(5)
            # Get page source and close the driver
            page_source_new = driver_new.page_source
            driver_new.quit()
            # Parse with BeautifulSoup
            soup_new = BeautifulSoup(page_source_new, "html.parser")

            # Extract property type 
            exact_location_div = soup_new.find("div", class_="property_categs")
            exact_location = exact_location_div.text.strip() if exact_location_div else "N/A"
            print(exact_location)

            # Extract description
            # Find the parent <div> by class or ID
            description_div = soup_new.find("div", class_="wpestate_property_description")

            # Extract all <p> elements within the <div>
            p_tags = description_div.find_all("p")
            description = ""
            # Iterate through each <p> and print its text
            for idx, p in enumerate(p_tags, 1):
                description+= f"{p.text.strip()}\n"
            
            # Extract Country
            info_div = soup_new.find("div", class_="single-overview-section panel-group property-panel")
            country_div = info_div.find_all("li")[5]
            country = country_div.text.strip()

            # Extract amenities
            amenities_div = soup_new.find("div", class_="listing_detail col-md-12 feature_block_others")
            all_amenities = amenities_div.find_all("div")
            list_amenities = []
            for item in all_amenities:
                it = item.text.strip()
                f_it = it.replace("movie-recorderCreated with Sketch Beta.   ", "")
                list_amenities.append(f_it)

            # Extract Property details
            property_id_div = soup_new.find("div", id="propertyid_display")
            property_id = property_id_div.text.strip().split(":")[-1].strip() if property_id_div else "N/A"

            # Extract date of lunch
            dol_div = soup_new.find("div", class_="listing_detail col-md-6 property-year")
            date_of_launch = dol_div.text.strip().split(":")[-1].strip() if dol_div else "N/A"

            # Extract land size
            ls_div = soup_new.find("div", class_="listing_detail col-md-6 terrains")
            land_size = ls_div.text.strip().split(":")[-1].strip() if ls_div else "N/A"

            # Extract lot size
            lot_size_div = soup_new.find("div", class_="listing_detail col-md-6 property_default_lot_size")

            lot_size = lot_size_div.text.strip().split(":")[-1].strip() if lot_size_div else "N/A"
            lot_size = lot_size.replace("ha", "hectare")

            # Extract number of villas
            nv_div = soup_new.find("div", class_="listing_detail col-md-6 villas")
            number_of_villas = nv_div.text.strip().split(":")[-1].strip().split(" ")[0].strip() if nv_div else "N/A"

            # Extract number of Apartments
            apartment_div = soup_new.find("div", class_="listing_detail col-md-6 apartment")
            number_of_apartments = apartment_div.text.strip().split(":")[-1].strip() if apartment_div else "N/A"

            print(f"Property ID: {property_id}\nDate of Launch: {date_of_launch}\nLand Size: {land_size}\nNumber of Villas: {number_of_villas}\nNumber of Apartments = {number_of_apartments}\nLot size = {lot_size}\nCountry = {country}\nDescription = {description}")
            property_details = {"Property ID": property_id, "Date of launch": date_of_launch, "Land Size": land_size, "Number of Villas": number_of_villas,
                                "Number of Apartments": number_of_apartments, "Property Lot Size": lot_size}
            final_amenities = []
            for item in list_amenities[1:]:
                if "Caméra de sécurit" in item:
                    i = item[:-1]
                else:
                    i = item
                final_amenities.append(i)
            
            print(final_amenities)
            # Extract Number
            ###  *********  ###
            create_new_property(property_name, property_type, property_status, price, property_link, project_type, country, exact_location, description,property_details, final_amenities)
        
        
        time.sleep(5)

scrape_sablux_properties()
