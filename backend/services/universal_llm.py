import pandas as pd
import requests
import json

def call_ollama(prompt: str):
    """Ollama ile iletişim kuran yardımcı fonksiyon"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3:latest",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        return response.json().get("response", "{}")
    except Exception as e:
        return json.dumps({"error": f"Ollama Connection Error: {str(e)}"})

def run_universal_analysis(df: pd.DataFrame, profile: dict):
    """
    Sektörden bağımsız, verinin matematiksel profiline göre analiz yapar.
    """
    # Veri örneğini hazırlayalım
    sample_data = df.head(5).to_dict(orient="records")
    
    prompt = f"""
    You are an Expert Data Scientist. Analyze this dataset using its STATISTICAL DNA.
    
    STATISTICAL PROFILE:
    - Time Series Characteristics: {profile.get('is_time_series', False)}
    - Outlier Detection: {profile.get('has_outliers', False)} (Percentage: {profile.get('outlier_percentage', 0):.2f}%)
    - High Correlations: {profile.get('key_correlations', [])}
    
    SAMPLE DATA:
    {json.dumps(sample_data)}

    YOUR GOAL:
    1. Interpret the 'Outlier Detection'. Are these anomalies risks (like fraud) or opportunities (like high-value customers)?
    2. If it's a 'Time Series', identify possible trends or seasonality.
    3. Based on 'High Correlations', suggest which variables drive the results.
    4. Provide a high-level Business Strategy.

    STRICT RULE: Return ONLY a JSON object with these keys:
    'executive_summary', 'mathematical_findings', 'strategic_advice', 'risk_score' (1-10)
    """

    analysis_raw = call_ollama(prompt)
    
    # JSON güvenliği için temizleme
    try:
        start = analysis_raw.find("{")
        end = analysis_raw.rfind("}") + 1
        return json.loads(analysis_raw[start:end])
    except:
        return {"error": "Analysis could not be parsed as JSON", "raw": analysis_raw}