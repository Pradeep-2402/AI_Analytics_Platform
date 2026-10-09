import requests

MODEL_NAME = "phi3:mini"

def ask_ollama(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 250,
                "temperature": 0.2
            }
        },
        timeout=600
    )

    return response.json()["response"]