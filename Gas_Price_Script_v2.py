# Importing the os module to interact with the OS, e.g., to get environment variables.
import os

# Importing the timedelta class to calculate the date for yesterday.
from datetime import datetime, timedelta

# Importing the requests module to send HTTP requests.
import requests

# Importing the webdriver class from selenium for browser automation.
from selenium import webdriver

# Importing the By class from selenium.webdriver.common.by to select HTML elements.
from selenium.webdriver.common.by import By

# Importing Options class from selenium.webdriver.chrome.options to configure ChromeDriver options.
from selenium.webdriver.chrome.options import Options

# Discord webhook URL obtained from environment variables.
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# This function retrieves the HTML content from the URL and parses it.
def retrieve_and_parse(url):

    global title_variable

    # Set Chrome options for headless mode.
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode.

    with webdriver.Chrome(options=chrome_options) as browser:  # Pass options to Chrome.
        
        browser.get(url)  # Navigate to the URL.

        # Extracting the prices. Uses the element IDs to locate elements and extract text, while also cleaning up the text.
        price_today = browser.find_element(By.ID, 'priceToday').text.replace('$', '').replace('/L', '').strip()
        price_yesterday = browser.find_element(By.ID, 'priceYesterday').text.replace('$', '').replace('/L', '').strip()
        price_tomorrow = browser.find_element(By.ID, 'priceTomorrow').text.replace('$', '').replace('/L', '').strip()

        # Extracting the dates.
        date_today = browser.find_element(By.ID, 'dateToday').text.strip()
        date_tomorrow = browser.find_element(By.ID, 'dateTomorrow').text.strip()

        # Convert the date strings to datetime objects.
        date_today_obj = datetime.strptime(date_today, "%d-%m-%Y")
        date_tomorrow_obj = datetime.strptime(date_tomorrow, "%d-%m-%Y")

        # Get the name of the day of the week.
        day_name_today = date_today_obj.strftime("%A")
        day_name_tomorrow = date_tomorrow_obj.strftime("%A")

        # Calculate the date and day name for yesterday.
        date_yesterday_obj = date_today_obj - timedelta(days=1)
        day_name_yesterday = date_yesterday_obj.strftime("%A")
        #date_yesterday = date_yesterday_obj.strftime("%d-%m-%Y") # Need if there is a future display of yesterday's price.

        # Formatting the dates with the day names.
        formatted_today = f"Price today ({day_name_today} - {date_today}): **${price_today}/L**"
        formatted_yesterday = f"Price yesterday ({day_name_yesterday}): **${price_yesterday}/L**"
        formatted_tomorrow = f"Price tomorrow ({day_name_tomorrow} - {date_tomorrow}): **${price_tomorrow}/L**"

        title_variable = f"{day_name_tomorrow} - {date_tomorrow}"

        # Returning a dictionary containing the extracted information.
        return {
            'price_today': price_today,
            'price_yesterday': price_yesterday,
            'price_tomorrow': price_tomorrow,
            'formatted_today': formatted_today,
            'formatted_yesterday': formatted_yesterday,
            'formatted_tomorrow': formatted_tomorrow,
        }

# This function sends the information to Discord via a webhook.    
def send_to_discord(parsed_content):

    # Check if the WEBHOOK_URL environment variable has been set.
    if not WEBHOOK_URL:

        raise ValueError("Missing WEBHOOK_URL environment variable.")

    # Convert the price strings to float for comparison.
    price_today = float(parsed_content['price_today'])
    #price_yesterday = float(parsed_content['price_yesterday']) # Need if calculations are done for price change from yesterday to today.
    price_tomorrow = float(parsed_content['price_tomorrow'])

    # Determine the price change from today to tomorrow in cents
    change_tomorrow_cents = (price_tomorrow - price_today) * 100  # Convert dollar change to cents.
 
    # Create a description of the price change from today to tomorrow.
    if change_tomorrow_cents > 0:

        quick_summary = f"The price will increase by {int(abs(change_tomorrow_cents))} cent{'s' if int(abs(change_tomorrow_cents)) != 1 else ''} for tomorrow ({title_variable})."
    
    elif change_tomorrow_cents < 0:

        quick_summary = f"The price will decrease by {int(abs(change_tomorrow_cents))} cent{'s' if int(abs(change_tomorrow_cents)) != 1 else ''} for tomorrow ({title_variable})."
    
    else:

        quick_summary = f"The price will remain the same for tomorrow ({title_variable})."

    # Formatting the message content.
    content = (
        f"{quick_summary}\n"
        f"---------------------------------------------\n"
        f"{parsed_content['formatted_tomorrow']}\n"
        f"{parsed_content['formatted_today']}\n"
        f"{parsed_content['formatted_yesterday']}\n"      
    )

    # Sending the message to Discord via the webhook.
    requests.post(WEBHOOK_URL, json={'content': content})

# This function is the main function that calls the other functions.
def main():

    # Define the URL to be scraped.
    url = 'https://www.en-pro.com/index.html'

    # Call the retrieve_and_parse function to extract information.
    parsed_content = retrieve_and_parse(url)

    # Call the send_to_discord function to send the information to Discord.
    send_to_discord(parsed_content)

# This block ensures the main() function is called only when the script is run directly, not when imported as a module.
if __name__ == "__main__":

    main()