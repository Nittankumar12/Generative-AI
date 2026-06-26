import json
from chatbot import Chatbot
from config import GEMINI_API_KEY, MODEL_NAME

chatbot = Chatbot(MODEL_NAME)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    response = chatbot.ask(user_input)
    print(f"Chatbot: {response}")

def load_history():
    try:
        with open("conversation/history.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    with open("conversation/history.json", "w") as f:
        json.dump(history, f, indent=4)

