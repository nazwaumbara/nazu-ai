# Nazu AI — Career Specialist
### CV Builder Profesional Berbasis AI · ATS-Optimized · Powered by Claude

---

## Arsitektur Sistem

```
nazu-ai/
├── frontend/
│   ├── pages/
│   │   └── index.html          ← Single-page app (Hero + Builder + Features)
│   └── assets/
│       ├── css/                ← Global styles (sudah inline di HTML)
│       └── js/                 ← App logic (sudah inline di HTML)
│
├── backend/
│   ├── main.py                 ← FastAPI entrypoint
│   ├── requirements.txt        ← Python dependencies
│   ├── Dockerfile              ← Container config
│   └── routers/
│       ├── cv.py               ← CV processing & AI endpoints
│       ├── ats.py              ← ATS analysis & keyword extraction
│       └── auth.py             ← Auth (extensible)
│
├── docker-compose.yml          ← Full stack deployment
├── nginx.conf                  ← Reverse proxy config
├── .env.example                ← Environment template
└── README.md
```

---

## Tech Stack

| Layer | Teknologi | Fungsi |
|-------|-----------|--------|
| Frontend | HTML/CSS/JS (Vanilla) | UI profesional multi-section |
| Backend | Python + FastAPI | API, AI processing |
| AI Engine | Claude (claude-opus-4-5) | CV parsing, expansion, ATS |
| Proxy | Nginx | Serve frontend + proxy API |
| Deploy | Docker Compose | Orchestration |

---

## Cara Menjalankan

### 1. Development (Local)

```bash
# Clone & masuk folder
cd nazu-ai

# Setup environment
cp .env.example .env
# Edit .env dan isi ANTHROPIC_API_KEY

# Jalankan backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Buka frontend
# Buka frontend/pages/index.html di browser
# ATAU jalankan live server di VS Code
```

### 2. Docker Compose (Production)

```bash
# Setup env
cp .env.example .env
# Edit ANTHROPIC_API_KEY di .env

# Build & run
docker-compose up --build -d

# Akses:
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Health:   http://localhost:8000/health
```

---

## API Endpoints

### CV Builder
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | /api/cv/process | Proses narasi bebas → data CV terstruktur |
| POST | /api/cv/expand-description | Kembangkan deskripsi kerja singkat |
| POST | /api/cv/generate-summary | Generate professional summary |

### ATS Analysis
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | /api/ats/analyze | Analisis CV vs JD → skor + rekomendasi |
| POST | /api/ats/extract-keywords | Ekstrak keyword dari JD |
| POST | /api/ats/generate-cv-text | Export CV ke plain text ATS-friendly |

---

## Fitur Utama

### 🎯 AI-Powered Form Fill
Ceritakan pengalaman secara bebas → AI otomatis mengisi semua field form

### ✦ Content Expansion
Deskripsi kerja singkat → dikembangkan jadi 3-5 bullet profesional dengan action verbs & metrik

### 📊 ATS Score & Analysis
Upload Job Description → skor kecocokan, breakdown per kategori, keyword missing, rekomendasi

### 💡 Real-time Preview
Preview CV diperbarui otomatis saat mengisi form

### ⬇ Export
Download CV sebagai plain text (100% ATS-selectable) atau salin ke clipboard

---

## Pengembangan Lanjutan

- [ ] Database (PostgreSQL) untuk simpan CV user
- [ ] Auth (JWT) + dashboard history
- [ ] Export PDF dengan Puppeteer/WeasyPrint
- [ ] Multiple template CV
- [ ] LinkedIn scraper untuk auto-fill
- [ ] Email CV langsung ke rekruter