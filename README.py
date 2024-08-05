Property Data Scraper Overview

*Currenlty, the Cloudflare method does not work.

This project provides a web scraper for extracting property data from URLs. It uses different methods to fetch the HTML content from the provided URLs and parses it to extract relevant property information. The tool is built using Python and integrates with Streamlit for a user-friendly interface.

Features
Fetch Property Data: Extracts property details such as Parcel ID, Property Address, Tax Description, Acres, Class Code, and Tax District.
  
Scraping Methods: Supports fetching data using cloudscraper, selenium, or with specified cookies.
  
Valuation and Taxation Data: Extracts and displays valuation and taxation data in tabular format.
  
User Interface: A simple web interface for inputting URLs and selecting the scraping method.
  
Requirements
Python 3.7 or later
Libraries:
streamlit
pandas
beautifulsoup4
requests
cloudscraper
selenium
webdriver-manager
lxml
Installation
Clone the repository or download the code.

bash
Copy code
git clone https://github.com/SimpleMobileResponsiveWebsites/Property-Data-Scraper.git
cd property-data-scraper
Create a virtual environment and activate it:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install the required libraries:

bash
Copy code
pip install -r requirements.txt
Ensure you have the necessary browser drivers installed. The webdriver-manager library will handle this automatically.

Usage
Run the Streamlit application:

bash
Copy code
streamlit run app.py
Open the provided URL in your web browser (typically at http://localhost:8501).

Enter the property URL you wish to scrape in the input field.

Choose the scraping method from the dropdown menu:

cloudscraper: Uses CloudScraper to fetch the page content.

selenium: Uses Selenium WebDriver for dynamic content.
                       
cookies: Uses Selenium with specified cookies (update the example cookies as needed).

Click the "Scrape Data" button to fetch and display the property data.

Code Overview

setup_driver(cookies=None): Configures the Selenium WebDriver with options and handles cookies.
  
fetch_with_selenium(url, cookies=None): Fetches page content using Selenium.
  
fetch_with_cloudscraper(url): Fetches page content using CloudScraper.
  
scrape_property_data(url, method='cloudscraper'): Main function to scrape data using the selected method and parse HTML content.
  
Streamlit App: Provides an interface for user input and displays the extracted data.
  
Troubleshooting
  
Missing Packages: Ensure all required packages are installed using pip install -r requirements.txt.
Browser Driver Issues: If encountering issues with Selenium, make sure webdriver-manager is up-to-date.
