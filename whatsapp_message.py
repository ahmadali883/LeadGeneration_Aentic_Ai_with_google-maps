import pywhatkit
import time
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Parameters ---
target_phone_number = "+923348958772"  # The number you want to send to
message_content = f"This is a test message sent via pywhatkit at {time.strftime('%Y-%m-%d %H:%M:%S')}"
wait_time_seconds = 25  # How long to wait for WhatsApp Web to load (increase if needed)
# --- End Parameters ---

logging.info(f"Attempting to send WhatsApp message to: {target_phone_number}")
logging.info(f"Message: {message_content}")
logging.info(f"Waiting {wait_time_seconds} seconds for WhatsApp Web/Desktop...")
logging.info("Ensure WhatsApp Web or Desktop is open and logged in.")

try:
    pywhatkit.sendwhatmsg_instantly(
        phone_no=target_phone_number,
        message=message_content,
        wait_time=wait_time_seconds,
        tab_close=True,      # Close the browser tab after sending
        close_time=3         # Seconds to wait before closing tab
    )
    logging.info("pywhatkit function completed. Please check WhatsApp manually to confirm sending.")
    print("\nSUCCESS: pywhatkit function executed without error. Check WhatsApp.")

except Exception as e:
    error_type = type(e).__name__
    logging.error(f"An error occurred: {error_type} - {e}")
    print(f"\nERROR: Failed to send message. Error Type: {error_type}")
    print(f"Error Details: {e}")
    print("\nTroubleshooting Tips:")
    print("- Is WhatsApp Web or Desktop open and logged in?")
    print("- Is your phone connected to the internet?")
    print("- Is the phone number format correct (e.g., +923348958772)?")
    print(f"- Try increasing the 'wait_time_seconds' variable (currently {wait_time_seconds})?")