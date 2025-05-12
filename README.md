# Google Maps Scraper with WhatsApp Automation

A powerful Streamlit web application that combines Google Maps business data scraping with automated WhatsApp messaging capabilities. This tool helps businesses and marketers find potential leads and engage with them through WhatsApp.

## 🌟 Features

- **Google Maps Scraping**
  - Search for businesses based on location and type
  - Extract business details including:
    - Business name
    - Address
    - Phone numbers
    - Website
    - Reviews and ratings
  - Export data to Excel/CSV formats

- **WhatsApp Automation**
  - Send messages to multiple contacts
  - Support for bulk messaging
  - Automatic phone number formatting
  - Message delivery status tracking
  - Rate limiting to prevent blocking

- **AI-Powered Interface**
  - Natural language processing for search queries
  - Smart message preparation
  - Intelligent lead selection
  - User-friendly Streamlit interface

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- WhatsApp Web/Desktop installed and logged in
- Google API Key (for Gemini AI features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Google-Map-Scrapper-Streamlit-Web.git
cd Google-Map-Scrapper-Streamlit-Web
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Create a `.env` file in the project root and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run main_setVal.py
```

2. Open your browser and navigate to the provided local URL (typically http://localhost:8501)

## 💡 Usage

### Searching for Businesses

1. Enter your search query in natural language (e.g., "Find cafes in Islamabad")
2. Specify the number of results you want
3. View the results in the interactive table
4. Download the data in Excel or CSV format

### Sending WhatsApp Messages

1. Prepare your message content
2. Choose recipients:
   - Direct phone numbers
   - Results from a search
   - Specific number of leads from search results
3. Ensure WhatsApp Web is open and logged in
4. Send messages and monitor delivery status

## ⚙️ Configuration

The application can be configured through various parameters:

- `MESSAGE_INTERVAL`: Delay between messages (default: 15 seconds)
- `PYWHATKIT_WAIT_TIME`: Wait time for WhatsApp Web (default: 25 seconds)
- `MAX_RETRIES`: Maximum retry attempts for failed messages
- `DEFAULT_COUNTRY_CODE`: Default country code for phone numbers

## 🔒 Security and Privacy

- API keys are stored in environment variables
- Phone numbers are validated and formatted securely
- Rate limiting prevents abuse
- No data is stored permanently

## 🛠️ Technical Details

### Key Technologies

- **Streamlit**: Web interface
- **Playwright**: Browser automation
- **Pandas**: Data handling
- **Google Gemini AI**: Natural language processing
- **PyWhatKit**: WhatsApp automation
- **Python-dotenv**: Environment management

### Project Structure

```
├── main_setVal.py          # Main application file
├── requirements.txt        # Python dependencies
├── packages.txt           # System dependencies
├── .env                   # Environment variables
├── output/               # Exported data directory
└── venv/                 # Virtual environment
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Important Notes

- Always ensure WhatsApp Web is open and logged in before sending messages
- Respect WhatsApp's terms of service and rate limits
- Use the tool responsibly and ethically
- Keep your API keys secure

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Shakib Absar** - *Initial work*

## 🙏 Acknowledgments

- Google Maps API
- WhatsApp Web
- Streamlit community
- All contributors and users

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ by Shakib Absar
