"""TRAMPO v8 — Scraper de Vagas
Fontes gratuitas:
  1. Adzuna API (100 req/dia grátis)
  2. Remotive API (100% gratuita, sem auth)
  3. The Muse API (500 req/mês grátis)
"""
from __future__ import annotations
import os
import time
import requests
from datetime import datetime, timezone


# ─── Adzuna ──────────────────────────────────────────────────

def fetch_adzuna_jobs(query: str = "desenvolvedor", city: str = "Salvador", max_results: int = 50) -> list[dict]:
    """Busca vagas na API Adzuna (Brasil)."""
    app_id = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        print("⚠️ Adzuna: ADZUNA_APP_ID ou ADZUNA_APP_KEY não configurados")
        return []

    results = []
    try:
        url = "https://api.adzuna.com/v1/api/jobs/br/search/1"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": min(max_results, 50),
            "what": query,
            "where": city,
            "content-type": "application/json",
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for job in data.get("results", []):
            loc = job.get("location", {})
            display_loc = loc.get("display_name", city)
            area = loc.get("area", [])
            cidade = area[-1] if area else city
            estado = _guess_estado(cidade)

            results.append({
                "title": job.get("title", "")[:200],
                "company": job.get("company", {}).get("display_name", "Empresa")[:200],
                "description": job.get("description", "")[:3000],
                "location": display_loc,
                "cidade": cidade[:100],
                "estado": estado,
                "salary_min": int(job["salary_min"]) if job.get("salary_min") else None,
                "salary_max": int(job["salary_max"]) if job.get("salary_max") else None,
                "source_url": job.get("redirect_url", ""),
                "source": "api_adzuna",
                "work_mode": "remote" if "remoto" in job.get("title", "").lower() or "remote" in job.get("title", "").lower() else "onsite",
                "contract_type": "clt",
                "contact_email": "",
            })
        print(f"✅ Adzuna: {len(results)} vagas obtidas para '{query}' em {city}")
    except Exception as e:
        print(f"❌ Adzuna falhou: {e}")

    return results


# ─── Remotive ─────────────────────────────────────────────────

def fetch_remotive_jobs(query: str = "", max_results: int = 30) -> list[dict]:
    """Busca vagas remotas na API Remotive (gratuita, sem auth)."""
    results = []
    try:
        params = {"limit": max_results}
        if query:
            params["search"] = query
        resp = requests.get("https://remotive.com/api/remote-jobs", params=params, timeout=15)
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])

        for job in jobs:
            results.append({
                "title": job.get("title", "")[:200],
                "company": job.get("company_name", "Empresa")[:200],
                "description": job.get("description", "")[:3000],
                "location": "Remoto",
                "cidade": "",
                "estado": "",
                "salary_min": None,
                "salary_max": None,
                "source_url": job.get("url", ""),
                "source": "api_remotive",
                "work_mode": "remote",
                "contract_type": "pj",
                "contact_email": "",
                "required_skills": _extract_tags(job.get("tags", [])),
            })
        print(f"✅ Remotive: {len(results)} vagas remotas obtidas")
    except Exception as e:
        print(f"❌ Remotive falhou: {e}")

    return results


# ─── The Muse ─────────────────────────────────────────────────

def fetch_themuse_jobs(query: str = "developer", max_results: int = 20) -> list[dict]:
    """Busca vagas na API The Muse (500 req/mês grátis)."""
    api_key = os.environ.get("THEMUSE_API_KEY", "")
    results = []
    try:
        params = {"page": 1, "descended": "true"}
        if query:
            params["category"] = query
        if api_key:
            params["api_key"] = api_key

        resp = requests.get("https://www.themuse.com/api/public/jobs", params=params, timeout=15)
        resp.raise_for_status()
        jobs = resp.json().get("results", [])[:max_results]

        for job in jobs:
            loc_list = job.get("locations", [])
            location = loc_list[0].get("name", "Remoto") if loc_list else "Remoto"

            # Extrai texto limpo da descrição HTML
            desc_html = job.get("contents", "")
            desc = _strip_html(desc_html)[:3000]

            results.append({
                "title": job.get("name", "")[:200],
                "company": job.get("company", {}).get("name", "Empresa")[:200],
                "description": desc,
                "location": location,
                "cidade": "",
                "estado": "",
                "salary_min": None,
                "salary_max": None,
                "source_url": job.get("refs", {}).get("landing_page", ""),
                "source": "api_themuse",
                "work_mode": "remote",
                "contract_type": "clt",
                "contact_email": "",
            })
        print(f"✅ The Muse: {len(results)} vagas obtidas")
    except Exception as e:
        print(f"❌ The Muse falhou: {e}")

    return results


# ─── Salvar no banco ──────────────────────────────────────────

def save_jobs_to_db(jobs: list[dict]) -> int:
    """Salva vagas no banco, ignorando duplicatas por source_url."""
    from database import db
    from models import Job

    saved = 0
    for job_data in jobs:
        try:
            # Verifica duplicata
            url = job_data.get("source_url", "")
            if url and Job.query.filter_by(source_url=url).first():
                continue

            job = Job(
                title=job_data.get("title", "Sem título"),
                company=job_data.get("company", "Empresa"),
                description=job_data.get("description", ""),
                location=job_data.get("location", ""),
                cidade=job_data.get("cidade", ""),
                estado=job_data.get("estado", ""),
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                source_url=url or None,
                source=job_data.get("source", "scraped"),
                work_mode=job_data.get("work_mode", "onsite"),
                contract_type=job_data.get("contract_type", "clt"),
                contact_email=job_data.get("contact_email", ""),
                required_skills=job_data.get("required_skills", ""),
                status="active",
                is_paid=True,   # vagas de API são gratuitas/já pagas
                posted_at=datetime.now(timezone.utc),
            )
            db.session.add(job)
            saved += 1

            # Commit em lotes de 20 para não sobrecarregar
            if saved % 20 == 0:
                db.session.commit()
                time.sleep(0.1)

        except Exception as e:
            print(f"⚠️ Erro ao salvar vaga '{job_data.get('title')}': {e}")
            db.session.rollback()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro no commit final: {e}")

    print(f"💾 {saved} vagas novas salvas no banco")
    return saved


# ─── Scraping completo ────────────────────────────────────────

def run_full_scrape() -> dict:
    """Executa todos os scrapers e salva no banco."""
    queries_adzuna = ["desenvolvedor", "analista", "designer", "marketing", "engenheiro"]
    queries_remotive = ["developer", "engineer", "design", "marketing", "data"]

    all_jobs = []

    # Adzuna — várias queries para Salvador e São Paulo
    for q in queries_adzuna:
        jobs = fetch_adzuna_jobs(query=q, city="Salvador", max_results=20)
        all_jobs.extend(jobs)
        time.sleep(1)  # respeita rate limit

    # Remotive — vagas remotas
    for q in queries_remotive:
        jobs = fetch_remotive_jobs(query=q, max_results=15)
        all_jobs.extend(jobs)
        time.sleep(0.5)

    # The Muse — fallback
    muse_jobs = fetch_themuse_jobs(query="developer", max_results=20)
    all_jobs.extend(muse_jobs)

    total_saved = save_jobs_to_db(all_jobs)

    result = {
        "total_fetched": len(all_jobs),
        "total_saved": total_saved,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    print(f"🏁 Scraping completo: {result}")
    return result


# ─── Helpers ──────────────────────────────────────────────────

def _guess_estado(cidade: str) -> str:
    mapping = {
        "salvador": "BA", "feira de santana": "BA", "vitória da conquista": "BA",
        "são paulo": "SP", "campinas": "SP", "guarulhos": "SP", "santos": "SP",
        "rio de janeiro": "RJ", "niterói": "RJ",
        "belo horizonte": "MG", "uberlândia": "MG",
        "curitiba": "PR", "londrina": "PR",
        "porto alegre": "RS",
        "recife": "PE", "caruaru": "PE",
        "fortaleza": "CE",
        "manaus": "AM",
        "brasília": "DF", "distrito federal": "DF",
    }
    return mapping.get(cidade.lower().strip(), "")


def _extract_tags(tags: list) -> str:
    if isinstance(tags, list):
        return ", ".join(str(t) for t in tags[:10])
    return ""


def _strip_html(html: str) -> str:
    """Remove tags HTML simples."""
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
