import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Gemini API Limit Reached.\n\nError: {str(e)}"