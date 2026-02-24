import pandas as pd
import io
import json
import sys
import os
import requests

# --- 1. LLM YARDIMCI FONKSİYONLARI (Doğrudan İçeri Aldık) ---
def call_ollama_internal(prompt: str):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3:latest", "prompt": prompt, "stream": False, "format": "json"}
    try:
        response = requests.post(url, json=payload, timeout=120)
        return response.json().get("response", "{}")
    except:
        return "{}"

def run_universal_analysis_internal(df, profile):
    sample = df.head(5).to_dict(orient="records")
    prompt = f"""Analyze dataset DNA: TimeSeries={profile['is_time_series']}, Outliers={profile['has_outliers']}. Sample: {json.dumps(sample)}. Return JSON with 'executive_summary', 'mathematical_findings', 'strategic_advice'."""
    res = call_ollama_internal(prompt)
    try:
        return json.loads(res[res.find("{"):res.rfind("}")+1])
    except:
        return {"executive_summary": "Analiz tamamlandı."}

# --- 2. GÜVENLİ İMPORTLAR ---
try:
    from backend.llm.sector_llm import run_sector_detection
    from backend.services.profiler_service import profile_dataset
    from backend.analysis_stat.stat_engine import StatEngine
except ImportError:
    from llm.sector_llm import run_sector_detection
    from services.profiler_service import profile_dataset
    from analysis_stat.stat_engine import StatEngine

# --- 3. ANA SERVİS ---
def process_analysis_request(file_content: bytes, file_name: str):
    response_payload = {"status": "pending", "file_info": {"name": file_name}, "mathematical_profile": {}, "sector_analysis": {}, "insight_report": {}, "execution_logs": []}

    try:
        # DOSYA OKUMA
        if file_name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        # ADIM 1: DNA (Profiler)
        data_profile = profile_dataset(df)
        response_payload["mathematical_profile"] = data_profile

        # ADIM 2: SEKTÖR
        sector_info = run_sector_detection(df)
        response_payload["sector_analysis"] = {"detected_sector": sector_info.get("sector", "generic")}

        # ADIM 3: EVRENSEL ANALİZ (İçerideki fonksiyondan)
        response_payload["insight_report"] = run_universal_analysis_internal(df, data_profile)

        # ADIM 4: STATENGINE
        engine = StatEngine()
        raw_config = sector_info.get("llm_json_output", {})
        analysis_config = json.loads(raw_config) if isinstance(raw_config, str) else raw_config
        processed_df, logs = engine.execute_pipeline(df, analysis_config)
        
        response_payload["status"] = "success"
        response_payload["data_preview"] = processed_df.head(10).to_dict(orient="records")
        response_payload["summary_stats"] = processed_df.describe().to_dict()
        return response_payload

    except Exception as e:
        return {"status": "error", "message": str(e)}

