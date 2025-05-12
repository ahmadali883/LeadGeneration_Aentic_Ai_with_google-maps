import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('GOOGLE_API_KEY')

def test_gemini_text():
    """Test basic text generation with Gemini"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [{
                "parts": [{"text": "Write a short poem about artificial intelligence."}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== Text Generation Test ===")
            print("Response:", result)
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Error in text generation test: {e}")
        return False

def test_gemini_chat():
    """Test chat functionality with Gemini"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        messages = [
            "Hello! How are you?",
            "What can you tell me about machine learning?",
            "Thank you for the information!"
        ]
        
        print("\n=== Chat Test ===")
        for message in messages:
            data = {
                "contents": [{
                    "parts": [{"text": message}]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"\nUser: {message}")
                print(f"Assistant: {result}")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return False
        
        return True
    except Exception as e:
        print(f"Error in chat test: {e}")
        return False

def test_gemini_image():
    """Test image analysis with Gemini"""
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Test image path (you'll need to provide a valid image path)
        image_path = "test_image.jpg"
        
        if not os.path.exists(image_path):
            print(f"\nImage file not found: {image_path}")
            return False
        
        # Load and analyze image
        image = genai.upload_file(image_path)
        response = model.generate_content(["Describe this image in detail:", image])
        
        print("\n=== Image Analysis Test ===")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"Error in image analysis test: {e}")
        return False

def main():
    """Run all tests"""
    if not API_KEY:
        print("Error: GOOGLE_API_KEY not found in environment variables")
        return
        
    print("Starting Gemini API Tests...")
    
    # Run text generation test
    text_result = test_gemini_text()
    print(f"\nText Generation Test {'Passed' if text_result else 'Failed'}")
    
    # Run chat test
    chat_result = test_gemini_chat()
    print(f"\nChat Test {'Passed' if chat_result else 'Failed'}")
    
    # Run image analysis test
    image_result = test_gemini_image()
    print(f"\nImage Analysis Test {'Passed' if image_result else 'Failed'}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 