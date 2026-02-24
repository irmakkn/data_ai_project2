from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Bizim yazdığımız servis
from backend.services.analysis_service import process_analysis_request

app = FastAPI(title="LLM Powered Data Analysis API")

# --- CORS AYARLARI (Frontend ile iletişim için şart) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme aşamasında her yerden gelen isteğe izin ver
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-analysis")
async def upload_data(file: UploadFile = File(...)):
    """
    Dosyayı alır ve analiz sürecini başlatır.
    """
    try:
        # 1. Dosya içeriğini oku
        content = await file.read()
        
        # 2. Servis katmanını çağır
        result = process_analysis_request(content, file.filename)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu Hatası: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Data-AI Project API is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


