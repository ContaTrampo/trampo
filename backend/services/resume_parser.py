"""TRAMPO v8 — Parser de Currículo PDF
1. Extrai texto com pdfplumber
2. Regex para campos básicos
3. Groq (LLaMA 3, gratuito) para extração semântica
"""
from __future__ import annotations
import re, os, json


def extract_text_from_pdf(filepath: str) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            parts = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(parts).strip()
    except Exception as e:
        print(f"⚠️ pdfplumber falhou: {e}")
        try:
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                pages  = [p.extract_text() or "" for p in reader.pages]
            return "\n".join(pages).strip()
        except Exception as e2:
            print(f"⚠️ PyPDF2 também falhou: {e2}")
            return ""


def _extract_email(text: str) -> str | None:
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else None

def _extract_phone(text: str) -> str | None:
    m = re.search(r"(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[\-\s]?\d{4}", text)
    return m.group(0).strip() if m else None

def _extract_linkedin(text: str) -> str | None:
    m = re.search(r"linkedin\.com/in/[\w\-]+", text, re.IGNORECASE)
    return "https://" + m.group(0) if m else None

def _extract_github(text: str) -> str | None:
    m = re.search(r"github\.com/[\w\-]+", text, re.IGNORECASE)
    return "https://" + m.group(0) if m else None

def _extract_skills_regex(text: str) -> list[str]:
    known = [
        "Python","JavaScript","TypeScript","Java","C#","C++","Go","Rust","PHP","Ruby",
        "React","Vue","Angular","Next.js","HTML","CSS","Tailwind","Node.js",
        "Django","Flask","FastAPI","Spring","Laravel","Express",
        "PostgreSQL","MySQL","MongoDB","Redis","SQLite",
        "AWS","Azure","GCP","Docker","Kubernetes","Terraform","Git","Linux",
        "Machine Learning","TensorFlow","PyTorch","Pandas","NumPy",
        "Excel","Power BI","Tableau","Google Analytics","SEO","Google Ads","Meta Ads",
        "Figma","Photoshop","Canva","Scrum","Agile","Jira",
    ]
    text_lower = text.lower()
    return [s for s in known if s.lower() in text_lower][:20]

def _extract_years_regex(text: str) -> int:
    for pat in [
        r"(\d+)\+?\s*anos?\s*de\s*experi[êe]ncia",
        r"experi[êe]ncia\s*de\s*(\d+)\+?\s*anos?",
        r"(\d+)\s*years?\s*of\s*experience",
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return min(int(m.group(1)), 40)
    return 0


def _extract_with_groq(text: str) -> dict:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("⚠️ GROQ_API_KEY não configurada — usando só regex")
        return {}

    text_truncated = text[:4000]

    prompt = f"""Analise este currículo em português e extraia as informações no formato JSON.
Responda APENAS com o JSON, sem explicações, sem markdown.

Currículo:
{text_truncated}

Retorne EXATAMENTE este JSON (preencha com null se não encontrar):
{{
  "nome": "Nome completo da pessoa",
  "cargo_atual": "Título do cargo mais recente ou pretendido",
  "anos_experiencia": 0,
  "resumo": "Resumo profissional em 2-3 frases",
  "skills": ["skill1", "skill2", "skill3"],
  "linkedin": "URL do LinkedIn ou null",
  "github": "URL do GitHub ou null",
  "telefone": "Telefone ou null",
  "cidade": "Cidade ou null",
  "estado": "UF de 2 letras ou null",
  "nivel": "junior ou mid ou senior ou lead"
}}"""

    try:
        import urllib.request
        payload = json.dumps({
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 800,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        content = data["choices"][0]["message"]["content"].strip()
        content = re.sub(r"```json|```", "", content).strip()
        parsed = json.loads(content)
        print(f"✅ Groq extraiu: cargo={parsed.get('cargo_atual')}, skills={len(parsed.get('skills', []))}")
        return parsed

    except Exception as e:
        print(f"⚠️ Groq falhou: {e}")
        return {}


def parse_resume(filepath: str) -> dict:
    text = extract_text_from_pdf(filepath)
    if not text:
        return {"text": "", "skills": [], "error": "Não foi possível extrair texto do PDF"}

    result = {
        "text":             text,
        "job_title":        None,
        "years_experience": _extract_years_regex(text),
        "skills":           _extract_skills_regex(text),
        "bio":              None,
        "linkedin_url":     _extract_linkedin(text),
        "github_url":       _extract_github(text),
        "phone":            _extract_phone(text),
        "email":            _extract_email(text),
        "seniority":        None,
        "cidade":           None,
        "estado":           None,
        "name":             None,
    }

    ai = _extract_with_groq(text)
    if ai:
        if ai.get("cargo_atual"):   result["job_title"]        = ai["cargo_atual"]
        if ai.get("anos_experiencia"): result["years_experience"] = int(ai["anos_experiencia"] or 0)
        if ai.get("skills") and len(ai["skills"]) > len(result["skills"]):
                                    result["skills"]           = ai["skills"][:20]
        if ai.get("resumo"):        result["bio"]              = ai["resumo"]
        if ai.get("linkedin") and not result["linkedin_url"]:
                                    result["linkedin_url"]     = ai["linkedin"]
        if ai.get("github") and not result["github_url"]:
                                    result["github_url"]       = ai["github"]
        if ai.get("telefone") and not result["phone"]:
                                    result["phone"]            = ai["telefone"]
        if ai.get("nivel"):         result["seniority"]        = ai["nivel"]
        if ai.get("cidade"):        result["cidade"]           = ai["cidade"]
        if ai.get("estado"):        result["estado"]           = ai["estado"]
        if ai.get("nome"):          result["name"]             = ai["nome"]

    return result
