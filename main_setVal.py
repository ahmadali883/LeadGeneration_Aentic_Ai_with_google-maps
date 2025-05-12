import streamlit as st
import pandas as pd
import asyncio
import playwright.async_api
from playwright.async_api import async_playwright
import os
import logging
from dataclasses import dataclass, asdict, field
import datetime
import time
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')

if not API_KEY:
    st.error("Error: GOOGLE_API_KEY not found in environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- Define Tool Schemas (Functions the LLM can 'call') ---
search_Maps_func = {
    "name": "search_Maps",
    "description": "Searches Google Maps for businesses based on a query.",
    "parameters": {
        # Use UPPERCASE type names
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING", # Use UPPERCASE
                "description": "The search term for Google Maps (e.g., 'cafes in islamabad', 'restaurants near Eiffel Tower'). Include the type of place and location.",
            },
            "num_results": {
                "type": "INTEGER", # Use UPPERCASE
                "description": "Optional. The desired approximate number of business results to find. Defaults to 20 if not specified.",
            },
        },
        "required": ["query"],
    },
}

prepare_whatsapp_message_func = {
    "name": "prepare_whatsapp_message",
    "description": "Prepares the content and specifies the number of recipients for a WhatsApp message campaign.",
    "parameters": {
        # Use UPPERCASE type names
        "type": "OBJECT",
        "properties": {
            "message": {
                "type": "STRING", # Use UPPERCASE
                "description": "The exact content of the WhatsApp message to be sent.",
            },
            "k": {
                "type": "INTEGER", # Use UPPERCASE
                "description": "Optional. The maximum number of recipients (leads) from the search results to send the message to.",
            },
            "target_numbers": {
                "type": "ARRAY", # Use UPPERCASE
                # The 'items' schema still defines the type of elements within the array
                "items": {"type": "STRING"}, # Keep nested type as STRING
                "description": "Optional. A specific list of phone numbers to send the message to.",
            }
        },
        "required": ["message"],
    },
}

# Initialize the LLM Model with the corrected Tools
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    tools=[search_Maps_func, prepare_whatsapp_message_func] # Pass the corrected dictionaries
)


asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Ensure necessary system packages are installed
os.system(
    'apt-get update && apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libdrm2'
)

# Install Playwright
os.system('pip install playwright')

# Install Playwright browsers
os.system('playwright install')


# Ensure Playwright browsers are installed
async def install_playwright_browsers():
    from playwright.__main__ import main as playwright_main
    await asyncio.create_task(playwright_main(['install']))


# asyncio.run(install_playwright_browsers())


# Ensuring Playwright browsers are installed
async def install_playwright_browsers():
    from playwright.__main__ import main as playwright_main
    await asyncio.create_task(playwright_main(['install']))


# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class Business:
    """Holds business data"""
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    # reviews_count: int = None
    reviews_average: float = None

    def __eq__(self, other):
        if not isinstance(other, Business):
            return NotImplemented
        return (self.name, self.address, self.website, self.phone_number,
                self.reviews_average) == \
               (other.name, other.address, other.website, other.phone_number,
                 other.reviews_average)

    def __hash__(self):
        return hash((self.name, self.address, self.website, self.phone_number,
                     self.reviews_average))


@dataclass
class BusinessList:
    """Holds list of Business objects, and saves to both Excel and CSV"""
    business_list: list[Business] = field(default_factory=list)
    save_at = 'output'

    def dataframe(self):
        """Transform business_list to pandas DataFrame"""
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_")

    def save_to_excel(self, filename):
        """Saves pandas DataFrame to Excel (xlsx) file and returns file path"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        file_path = f"{self.save_at}/{filename}.xlsx"
        try:
            self.dataframe().to_excel(file_path, index=False)
            logging.info(f"Saved data to {file_path}")
            return file_path  # Return the file path after saving
        except Exception as e:
            logging.error(f"Failed to save data to Excel: {e}")
            return None

    def save_to_csv(self, filename):
        """Saves pandas DataFrame to CSV file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        file_path = f"{self.save_at}/{filename}.csv"
        try:
            self.dataframe().to_csv(file_path, index=False)
            logging.info(f"Saved data to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save data to CSV: {e}")

    def get_row_size(self):
        """Returns the number of rows in the DataFrame"""
        return len(self.business_list)


async def scrape_business(search_term, total):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("https://www.google.com/maps", timeout=60000)
            await page.wait_for_timeout(5000)

            await page.fill('//input[@id="searchboxinput"]', search_term)
            await page.wait_for_timeout(3000)

            await page.keyboard.press("Enter")
            await page.wait_for_timeout(5000)

            await page.hover(
                '//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            listings = []

            while True:
                await page.mouse.wheel(0, 10000)
                await page.wait_for_timeout(2000)

                current_count = await page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).count()
                if current_count >= total:

                    all_listings = await page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()

                    listings = all_listings[:total]

                    break

                elif current_count == previously_counted:

                    listings = await page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()

                    break

                else:
                    previously_counted = current_count

            business_list = BusinessList()

            for listing in listings:
                try:
                    await listing.click()
                    await page.wait_for_timeout(3000)

                    name_css_selector = 'h1.DUwDvf.lfPIob'
                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    phone_number_xpath = '//button[contains(@data-item-id, "phone")]//div[contains(@class, "fontBodyMedium")]'
                    # review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                    business = Business()

                    if await page.locator(name_css_selector).count() > 0:
                        business.name = await page.locator(name_css_selector
                                                           ).inner_text()
                    else:
                        business.name = ""

                    if await page.locator(address_xpath).count() > 0:
                        address_elements = await page.locator(address_xpath
                                                              ).all()
                        if address_elements:
                            business.address = await address_elements[
                                0].inner_text()
                        else:
                            business.address = ""
                    else:
                        business.address = ""

                    if await page.locator(website_xpath).count() > 0:
                        website_elements = await page.locator(website_xpath
                                                              ).all()
                        if website_elements:
                            business.website = await website_elements[
                                0].inner_text()
                        else:
                            business.website = ""
                    else:
                        business.website = ""

                    if await page.locator(phone_number_xpath).count() > 0:
                        phone_elements = await page.locator(phone_number_xpath
                                                            ).all()
                        if phone_elements:
                            business.phone_number = await phone_elements[
                                0].inner_text()
                        else:
                            business.phone_number = ""
                    else:
                        business.phone_number = ""

                    # if await page.locator(review_count_xpath).count() > 0:
                    #     review_count_text = await page.locator(
                    #         review_count_xpath).inner_text()
                    #     business.reviews_count = int(
                    #         review_count_text.split()[0].replace(',',
                    #                                              '').strip())
                    # else:
                    #     business.reviews_count = None

                    if await page.locator(reviews_average_xpath).count() > 0:
                        reviews_average_text = await page.locator(
                            reviews_average_xpath).get_attribute('aria-label')
                        if reviews_average_text:
                            business.reviews_average = float(
                                reviews_average_text.split()[0].replace(
                                    ',', '.').strip())
                        else:
                            business.reviews_average = None
                    else:
                        business.reviews_average = None

                    business_list.business_list.append(business)
                except Exception as e:
                    logging.error(
                        f'Error occurred while scraping listing: {e}')

            await browser.close()
            return business_list

        except Exception as e:
            logging.error(f'Error occurred during scraping: {e}')
            await browser.close()
            return BusinessList()


async def get_agent_plan(user_input: str):
    """Processes user input using the LLM to determine intent and extract parameters."""
    planned_calls = []
    try:
        chat = model.start_chat()
        prompt = f"""Analyze the following user request for lead generation. Determine the required actions (search Google Maps, send WhatsApp message, or both). Extract all necessary parameters for the corresponding functions.

        User Request: "{user_input}"

        Based on the request, identify the function(s) to call and the arguments for each. If the user wants to send a message based on search results, first call 'search_Maps' and then 'prepare_whatsapp_message'. If they only want to send a message to specific numbers, only call 'prepare_whatsapp_message' with the 'target_numbers'. If they only want to search, only call 'search_Maps'.
        """
        response = chat.send_message(prompt)

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    call = part.function_call
                    function_name = call.name
                    args = {key: value for key, value in call.args.items()}

                    if function_name == "search_Maps" and "num_results" not in args:
                        args["num_results"] = 20

                    planned_calls.append({
                        "function_name": function_name,
                        "args": args
                    })

        return planned_calls, response.text

    except Exception as e:
        st.error(f"An error occurred during LLM interaction: {e}")
        return [], str(e)

async def main():
    st.title("AI-Powered Lead Generation Assistant")

    st.text("By Shakib Absar")
    st.markdown("---")

    st.markdown(
        """
    <p style="font-size: 13px;color: aqua;">Enter your request in natural language. Examples:</p>
    <ul>
        <li>"Find cafes in Islamabad and send the first 5 this message: 'Hello! We have a special offer today.'"</li>
        <li>"Show me barber shops in Malakand, maybe 10 of them."</li>
        <li>"Send 'Meeting reminder for tomorrow at 10 AM' to +923001234567 and +923339876543"</li>
    </ul>
    """,
        unsafe_allow_html=True,
    )

    user_input = st.text_area(
        "Enter your request",
        placeholder="e.g., Find cafes in Islamabad and send them a promotional message"
    )

    if st.button("Process Request"):
        if not user_input:
            st.error("Please enter your request")
        else:
            with st.spinner("Analyzing your request..."):
                planned_calls, llm_response = await get_agent_plan(user_input)
                
                if planned_calls:
                    st.success("Request analyzed successfully!")
                    st.json(planned_calls)
                    
                    # Process each planned call
                    for call in planned_calls:
                        if call["function_name"] == "search_Maps":
                            with st.spinner("Searching Google Maps..."):
                                business_list = await scrape_business(
                                    call["args"]["query"],
                                    call["args"].get("num_results", 20)
                                )
                                
                                if business_list.business_list:
                                    st.success(f"Found {len(business_list.business_list)} results!")
                                    st.dataframe(business_list.dataframe())
                                    
                                    # Save results
                                    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                    search_for_filename = call["args"]["query"].replace(' ', '_')
                                    excel_filename = f"({len(business_list.business_list)}_Rows)__{current_datetime}__({search_for_filename})"
                                    
                                    excel_file_path = business_list.save_to_excel(excel_filename)
                                    if excel_file_path:
                                        st.download_button(
                                            label="Download Results",
                                            data=open(excel_file_path, 'rb').read(),
                                            file_name=f"{excel_filename}.xlsx",
                                            mime="application/octet-stream"
                                        )
                        elif call["function_name"] == "prepare_whatsapp_message":
                            st.info("WhatsApp Message Prepared:")
                            st.write(f"Message: {call['args']['message']}")
                            if "k" in call["args"]:
                                st.write(f"Number of recipients: {call['args']['k']}")
                            if "target_numbers" in call["args"]:
                                st.write("Target numbers:", call["args"]["target_numbers"])
                else:
                    st.info("LLM Response:")
                    st.write(llm_response)

if __name__ == "__main__":
    asyncio.run(main())
