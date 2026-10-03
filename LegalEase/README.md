# LegalEase — AI-Powered Legal Document Generator

LegalEase is a FastAPI + Streamlit application that generates editable legal-document drafts with Gemini and exports them as TXT, DOCX, or PDF.

> **Important:** LegalEase produces AI-generated drafts for informational and document-preparation purposes. It is not a substitute for advice from a qualified lawyer, and users should review jurisdiction-specific requirements before using a document.

## Architecture

```text
Streamlit UI
    │
    │ POST /generate
    ▼
FastAPI backend
    │
    ├── Pydantic validation
    │
    ├── GeminiDocumentGenerator
    │        │
    │        └── Google GenAI SDK → Gemini model
    │
    └── Export service
             ├── TXT
             ├── DOCX
             └── PDF
```

## Project structure

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py
│   └── services/
│       ├── __init__.py
│       └── document_formatter.py
├── frontend/
│   └── app.py
├── assets/
│   └── legal_ease_logo.png
├── tests/
│   ├── test_api.py
│   └── test_formatter.py
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- A Gemini API key
- VS Code
- Internet connection for Gemini generation

The PDF specification originally used `google-generativeai` and Gemini 1.5 Pro. This implementation uses Google's newer `google-genai` SDK. The Gemini model is configurable through `GEMINI_MODEL`.

## 1. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Configure Gemini

Copy:

```text
.env.example
```

to:

```text
.env
```

Then add your API key:

```env
GEMINI_API_KEY=your_real_api_key_here
GEMINI_MODEL=gemini-2.5-flash
BACKEND_URL=http://127.0.0.1:8000
```

Do not commit `.env`.

## 4. Start the FastAPI backend

Open Terminal 1:

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Check:

```text
http://127.0.0.1:8000/
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## 5. Start Streamlit

Open Terminal 2:

```powershell
streamlit run frontend/app.py
```

Streamlit normally opens:

```text
http://localhost:8501
```

## 6. Test the application

Example:

- Document Type: `Freelance Work Contract`
- Parties:
  `Jane Doe (Service Provider), TechNova Inc. (Client)`
- Terms:
  `Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice`
- Effective Date:
  `October 10, 2026`

Click **Generate Document**.

Then:

1. Review the generated text.
2. Click **Edit Document**.
3. Modify the text if necessary.
4. Download TXT, DOCX, or PDF.

## API example

```powershell
$body = @{
    document_type = "Non-Disclosure Agreement"
    parties = "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)"
    terms = "Confidential information must be protected; Disclosure is limited to authorized personnel"
    effective_date = "October 10, 2026"
    language = "English"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/generate `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## Run tests

```powershell
pytest -q
```

The tests cover validation, formatting, export generation, and the API health endpoint. Gemini generation itself requires a real API key and is intentionally not called by the unit tests.

## Docker

Build:

```powershell
docker build -t legalease .
```

Run:

```powershell
docker run --env-file .env -p 8000:8000 -p 8501:8501 legalease
```

For a production deployment, it is generally cleaner to deploy the FastAPI backend and Streamlit frontend as separate services.

## Security notes

- Keep `GEMINI_API_KEY` server-side.
- Never put the API key into Streamlit code sent to users.
- `.env` is ignored by Git.
- Do not log user legal documents unnecessarily.
- Treat generated documents as sensitive user data.
- Add authentication, rate limiting, encrypted storage, and audit logging before exposing the service publicly.

## Scope

The implementation follows the PDF's core workflow: document type, parties, terms, effective date, AI generation, editable preview, and TXT/DOCX/PDF export.
