from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import google.generativeai as genai
import os
import json

router = APIRouter()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

NAZU_SYSTEM_PROMPT = """You are "Nazu AI Career Specialist", a professional recruitment expert and ATS (Applicant Tracking System) specialist.

TASK: Help users build professional, ATS-optimized, humanistic, empirical, systematic, and logical CVs.

3-STAGE MANDATORY WORKFLOW:

## 1. DATA EXTRACTION (The Parser)
Extract from user input into categories:
- Identity (name, email, phone, city, LinkedIn, portfolio)
- Professional summary (target position, years of experience, key expertise)
- Work experience (company, position, period, job description)
- Education (institution, major, degree, graduation year, GPA)
- Skills (hard skills & soft skills)
- Certifications (name, organization, year)

## 2. CONTENT EXPANSION (The Humanizer)
- Use strong Action Verbs: Led, Pioneered, Optimized, Integrated, Designed, Developed, Increased, Managed, Coordinated, Implemented
- Every bullet MUST be results-oriented with measurable outcomes: "Increased operational efficiency by 15%", "Managed a team of 8"
- SEO-optimized with industry keywords while remaining humanistic
- Minimum 3 bullets per work experience

## 3. ATS OPTIMIZATION (The Auditor)
- MANDATORY headers: Professional Summary, Work Experience, Education, Skills, Certifications
- NO graphics, NO bar ratings, NO tables — clean text only
- Use relevant industry keywords
- Consistent format, easy for ATS parsers to read

## LANGUAGE RULES (CRITICAL):
- If the user's input or instructions specify a language (English or Bahasa Indonesia), ALL generated CV content (descriptions, summaries, achievements, bullet points) MUST be written in that language.
- If the user says "Generate in English" or includes "English" language instruction → use English for all content.
- If the user says "Generate in Bahasa Indonesia" or includes "Indonesia" instruction → use Bahasa Indonesia for all content.
- Default to English if no language specified.
- Proper nouns, company names, technical terms, and internationally recognized acronyms may stay in their original form.

## MANDATORY OUTPUT FORMAT (JSON):
Always return response in this exact JSON format:
{
  "message": "A friendly message to the user explaining what was processed and improvement suggestions",
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
  "suggestions": ["Specific suggestion 1", "Specific suggestion 2"],
  "missing_fields": ["Fields not yet filled"],
  "ats_tips": ["Specific ATS tip"]
}

If a field is empty because user hasn't provided data, fill with empty string "" or empty array [].
NEVER return a response outside this JSON format."""


class CVRequest(BaseModel):
    user_input: str
    existing_cv: Optional[dict] = None
    conversation_history: Optional[List[dict]] = []


class GenerateSummaryRequest(BaseModel):
    name: Optional[str] = ""
    target_position: Optional[str] = ""
    professional_summary: Optional[str] = ""
    work_experience: Optional[list] = []
    education: Optional[list] = []
    skills: Optional[list] = []
    certifications: Optional[list] = []
    email: Optional[str] = ""
    phone: Optional[str] = ""
    city: Optional[str] = ""
    linkedin: Optional[str] = ""
    portfolio: Optional[str] = ""
    _lang_note: Optional[str] = ""


@router.post("/process")
async def process_cv(request: CVRequest):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-latest",
            system_instruction=NAZU_SYSTEM_PROMPT
        )

        context = ""
        if request.existing_cv:
            context = f"\n\nExisting CV data (update if new info is provided):\n{json.dumps(request.existing_cv, ensure_ascii=False)}"

        history_text = ""
        if request.conversation_history:
            history_text = "\n\nPrevious conversation:\n"
            for msg in request.conversation_history[-6:]:
                history_text += f"{msg['role']}: {msg['content']}\n"

        final_prompt = f"{history_text}\n\nCurrent User Input: {request.user_input}{context}"

        response = model.generate_content(
            final_prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        return {"success": True, "data": result}

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"AI response parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini service error: {str(e)}")


@router.post("/expand-description")
async def expand_description(data: dict):
    """Expand a short job description into professional ATS-optimized bullets"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Extract language instruction if present in description
        description = data.get('description', '')
        lang_note = ""
        if "Generate the bullet points in BAHASA INDONESIA" in description:
            lang_note = "IMPORTANT: Write ALL bullet points in Bahasa Indonesia."
            description = description.replace("Generate the bullet points in BAHASA INDONESIA.", "").strip()
        elif "Generate the bullet points in ENGLISH" in description:
            lang_note = "IMPORTANT: Write ALL bullet points in English."
            description = description.replace("Generate the bullet points in ENGLISH.", "").strip()

        prompt = f"""Expand this short job description into 3-5 professional bullet points that:
- Use strong Action Verbs
- Are results-oriented with measurable outcomes (with reasonable metric estimates)
- Are ATS-optimized with industry keywords
{lang_note}

Position: {data.get('position', '')}
Company: {data.get('company', '')}
Industry: {data.get('industry', 'General')}
Short description: {description}

Return ONLY a JSON array of strings: ["bullet 1", "bullet 2", "bullet 3"]"""

        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        bullets = json.loads(raw)
        return {"success": True, "bullets": bullets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-summary")
async def generate_summary(data: dict):
    """Generate professional summary from CV data"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        lang_note = data.get('_lang_note', '') or ''
        if 'Generate in Bahasa Indonesia' in lang_note:
            lang_instruction = "Write the summary in Bahasa Indonesia."
        else:
            lang_instruction = "Write the summary in English."

        prompt = f"""Create a strong Professional Summary (2-3 sentences) based on the following data.
The summary must: mention target position, years of experience, key expertise, and value offered.
{lang_instruction}

Data: {json.dumps({k: v for k, v in data.items() if k != '_lang_note'}, ensure_ascii=False)}

Return ONLY the summary string, not JSON."""

        response = model.generate_content(prompt)
        return {"success": True, "summary": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))