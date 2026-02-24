import pandas as pd
import json
import sys
import os
import requests

# Path koruması
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Uzmanları içe aktar
from .finance_llm import run_finance_analysis
from .healthcare_llm import run_healthcare_analysis
from .retail_llm import run_retail_analysis
from .generic_llm import run_generic_analysis

def run_sector_detection(df: pd.DataFrame):
    """
    Kural tabanlı değil, LLM tabanlı sektör tespiti yapar.
    """
    column_info = list(df.columns)
    sample_data = df.head(3).to_dict(orient="records")
    
    # --- ROUTER PROMPT ---
    router_prompt = f"""
    Analyze the following dataset columns and sample data. 
    Determine which sector this data belongs to: 'finance', 'healthcare', 'retail', or 'generic'.

    Columns: {column_info}
    Sample Data: {sample_data}

    Return ONLY a JSON object with two keys:
    1. "sector": (one of the four choices above)
    2. "reason": (a brief sentence explaining why)
    """

    try:
        # LLM'e soruyoruz: "Bu veri ne verisi?"
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": router_prompt,
                "stream": False,
                "format": "json"
            },
            timeout=30
        )
        
        router_output = json.loads(response.json()["response"])
        detected_sector = router_output.get("sector", "generic").lower()
        reason = router_output.get("reason", "No reason provided.")
        
        print(f"--- LLM KARARI ---")
        print(f"Tespit Edilen Sektör: {detected_sector}")
        print(f"Neden: {reason}")

        # Karara göre ilgili uzmana yönlendir
        if detected_sector == "finance":
            analysis = run_finance_analysis(df)
        elif detected_sector == "healthcare":
            analysis = run_healthcare_analysis(df)
        elif detected_sector == "retail":
            analysis = run_retail_analysis(df)
        else:
            analysis = run_generic_analysis(df)

        return {
            "sector": detected_sector,
            "reason": reason,
            "llm_json_output": analysis
        }

    except Exception as e:
        print(f"Router Hatası: {e}")
        return {"sector": "generic", "reason": "Error in routing", "llm_json_output": {}}