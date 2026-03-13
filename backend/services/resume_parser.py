"""TRAMPO v7 — Parser de Currículo PDF
1. Extrai texto com pdfplumber
2. Tenta detectar campos com regex
3. Opcional: usa OpenAI para extração semântica
"""
from __future__ import annotations
import re
import os


# ── Extração de texto ─────────────────────────────────────────

def extract_text_from_pdf(filepath: str) -> str:
    """Extrai todo o texto de um PDF. Retorna string vazia se falhar."""
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


# ── Parsers por regex ─────────────────────────────────────────

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


def _extract_skills(text: str) -> list[str]:
    """Detecta skills conhecidas no texto."""
    known = [
        "Python","JavaScript","TypeScript","Java","C#","C++","Go","Rust","PHP","Ruby","Swift","Kotlin",
        "React","Vue","Angular","Next.js","Svelte","HTML","CSS","SASS","Tailwind",
        "Node.js","Django","Flask","FastAPI","Spring","Laravel","Rails","Express",
        "PostgreSQL","MySQL","MongoDB","Redis","Elasticsearch","SQLite","Oracle",
        "AWS","Azure","GCP","Docker","Kubernetes","Terraform","CI/CD","Jenkins","GitHub Actions",
        "Git","Linux","Bash","REST","GraphQL","gRPC","Kafka","RabbitMQ",
        "Machine Learning","Deep Learning","TensorFlow","PyTorch","Scikit-learn","Pandas","NumPy",
        "Excel","Power BI","Tableau","Google Analytics","SEO","Google Ads","Meta Ads",
        "Figma","Photoshop","Illustrator","After Effects","Canva",
        "Scrum","Agile","Kanban","Jira","Notion","Slack",
        "Vendas","Atendimento ao cliente","Gestão de projetos","Marketing Digital",
    ]
    found = []
    text_lower = text.lower()
    for skill in known:
        if skill.lower() in text_lower and skill not in found:
            found.append(skill)
    return found[:20]


def _extract_years_experience(text: str) -> int:
    """Tenta extrair anos de experiência."""
    patterns = [
        r"(\d+)\+?\s*anos?\s*de\s*experi[êe]ncia",
        r"experi[êe]ncia\s*de\s*(\d+)\+?\s*anos?",
        r"(\d+)\s*years?\s*of\s*experience",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return min(int(m.group(1)), 40)
    return 0


def _extract_job_title(text: str) -> str | None:
    """Extrai cargo/título profissional heurístico."""
    titles_pt = [
        "Desenvolvedor","Developer","Engenheiro","Engineer","Analista","Analyst",
        "Designer","Gerente","Manager","Coordenador","Coordinator","Diretor","Director",
        "Técnico","Technician","Especialista","Specialist","Consultor","Consultant",
        "Cientista de Dados","Data Scientist","Arquiteto","Architect",
        "Product Manager","Product Owner","Scrum Master","DevOps","SRE",
        "Vendedor","Representante Comercial","Assistente Administrativo",
    ]
    for title in titles_pt:
        pattern = rf"(?:cargo|título|position|role)?:?\s*({re.escape(title)}[^\n,;]*)"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:80]
    return None


def _extract_summary(text: str) -> str | None:
    """Extrai seção de resumo/objetivo."""
    pattern = r"(?:resumo|objetivo|sobre mim|summary|about me|profile)[:\s]*\n?(.*?)(?:\n\n|\Z)"
    m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if m:
        summary = m.group(1).strip()[:500]
        return summary if len(summary) > 30 else None
    return None


# ── Extração semântica local (sem OpenAI) ────────────────────

def _extract_with_openai(text: str) -> dict:
    """Fallback local — sem dependência de OpenAI."""
    return {}


# ── Função principal ──────────────────────────────────────────

def parse_resume(filepath: str) -> dict:
    """
    Extrai dados do currículo. Retorna dict com:
    text, job_title, years_experience, skills, bio,
    linkedin_url, github_url, phone, email
    """
    text = extract_text_from_pdf(filepath)
    if not text:
        return {"text": "", "skills": [], "error": "Não foi possível extrair texto do PDF"}

    # Tenta regex primeiro
    result = {
        "text":             text,
        "job_title":        _extract_job_title(text),
        "years_experience": _extract_years_experience(text),
        "skills":           _extract_skills(text),
        "bio":              _extract_summary(text),
        "linkedin_url":     _extract_linkedin(text),
        "github_url":       _extract_github(text),
        "phone":            _extract_phone(text),
        "email":            _extract_email(text),
    }

    # Enriquece campos vazios com extração adicional (sem IA externa)
    ai_data = _extract_with_openai(text)
    for key in ("job_title", "years_experience", "skills", "bio", "linkedin_url", "github_url", "phone"):
        if not result.get(key) and ai_data.get(key):
            result[key] = ai_data[key]

    return result
