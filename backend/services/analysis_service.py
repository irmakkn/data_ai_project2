import pandas as pd
import io
import json
import requests
import sys
import os

# --- 1. LLM YARDIMCI FONKSİYONLARI ---
def call_ollama_internal(prompt: str):
    """Ollama API ile iletişim kurar."""
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
    except:
        return "{}"

def run_universal_analysis_internal(df, profile):
    """Verinin DNA'sına göre strateji ve TO-DO List oluşturur."""
    sample = df.head(5).to_dict(orient="records")
    
    prompt = f"""
    You are a Senior Data Strategist.
    DATA DNA: TimeSeries={profile['is_time_series']}, Outliers={profile['has_outliers']} (Rate: {profile.get('outlier_percentage', 0):.2f}%).
    SAMPLE DATA: {json.dumps(sample)}

    TASK:
    1. Analyze the mathematical patterns.
    2. Provide a 'todo_list' for the business owner (Actionable steps).
    3. Provide an 'executive_summary' and 'strategic_advice'.

    Return ONLY a JSON object with: 
    'executive_summary', 'mathematical_findings', 'strategic_advice', 'todo_list' (list of strings).
    """
    
    res = call_ollama_internal(prompt)
    try:
        # JSON string'i temizleyip objeye çevir
        start = res.find("{")
        end = res.rfind("}") + 1
        return json.loads(res[start:end])
    except:
        return {
            "executive_summary": "Analiz tamamlandı.",
            "todo_list": ["Veri kalitesini kontrol et", "Anomali tespiti yap"]
        }

# --- 2. GÜVENLİ İMPORTLAR ---
try:
    from backend.llm.sector_llm import run_sector_detection
    from backend.services.profiler_service import profile_dataset
    from backend.analysis_stat.stat_engine import StatEngine
except ImportError:
    from llm.sector_llm import run_sector_detection
    from services.profiler_service import profile_dataset
    from analysis_stat.stat_engine import StatEngine

# --- 3. ANA SERVİS FONKSİYONU ---
def process_analysis_request(file_content: bytes, file_name: str):
    """
    Sektör tespiti + Matematiksel DNA + Aksiyon Planı (To-Do)
    """
    response_payload = {
        "status": "pending",
        "file_info": {"name": file_name},
        "mathematical_profile": {},
        "sector_analysis": {},
        "insight_report": {},
        "execution_logs": []
    }

    try:
        # 1. DOSYA YÜKLEME
        if file_name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_content))
        else:
            df = pd.read_excel(io.BytesIO(file_content))

        if df.empty:
            raise ValueError("Veri seti boş.")

        # 2. ADIM: MATEMATİKSEL PROFIL (DNA)
        # Sektöre sormadan verinin tipini (Zaman serisi mi, anomali mi?) belirler.
        data_profile = profile_dataset(df)
        response_payload["mathematical_profile"] = data_profile

        # 3. ADIM: SEKTÖR TESPİTİ
        sector_info = run_sector_detection(df)
        response_payload["sector_analysis"] = {
            "detected_sector": sector_info.get("sector", "generic"),
            "reason": sector_info.get("reason", "")
        }

        # 4. ADIM: STRATEJİK RAPOR VE TO-DO LIST (İçerideki fonksiyondan)
        response_payload["insight_report"] = run_universal_analysis_internal(df, data_profile)

        # 5. ADIM: STATENGINE (Otomatik İşleme)
        engine = StatEngine()
        raw_config = sector_info.get("llm_json_output", {})
        analysis_config = json.loads(raw_config) if isinstance(raw_config, str) else raw_config
        
        processed_df, logs = engine.execute_pipeline(df, analysis_config)
        
        # 6. SONUÇLARIN PAKETLENMESİ
        response_payload["status"] = "success"
        response_payload["data_preview"] = processed_df.head(10).to_dict(orient="records")
        response_payload["summary_stats"] = processed_df.describe().to_dict()
        response_payload["execution_logs"] = logs

        return response_payload

    except Exception as e:
        return {"status": "error", "message": f"Sistem hatası: {str(e)}"}
