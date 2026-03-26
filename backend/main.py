from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os

# Import router menggunakan path absolute
from backend.routers import cv, ats, auth

app = FastAPI(
    title="Nazu AI Career Specialist API",
    description="Professional ATS-optimized CV builder powered by Gemini AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv.router, prefix="/api/cv", tags=["CV Builder"])
app.include_router(ats.router, prefix="/api/ats", tags=["ATS Analysis"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

# PERINTAH APP.MOUNT STATIC FILES YANG BIKIN ERROR SUDAH DIHAPUS

@app.get("/")
async def root():
    # Menggunakan jalur absolut agar Python tidak tersesat mencari HTML di server Vercel
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(base_dir, "frontend", "pages", "index.html")
    
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "API Nazu AI Berjalan Sempurna!"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Nazu AI Career Specialist"}