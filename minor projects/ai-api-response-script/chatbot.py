import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)


class chatbot:
    def __init__(self, model_name):
        self.model = genai.GenerativeModel(model_name)
    
    def ask(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text