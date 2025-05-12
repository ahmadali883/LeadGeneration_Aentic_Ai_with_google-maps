# Google Maps Business Scraper

A Streamlit-based web application that scrapes business information from Google Maps using Playwright for browser automation.

## Features

- Search for businesses by location and type
- Extract detailed business information including:
  - Business name
  - Address
  - Website
  - Phone number
  - Reviews average rating
- Export data to Excel format
- User-friendly web interface
- Real-time progress tracking

## Workflow

### 1. User Input Process

The application accepts two main inputs from users:

1. **Search Term**
   - Format: "Business Type in Location"
   - Examples:
     - "Coffee Shops in New York"
     - "Restaurants in London"
     - "Barber Shops in Tokyo"
   - The search term is used to query Google Maps

2. **Number of Results**
   - Range: 1-1000 businesses
   - Default: 30 results
   - Determines how many business listings to scrape

### 2. Data Collection Process

When the user clicks "Get Data", the following process occurs:

1. **Browser Initialization**
   - Launches a headless Chrome browser using Playwright
   - Navigates to Google Maps

2. **Search Execution**
   - Enters the search term in Google Maps search box
   - Waits for results to load
   - Scrolls through results to collect the specified number of listings

3. **Data Extraction**
   For each business listing, the scraper:
   - Clicks on the listing to open details
   - Extracts information using specific selectors:
     - Name: `h1.DUwDvf.lfPIob`
     - Address: `//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]`
     - Website: `//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]`
     - Phone: `//button[contains(@data-item-id, "phone")]//div[contains(@class, "fontBodyMedium")]`
     - Reviews: `//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]`

### 3. Data Processing

1. **Data Structure**
   - Each business is stored as a `Business` dataclass object
   - Contains fields for name, address, website, phone, and reviews
   - Objects are collected in a `BusinessList` container

2. **Data Transformation**
   - Converts business objects to pandas DataFrame
   - Handles missing data and formatting

### 4. Output Generation

1. **File Creation**
   - Generates Excel file with naming convention:
     `(Number_of_Rows)__DateTime__(Search_Term).xlsx`
   - Example: `(30_Rows)__20240315_123456__(Coffee_Shops_New_York).xlsx`

2. **User Interface Updates**
   - Displays success message
   - Shows download button for Excel file
   - Presents data in interactive table
   - Shows elapsed time

## Technical Implementation

### Key Components

1. **Business Class**
   ```python
   @dataclass
   class Business:
       name: str = None
       address: str = None
       website: str = None
       phone_number: str = None
       reviews_average: float = None
   ```

2. **BusinessList Class**
   - Manages collection of Business objects
   - Handles data export to Excel/CSV
   - Provides DataFrame conversion

3. **Scraping Function**
   - Uses Playwright for browser automation
   - Implements scrolling and pagination
   - Handles dynamic content loading

### Error Handling

- Graceful handling of:
  - Network issues
  - Missing data
  - Browser automation failures
  - File saving errors

## Setup and Installation

1. **Prerequisites**
   - Python 3.7+
   - pip package manager

2. **Installation**
   ```bash
   # Clone the repository
   git clone [repository-url]

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Install Playwright browsers
   playwright install
   ```

3. **Running the Application**
   ```bash
   streamlit run main_setVal.py
   ```

## Dependencies

- streamlit: Web interface
- playwright: Browser automation
- pandas: Data manipulation
- openpyxl: Excel file handling
- python-dotenv: Environment variable management

## Notes

- The application requires an active internet connection
- Google Maps may have rate limits or restrictions
- Some businesses may have incomplete information
- The scraping speed depends on network conditions and the number of results requested

## Contributing

Feel free to submit issues and enhancement requests!
