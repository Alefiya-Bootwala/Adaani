import google.generativeai as genai
import os

# Configuration
API_KEY = "AIzaSyD4NED4XQobmNAojPg7wkNHEnA0q1DY98w"

# Initialize the API
genai.configure(api_key=API_KEY)

# List available models
available_models = list(genai.list_models())
print("Available models:")
for model_info in available_models:
    print(f"  - {model_info.name}")

# Create a model instance - using gemini-2.5-flash
model = genai.GenerativeModel("models/gemini-2.5-flash")

def chat_with_gemini(user_input):
    """Send a message to Gemini and get a response."""
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function to interact with Gemini."""
    print("Welcome to Gemini API Demo!")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        response = chat_with_gemini(user_input)
        print(f"Gemini: {response}\n")

if __name__ == "__main__":
    main()
