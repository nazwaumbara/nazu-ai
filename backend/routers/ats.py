from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
import json

router = APIRouter()

# Konfigurasi Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class ATSRequest(BaseModel):
    cv_data: dict
    job_description: str

class KeywordsRequest(BaseModel):
    job_description: str

@router.post("/analyze")
async def analyze_ats(request: ATSRequest):
    """Full ATS analysis: score, keywords, recommendations"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""Kamu adalah ATS (Applicant Tracking System) expert. Analisis kecocokan CV ini dengan Job Description.

CV DATA:
{json.dumps(request.cv_data, ensure_ascii=False, indent=2)}

JOB DESCRIPTION:
{request.job_description}

Kembalikan HANYA JSON berikut (tidak ada teks lain):
{{
  "overall_score": 85,
  "breakdown": {{
    "keywords_match": 80,
    "experience_relevance": 90,
    "education_match": 85,
    "skills_match": 75,
    "format_score": 95
  }},
  "matched_keywords": ["keyword yang sudah ada di CV"],
  "missing_keywords": ["keyword penting yang belum ada di CV"],
  "recommendations": [
    "Rekomendasi spesifik 1",
    "Rekomendasi spesifik 2"
  ],
  "strengths": ["Kelebihan CV ini", "Kelebihan 2"],
  "weaknesses": ["Kelemahan yang perlu diperbaiki"],
  "verdict": "Sangat Cocok / Cukup Cocok / Perlu Perbaikan",
  "verdict_detail": "Penjelasan singkat verdict"
}}"""

        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw.strip())
        return {"success": True, "analysis": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-keywords")
async def extract_keywords(request: KeywordsRequest):
    """Extract important keywords from job description"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""Ekstrak keyword penting dari Job Description ini untuk keperluan ATS optimization.

JD: {request.job_description}

Kembalikan HANYA JSON:
{{
  "hard_skills": ["Python", "SQL", "..."],
  "soft_skills": ["Leadership", "Communication", "..."],
  "tools": ["Figma", "Jira", "..."],
  "qualifications": ["S1 Informatika", "..."],
  "industry_terms": ["Agile", "Scrum", "..."]
}}"""

        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw.strip())
        return {"success": True, "keywords": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-cv-text")
async def generate_cv_text(cv_data: dict):
    """Generate clean ATS-friendly plain text from CV data"""
    d = cv_data
    lines = []

    lines.append(d.get("name", "").upper())
    lines.append(d.get("target_position", ""))
    
    contacts = []
    for field in ["email", "phone", "city", "linkedin", "portfolio"]:
        val = d.get(field, "")
        if val:
            contacts.append(val)
    lines.append(" | ".join(contacts))
    lines.append("")

    if d.get("professional_summary"):
        lines.append("PROFESSIONAL SUMMARY")
        lines.append("-" * 40)
        lines.append(d["professional_summary"])
        lines.append("")

    if d.get("work_experience"):
        lines.append("WORK EXPERIENCE")
        lines.append("-" * 40)
        for exp in d["work_experience"]:
            lines.append(f"{exp.get('position', '')} — {exp.get('company', '')}")
            lines.append(exp.get("period", ""))
            for ach in exp.get("achievements", []):
                lines.append(f"• {ach}")
            lines.append("")

    if d.get("education"):
        lines.append("EDUCATION")
        lines.append("-" * 40)
        for edu in d["education"]:
            degree_line = f"{edu.get('degree', '')} {edu.get('major', '')}".strip()
            lines.append(degree_line)
            inst_line = edu.get("institution", "")
            if edu.get("year"):
                inst_line += f" | {edu['year']}"
            if edu.get("gpa"):
                inst_line += f" | IPK: {edu['gpa']}"
            lines.append(inst_line)
            lines.append("")

    if d.get("skills"):
        lines.append("SKILLS")
        lines.append("-" * 40)
        lines.append(", ".join(d["skills"]))
        lines.append("")

    if d.get("certifications"):
        lines.append("CERTIFICATIONS")
        lines.append("-" * 40)
        for cert in d["certifications"]:
            cert_line = cert.get("name", "")
            if cert.get("issuer"):
                cert_line += f" — {cert['issuer']}"
            if cert.get("year"):
                cert_line += f" ({cert['year']})"
            lines.append(f"• {cert_line}")

    return {"success": True, "cv_text": "\n".join(lines)}