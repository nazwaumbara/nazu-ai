from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import file router (pastikan folder bernama 'routers' dan file-filenya sudah ada)
from routers import cv, ats, auth 

# 1. Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="CV Maker by Nazu API",
    description="Backend API untuk generate CV ATS-Friendly menggunakan AI",
    version="1.0.0"
)

# 2. Konfigurasi CORS (Sangat penting untuk Vercel / WebApp)
# Ini memberi izin agar tampilan HTML kamu bisa "ngobrol" dengan API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Di tahap awal biarkan "*", nanti bisa diganti domain Vercel kamu
    allow_credentials=True,
    allow_methods=["*"], # Mengizinkan semua metode (GET, POST, dll)
    allow_headers=["*"],
)

# 3. Mendaftarkan Rute (Endpoints)
# Menggabungkan logika AI dari folder routers ke dalam satu aplikasi utama
app.include_router(cv.router, prefix="/api/cv", tags=["CV Generation"])
app.include_router(ats.router, prefix="/api/ats", tags=["ATS Analysis"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# 4. Endpoint Dasar (Health Check)
# Untuk memastikan backend menyala saat kamu buka link API-nya di browser
@app.get("/")
async def root():
    return {
        "message": "Welcome to CV Maker by Nazu API!",
        "status": "Serverless Active",
        "docs": "/docs" # FastAPI otomatis membuatkan UI dokumentasi di sini
    }

# CATATAN UNTUK VERCEL:
# Tidak perlu ada blok `if __name__ == "__main__": uvicorn.run(...)` di bawah sini.
# Vercel akan otomatis mengenali variabel `app` di atas.