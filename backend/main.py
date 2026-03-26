from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from routers import cv, ats, auth
# from routers import cv, ats, auth
app = FastAPI(
    title="Nazu AI Career Specialist API",
    description="Professional ATS-optimized CV builder powered by Claude AI",
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

app.mount("/static", StaticFiles(directory="../frontend/assets"), name="static")

@app.get("/")
async def root():
    return FileResponse("../frontend/pages/index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Nazu AI Career Specialist"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)