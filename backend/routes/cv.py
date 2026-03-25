from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import anthropic
import os
import json

router = APIRouter()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

NAZU_SYSTEM_PROMPT = """Anda adalah "Nazu AI Career Specialist", pakar rekrutmen profesional dan spesialis ATS (Applicant Tracking System).

TUGAS: Bantu user membuat CV profesional yang ATS-optimized, humanis, empiris, sistematis, dan logis.

WORKFLOW 3 TAHAP WAJIB:

## 1. DATA EXTRACTION (The Parser)
Ekstrak dari input user ke kategori:
- Identitas (nama, email, HP, kota, LinkedIn, portfolio)
- Ringkasan profesional (target posisi, tahun pengalaman, keahlian utama)
- Pengalaman kerja (perusahaan, posisi, periode, deskripsi tugas)
- Pendidikan (institusi, jurusan, gelar, tahun lulus, IPK)
- Skill (hard skills & soft skills)
- Sertifikasi (nama, lembaga, tahun)

## 2. CONTENT EXPANSION (The Humanizer)
- Gunakan Action Verbs kuat: Mempelopori, Mengoptimalkan, Mengintegrasikan, Memimpin, Merancang, Mengembangkan, Meningkatkan, Mengelola, Mengkoordinasikan, Mengimplementasikan
- Setiap poin HARUS berorientasi hasil terukur: "Meningkatkan efisiensi operasional sebesar 15%", "Mengelola tim 8 orang"
- SEO-optimized dengan keyword industri namun tetap humanis
- Minimum 3 bullet per pengalaman kerja

## 3. ATS OPTIMIZATION (The Auditor)
- Header WAJIB: Professional Summary, Work Experience, Education, Skills, Certifications
- NO graphics, NO bar rating, NO tabel — hanya teks bersih
- Gunakan keyword industri yang relevan
- Format konsisten dan mudah dibaca parser ATS

## OUTPUT FORMAT WAJIB (JSON):
Selalu kembalikan response dalam format JSON berikut:
{
  "message": "Pesan ramah kepada user menjelaskan apa yang telah diproses dan saran perbaikan",
  "cv_data": {
    "name": "",
    "target_position": "",
    "email": "",
    "phone": "",
    "city": "",
    "linkedin": "",
    "portfolio": "",
    "professional_summary": "",
    "work_experience": [
      {
        "position": "",
        "company": "",
        "period": "",
        "achievements": ["", "", ""]
      }
    ],
    "education": [
      {
        "degree": "",
        "major": "",
        "institution": "",
        "year": "",
        "gpa": ""
      }
    ],
    "skills": [""],
    "certifications": [
      {
        "name": "",
        "issuer": "",
        "year": ""
      }
    ]
  },
  "suggestions": ["Saran spesifik 1", "Saran spesifik 2"],
  "missing_fields": ["Field yang belum diisi"],
  "ats_tips": ["Tip ATS spesifik"]
}

Jika ada field yang kosong karena user belum memberikan data, isi dengan string kosong "" atau array kosong [].
Jangan pernah mengembalikan response di luar format JSON ini.
Selalu gunakan Bahasa Indonesia untuk message, suggestions, dan ats_tips."""

class CVRequest(BaseModel):
    user_input: str
    existing_cv: Optional[dict] = None
    conversation_history: Optional[List[dict]] = []

class ATSRequest(BaseModel):
    cv_data: dict
    job_description: str

class GeneratePDFRequest(BaseModel):
    cv_data: dict
    template: Optional[str] = "modern"

@router.post("/process")
async def process_cv(request: CVRequest):
    try:
        messages = request.conversation_history[-6:] if request.conversation_history else []
        
        context = ""
        if request.existing_cv:
            context = f"\n\nData CV yang sudah ada (update jika ada informasi baru):\n{json.dumps(request.existing_cv, ensure_ascii=False)}"
        
        messages.append({
            "role": "user",
            "content": request.user_input + context
        })

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4000,
            system=NAZU_SYSTEM_PROMPT,
            messages=messages
        )

        raw = response.content[0].text.strip()
        
        # Clean JSON if wrapped in markdown
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        return {"success": True, "data": result}

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"AI response parsing error: {str(e)}")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/expand-description")
async def expand_description(data: dict):
    """Expand a short job description into professional ATS-optimized bullets"""
    try:
        prompt = f"""Kembangkan deskripsi pekerjaan singkat ini menjadi 3-5 bullet point profesional yang:
- Menggunakan Action Verbs kuat
- Berorientasi hasil terukur (dengan estimasi metrik yang masuk akal)
- ATS-optimized dengan keyword industri

Posisi: {data.get('position', '')}
Perusahaan: {data.get('company', '')}
Industri: {data.get('industry', 'Umum')}
Deskripsi singkat: {data.get('description', '')}

Kembalikan HANYA JSON array of strings: ["bullet 1", "bullet 2", "bullet 3"]"""

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        bullets = json.loads(raw.strip())
        return {"success": True, "bullets": bullets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-summary")
async def generate_summary(data: dict):
    """Generate professional summary from CV data"""
    try:
        prompt = f"""Buat Professional Summary yang kuat (2-3 kalimat) berdasarkan data berikut.
Summary harus: menyebutkan posisi target, tahun pengalaman, keahlian utama, dan nilai yang ditawarkan.

Data: {json.dumps(data, ensure_ascii=False)}

Kembalikan HANYA string summary, bukan JSON."""

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"success": True, "summary": response.content[0].text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))