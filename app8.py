import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import cloudscraper
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def setup_driver(cookies=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    if cookies:
        driver.get('https://beacon.schneidercorp.com')
        for cookie in cookies:
            driver.add_cookie(cookie)

    return driver

def fetch_with_selenium(url, cookies=None):
    driver = setup_driver(cookies)

    try:
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load content
        html_content = driver.page_source
    except Exception as e:
        print(f"Error fetching the URL with Selenium: {e}")
        driver.quit()
        return None
    driver.quit()

    return html_content

def fetch_with_cloudscraper(url):
    scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
    response = scraper.get(url)
    return response.content

def scrape_property_data(url, method='cloudscraper'):
    if method == 'cloudscraper':
        html_content = fetch_with_cloudscraper(url)
    elif method == 'selenium':
        html_content = fetch_with_selenium(url)
    elif method == 'cookies':
        # Example cookies, replace with actual cookies
        cookies = [
            {'name': 'cookie_name', 'value': 'cookie_value', 'domain': '.schneidercorp.com'}
        ]
        html_content = fetch_with_selenium(url, cookies)
    else:
        return None

    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'lxml')

    # Extract data
    data = {}

    # Summary
    summary = soup.find('div', id='ctlBodyPane_ctl00_lblName', string='Summary')
    if summary:
        summary_section = summary.find_parent('div', class_='module-content')
        if summary_section:
            data['Parcel ID'] = summary_section.find('strong', string='Parcel ID').find_next_sibling(text=True).strip()
            data['Property Address'] = summary_section.find('strong', string='Property Address').find_next_sibling('div').text.strip()
            data['Brief Tax Description'] = summary_section.find('strong', string='Brief Tax Description').find_next_sibling(text=True).strip()
            data['Acres'] = summary_section.find('strong', string='Acres').find_next_sibling(text=True).strip()
            data['Class Code'] = summary_section.find('strong', string='Class Code').find_next_sibling(text=True).strip()
            data['Tax District'] = summary_section.find('strong', string='Tax District').find_next_sibling(text=True).strip()

    # Additional HTML Paragraphs
    additional_info = soup.find('p')
    if additional_info:
        paragraphs = additional_info.find_all('br')
        for paragraph in paragraphs:
            text = paragraph.previous_sibling.strip()
            if text.startswith("Parcel ID:"):
                data['Parcel ID'] = text.split("Parcel ID:")[-1].strip()
            elif text.startswith("Property Address:"):
                data['Property Address'] = text.split("Property Address:")[-1].strip()
            elif text.startswith("Brief Tax Description:"):
                data['Brief Tax Description'] = text.split("Brief Tax Description:")[-1].strip()
            elif text.startswith("Acres:"):
                data['Acres'] = text.split("Acres:")[-1].strip()
            elif text.startswith("Class Code:"):
                data['Class Code'] = text.split("Class Code:")[-1].strip()
            elif text.startswith("Tax District:"):
                data['Tax District'] = text.split("Tax District:")[-1].strip()

    # Owners
    owners = soup.find('div', id='ctlBodyPane_ctl01_lblName', string='Owners')
    if owners:
        owners_section = owners.find_parent('div', class_='module-content')
        if owners_section:
            data['Primary Owner'] = owners_section.find('span', id='ctlBodyPane_ctl01_ctl01_rptOwner_ctl00_sprOwnerName1_lnkUpmSearchLinkSuppressed_lblSearch').text.strip()
            data['Owner Address'] = owners_section.find('span', id='ctlBodyPane_ctl01_ctl01_rptOwner_ctl00_lblOwnerAddress').text.strip()

    # Valuation
    valuation = soup.find('div', id='ctlBodyPane_ctl11_lblName', string='Valuation - Assessment Year')
    if valuation:
        valuation_table = valuation.find_next('table')
        if valuation_table:
            df_valuation = pd.read_html(str(valuation_table))[0]
            data['Valuation'] = df_valuation.to_dict('records')

    # Taxation
    taxation = soup.find('div', id='ctlBodyPane_ctl12_lblName', string='Taxation')
    if taxation:
        taxation_table = taxation.find_next('table')
        if taxation_table:
            df_taxation = pd.read_html(str(taxation_table))[0]
            data['Taxation'] = df_taxation.to_dict('records')

    return data

# Streamlit app
st.title('Property Data Scraper')

# Input field for URL
url = st.text_input('Enter the property URL:')
method = st.selectbox('Select scraping method:', ['cloudscraper', 'selenium', 'cookies'])

if st.button('Scrape Data'):
    if url:
        try:
            data = scrape_property_data(url, method=method)

            if not data:
                st.error('Failed to extract data. Please check the URL and try again.')
            else:
                # Display the extracted data
                st.subheader('Extracted Property Data')

                st.write("**Summary Information**")
                st.write(f"Parcel ID: {data.get('Parcel ID', 'N/A')}")
                st.write(f"Property Address: {data.get('Property Address', 'N/A')}")
                st.write(f"Brief Tax Description: {data.get('Brief Tax Description', 'N/A')}")
                st.write(f"Acres: {data.get('Acres', 'N/A')}")
                st.write(f"Class Code: {data.get('Class Code', 'N/A')}")
                st.write(f"Tax District: {data.get('Tax District', 'N/A')}")

                st.write("**Owner Information**")
                st.write(f"Primary Owner: {data.get('Primary Owner', 'N/A')}")
                st.write(f"Owner Address: {data.get('Owner Address', 'N/A')}")

                st.write("**Valuation Data**")
                if 'Valuation' in data:
                    st.dataframe(pd.DataFrame(data['Valuation']))
                else:
                    st.write("No valuation data found.")

                st.write("**Taxation Data**")
                if 'Taxation' in data:
                    st.dataframe(pd.DataFrame(data['Taxation']))
                else:
                    st.write("No taxation data found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning('Please enter a URL.')

