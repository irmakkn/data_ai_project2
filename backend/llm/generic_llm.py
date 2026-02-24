import requests
import json
import sys
import os

# Path koruması (isteğe bağlı ama güvenli)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def run_generic_analysis(df):
    """
    Sektörü belirlenemeyen veriler için genel analiz yapar.
    """
    rows, cols = df.shape
    column_names = list(df.columns)
    
    prompt = f"""
You are a general Data Analyst. Analyze this dataset.
Rows: {rows}
Columns: {column_names}

Return a valid JSON with:
1. "dataset_type": "General"
2. "cleaning_steps": ["General cleaning"]
3. "cleaning_code": "df = df.dropna()"
4. "visualization_suggestions": []
"""

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3:latest",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        result_text = response.json().get("response", "")
        
        # JSON temizleme ve döndürme
        start = result_text.find("{")
        end = result_text.rfind("}") + 1
        return result_text[start:end]
    except Exception as e:
        return json.dumps({"error": str(e)})
