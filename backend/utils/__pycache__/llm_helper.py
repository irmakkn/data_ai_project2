import requests

def call_ollama(prompt, model="llama3:latest"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120
        )
        text = response.json()["response"]
        start, end = text.find("{"), text.rfind("}") + 1
        return text[start:end] if start != -1 else '{"error": "No JSON found"}'
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'