"""TRAMPO v8 — Scraper de Vagas
Fontes gratuitas:
  1. Adzuna API       — 100 req/dia grátis
  2. Remotive API     — 100% gratuita, sem auth
  3. Arbeitnow API    — 100% gratuita, sem auth (vagas remotas)
  4. Gupy Scraper     — portais públicos de grandes empresas BR
  5. The Muse API     — 500 req/mês grátis
"""
from __future__ import annotations
import os, time, requests
from datetime import datetime, timezone


# ─── Adzuna ──────────────────────────────────────────────────

def fetch_adzuna_jobs(query: str = "desenvolvedor", city: str = "Salvador", max_results: int = 50) -> list[dict]:
    app_id  = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        print("⚠️ Adzuna: credenciais não configuradas")
        return []
    results = []
    try:
        resp = requests.get(
            "https://api.adzuna.com/v1/api/jobs/br/search/1",
            params={
                "app_id": app_id, "app_key": app_key,
                "results_per_page": min(max_results, 50),
                "what": query, "where": city,
                "content-type": "application/json",
            }, timeout=15)
        resp.raise_for_status()
        for job in resp.json().get("results", []):
            loc   = job.get("location", {})
            area  = loc.get("area", [])
            cidade = area[-1] if area else city
            results.append({
                "title":       job.get("title", "")[:200],
                "company":     job.get("company", {}).get("display_name", "Empresa")[:200],
                "description": job.get("description", "")[:3000],
                "location":    loc.get("display_name", city),
                "cidade":      cidade[:100],
                "estado":      _guess_estado(cidade),
                "salary_min":  int(job["salary_min"]) if job.get("salary_min") else None,
                "salary_max":  int(job["salary_max"]) if job.get("salary_max") else None,
                "source_url":  job.get("redirect_url", ""),
                "source":      "api_adzuna",
                "work_mode":   "remote" if "remoto" in job.get("title", "").lower() else "onsite",
                "contract_type": "clt",
            })
        print(f"✅ Adzuna: {len(results)} vagas para '{query}' em {city}")
    except Exception as e:
        print(f"❌ Adzuna falhou: {e}")
      
      # 6. JSearch (RapidAPI) — vagas BR com skills detalhadas
    jsearch_jobs = fetch_jsearch_jobs()
    all_jobs.extend(jsearch_jobs)
  def fetch_jsearch_jobs(max_results: int = 100) -> list[dict]:
    """JSearch via RapidAPI — vagas com skills detalhadas (100 req/mês grátis)."""
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    if not api_key:
        print("⚠️ RAPIDAPI_KEY não configurada")
        return []

    results = []
    queries  = ["desenvolvedor Brasil", "analista Brasil", "assistente Salvador",
                "designer Brasil", "marketing Brasil", "engenheiro Brasil"]

    for q in queries[:3]:  # 3 queries para não gastar cota
        try:
            resp = requests.get(
                "https://jsearch.p.rapidapi.com/search",
                headers={
                    "X-RapidAPI-Key":  api_key,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
                },
                params={
                    "query":           q,
                    "page":            "1",
                    "num_pages":       "3",
                    "country":         "br",
                    "language":        "pt",
                },
                timeout=15,
            )
            resp.raise_for_status()
            jobs = resp.json().get("data", [])

            for job in jobs:
                # Extrai skills das qualificações
                quals = job.get("job_required_skills") or []
                if isinstance(quals, list):
                    skills_str = ", ".join(quals[:10])
                else:
                    skills_str = ""

                city  = (job.get("job_city")  or "").strip()
                state = (job.get("job_state") or "").strip()

                results.append({
                    "title":          (job.get("job_title") or "")[:200],
                    "company":        (job.get("employer_name") or "Empresa")[:200],
                    "description":    _strip_html(job.get("job_description") or "")[:3000],
                    "location":       f"{city}, {state}" if city else "Brasil",
                    "cidade":         city[:100],
                    "estado":         state[:2].upper() if state else _guess_estado(city),
                    "salary_min":     int(job["job_min_salary"]) if job.get("job_min_salary") else None,
                    "salary_max":     int(job["job_max_salary"]) if job.get("job_max_salary") else None,
                    "source_url":     job.get("job_apply_link") or job.get("job_google_link") or "",
                    "source":         "api_jsearch",
                    "work_mode":      "remote" if job.get("job_is_remote") else "onsite",
                    "contract_type":  "clt",
                    "required_skills": skills_str,
                    "benefits":       ", ".join((job.get("job_benefits") or [])[:5]),
                })

            print(f"✅ JSearch: {len(jobs)} vagas para '{q}'")
            time.sleep(1)

        except Exception as e:
            print(f"❌ JSearch falhou para '{q}': {e}")

    return results
    return results


# ─── Remotive ─────────────────────────────────────────────────

def fetch_remotive_jobs(query: str = "", max_results: int = 30) -> list[dict]:
    results = []
    try:
        params = {"limit": max_results}
        if query:
            params["search"] = query
        resp = requests.get("https://remotive.com/api/remote-jobs", params=params, timeout=15)
        resp.raise_for_status()
        for job in resp.json().get("jobs", []):
            results.append({
                "title":          job.get("title", "")[:200],
                "company":        job.get("company_name", "Empresa")[:200],
                "description":    job.get("description", "")[:3000],
                "location":       "Remoto",
                "cidade":         "", "estado": "",
                "salary_min":     None, "salary_max": None,
                "source_url":     job.get("url", ""),
                "source":         "api_remotive",
                "work_mode":      "remote",
                "contract_type":  "pj",
                "required_skills": _extract_tags(job.get("tags", [])),
            })
        print(f"✅ Remotive: {len(results)} vagas para '{query}'")
    except Exception as e:
        print(f"❌ Remotive falhou: {e}")
    return results


# ─── Arbeitnow (vagas remotas globais — grátis) ───────────────

def fetch_arbeitnow_jobs(max_results: int = 30) -> list[dict]:
    """API pública, sem auth, vagas remotas com opção BR."""
    results = []
    try:
        resp = requests.get(
            "https://arbeitnow.com/api/job-board-api",
            params={"page": 1},
            headers={"User-Agent": "TRAMPO-App/1.0"},
            timeout=15
        )
        resp.raise_for_status()
        jobs = resp.json().get("data", [])[:max_results]
        for job in jobs:
            results.append({
                "title":         job.get("title", "")[:200],
                "company":       job.get("company_name", "Empresa")[:200],
                "description":   _strip_html(job.get("description", ""))[:3000],
                "location":      "Remoto",
                "cidade":        "", "estado": "",
                "salary_min":    None, "salary_max": None,
                "source_url":    job.get("url", ""),
                "source":        "api_arbeitnow",
                "work_mode":     "remote",
                "contract_type": "pj",
                "required_skills": ", ".join(job.get("tags", [])[:8]),
            })
        print(f"✅ Arbeitnow: {len(results)} vagas remotas")
    except Exception as e:
        print(f"❌ Arbeitnow falhou: {e}")
    return results


# ─── Gupy (portais públicos de grandes empresas BR) ───────────

GUPY_COMPANIES = [
    # Varejo
    ("gpa",         "GPA - Pão de Açúcar"),
    ("carrefour",   "Carrefour"),
    ("assai",       "Assaí Atacadista"),
    ("magazinevoce","Magazine Luiza"),
    ("casasbahia",  "Casas Bahia"),
    ("cea",         "C&A"),
    ("riachuelo",   "Riachuelo"),
    # Alimentação
    ("habibs",      "Habib's"),
    ("outback",     "Outback Steakhouse"),
    # Tecnologia / Finanças
    ("nubank",      "Nubank"),
    ("picpay",      "PicPay"),
    ("stone",       "Stone"),
    ("ifood",       "iFood"),
    ("quintoandar", "QuintoAndar"),
    # Saúde
    ("dasa",        "Dasa"),
    ("amil",        "Amil"),
    # Logística
    ("loggi",       "Loggi"),
    ("sequoia",     "Sequoia Logística"),
    # Educação
    ("cogna",       "Cogna Educação"),
]

def fetch_gupy_jobs(company_slug: str, company_name: str, max_results: int = 20) -> list[dict]:
    """Busca vagas no portal público Gupy de uma empresa."""
    results = []
    try:
        url  = f"https://{company_slug}.gupy.io/api/job"
        resp = requests.get(url, params={"limit": max_results}, timeout=10,
                            headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return []
        jobs = resp.json() if isinstance(resp.json(), list) else resp.json().get("data", [])
        for job in jobs[:max_results]:
            work_mode = "onsite"
            name = (job.get("name") or "").lower()
            if "remoto" in name or "home office" in name or "remote" in name:
                work_mode = "remote"
            elif "híbrido" in name or "hibrido" in name or "hybrid" in name:
                work_mode = "hybrid"

            city  = (job.get("city") or "").strip()
            state = (job.get("state") or "").strip()

            results.append({
                "title":         (job.get("name") or "")[:200],
                "company":       company_name,
                "description":   _strip_html(job.get("description") or "")[:3000],
                "location":      f"{city}, {state}" if city else "Brasil",
                "cidade":        city[:100],
                "estado":        state[:2].upper() if state else "",
                "salary_min":    None, "salary_max": None,
                "source_url":    f"https://{company_slug}.gupy.io/job/{job.get('id','')}",
                "source":        f"gupy_{company_slug}",
                "work_mode":     work_mode,
                "contract_type": "clt",
            })
        if results:
            print(f"✅ Gupy/{company_name}: {len(results)} vagas")
    except Exception as e:
        print(f"⚠️ Gupy/{company_slug} falhou: {e}")
    return results


def fetch_all_gupy_jobs() -> list[dict]:
    """Busca vagas em todos os portais Gupy configurados."""
    all_jobs = []
    for slug, name in GUPY_COMPANIES:
        jobs = fetch_gupy_jobs(slug, name, max_results=15)
        all_jobs.extend(jobs)
        time.sleep(0.5)  # respeita rate limit
    return all_jobs


# ─── The Muse ─────────────────────────────────────────────────

def fetch_themuse_jobs(query: str = "developer", max_results: int = 20) -> list[dict]:
    api_key = os.environ.get("THEMUSE_API_KEY", "")
    results = []
    try:
        params = {"page": 1, "descended": "true"}
        if query:
            params["category"] = query
        if api_key:
            params["api_key"] = api_key
        resp = requests.get("https://www.themuse.com/api/public/jobs",
                            params=params, timeout=15)
        resp.raise_for_status()
        for job in resp.json().get("results", [])[:max_results]:
            loc_list = job.get("locations", [])
            location = loc_list[0].get("name", "Remoto") if loc_list else "Remoto"
            results.append({
                "title":         job.get("name", "")[:200],
                "company":       job.get("company", {}).get("name", "Empresa")[:200],
                "description":   _strip_html(job.get("contents", ""))[:3000],
                "location":      location, "cidade": "", "estado": "",
                "salary_min":    None, "salary_max": None,
                "source_url":    job.get("refs", {}).get("landing_page", ""),
                "source":        "api_themuse",
                "work_mode":     "remote",
                "contract_type": "clt",
            })
        print(f"✅ The Muse: {len(results)} vagas")
    except Exception as e:
        print(f"❌ The Muse falhou: {e}")
    return results


# ─── Salvar no banco ──────────────────────────────────────────

def save_jobs_to_db(jobs: list[dict]) -> int:
    from database import db
    from models import Job
    saved = 0

    # Lista de empresas que merecem destaque
    big_companies = ["nubank", "ifood", "stone", "mercado livre", "amazon", "google", "microsoft", "magazine luiza", "carrefour", "gpa", "pão de açúcar", "outback", "habib's", "c&a", "riachuelo", "dasa", "amil", "loggi", "sequoia", "cogna", "picpay", "quintoandar"]

    for job_data in jobs:
        try:
            url = job_data.get("source_url", "")
            if url and Job.query.filter_by(source_url=url).first():
                continue

            # Determina se é destaque
            is_featured = False
            salary_min = job_data.get("salary_min")
            if salary_min and salary_min >= 5000:
                is_featured = True
            else:
                company_lower = (job_data.get("company") or "").lower()
                if any(c in company_lower for c in big_companies):
                    is_featured = True

            job = Job(
                title            = job_data.get("title", "Sem título"),
                company          = job_data.get("company", "Empresa"),
                description      = job_data.get("description", ""),
                location         = job_data.get("location", ""),
                cidade           = job_data.get("cidade", ""),
                estado           = job_data.get("estado", ""),
                salary_min       = salary_min,
                salary_max       = job_data.get("salary_max"),
                source_url       = url or None,
                source           = job_data.get("source", "scraped"),
                work_mode        = job_data.get("work_mode", "onsite"),
                contract_type    = job_data.get("contract_type", "clt"),
                contact_email    = job_data.get("contact_email", ""),
                required_skills  = job_data.get("required_skills", ""),
                status           = "active",
                is_paid          = True,
                is_featured      = is_featured,   # <- novo campo
                posted_at        = datetime.now(timezone.utc),
            )
            db.session.add(job)
            saved += 1
            if saved % 20 == 0:
                db.session.commit()
                time.sleep(0.1)
        except Exception as e:
            print(f"⚠️ Erro ao salvar '{job_data.get('title')}': {e}")
            db.session.rollback()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro no commit final: {e}")
    print(f"💾 {saved} vagas novas salvas no banco")
    return saved


# ─── Scraping completo ────────────────────────────────────────

def fetch_serpapi_jobs() -> list[dict]:
    """Google Jobs via SerpAPI (100 buscas/mês grátis)."""
    api_key = os.environ.get("SERPAPI_KEY", "")
    if not api_key:
        print("⚠️ SERPAPI_KEY não configurada")
        return []

    results = []
    queries = [
        "vagas emprego Salvador BA",
        "vagas desenvolvedor Brasil remoto",
        "vagas analista São Paulo",
        "vagas assistente administrativo Brasil",
        "vagas marketing digital Brasil",
    ]

    for q in queries:
        try:
            resp = requests.get(
                "https://serpapi.com/search",
                params={
                    "engine":   "google_jobs",
                    "q":        q,
                    "hl":       "pt",
                    "gl":       "br",
                    "api_key":  api_key,
                },
                timeout=20,
            )
            resp.raise_for_status()
            jobs = resp.json().get("jobs_results", [])

            for job in jobs:
                # Extrai localização
                location = job.get("location", "Brasil")
                parts    = location.split(",")
                city     = parts[0].strip() if parts else ""
                state    = parts[1].strip() if len(parts) > 1 else ""

                # Extrai salário se disponível
                sal_min = sal_max = None
                highlights = job.get("detected_extensions", {})
                if highlights.get("salary"):
                    raw = highlights["salary"]
                    nums = [int(n.replace(".","").replace(",","")) for n in __import__("re").findall(r"[\d.,]+", raw) if len(n) > 3]
                    if len(nums) >= 2: sal_min, sal_max = nums[0], nums[1]
                    elif len(nums) == 1: sal_min = nums[0]

                # Skills das extensões
                skills_list = job.get("job_highlights", [])
                skills_str  = ""
                for h in skills_list:
                    if h.get("title", "").lower() in ("qualifications", "qualificações", "requisitos", "skills"):
                        skills_str = ", ".join(h.get("items", [])[:8])
                        break

                work_mode = "remote"
                if any(w in location.lower() for w in ["remoto","remote","home office"]) or \
                   any(w in job.get("title","").lower() for w in ["remoto","remote"]):
                    work_mode = "remote"
                else:
                    work_mode = "onsite"

                results.append({
                    "title":           (job.get("title") or "")[:200],
                    "company":         (job.get("company_name") or "Empresa")[:200],
                    "description":     (job.get("description") or "")[:3000],
                    "location":        location,
                    "cidade":          city[:100],
                    "estado":          _guess_estado(city) or state[:2].upper(),
                    "salary_min":      sal_min,
                    "salary_max":      sal_max,
                    "source_url":      job.get("share_link") or "",
                    "source":          "api_serpapi",
                    "work_mode":       work_mode,
                    "contract_type":   "clt",
                    "required_skills": skills_str,
                    "benefits":        "",
                })

            print(f"✅ SerpAPI Google Jobs: {len(jobs)} vagas para '{q}'")
            time.sleep(2)  # respeita rate limit

        except Exception as e:
            print(f"❌ SerpAPI falhou para '{q}': {e}")

    return results
  
def run_full_scrape() -> dict:
    all_jobs = []

    # 1. Adzuna — várias queries em Salvador e SP
    for q in ["desenvolvedor", "analista", "designer", "marketing", "engenheiro",
               "vendedor", "auxiliar", "assistente", "operador", "técnico"]:
        all_jobs.extend(fetch_adzuna_jobs(query=q, city="Salvador", max_results=20))
        time.sleep(0.8)

    # 2. Remotive — vagas remotas variadas
    for q in ["developer", "engineer", "design", "marketing", "data",
               "customer", "finance", "product", "sales", "support"]:
        all_jobs.extend(fetch_remotive_jobs(query=q, max_results=15))
        time.sleep(0.4)

    # 3. Arbeitnow — vagas remotas globais (grátis, sem auth)
    all_jobs.extend(fetch_arbeitnow_jobs(max_results=40))
    time.sleep(1)

    # 4. Gupy — 20 grandes empresas brasileiras
    all_jobs.extend(fetch_all_gupy_jobs())
    time.sleep(1)

    # 5. The Muse — fallback internacional
    all_jobs.extend(fetch_themuse_jobs(query="developer", max_results=20))

    # 7. SerpAPI — Google Jobs (vagas com descrição completa)
    all_jobs.extend(fetch_serpapi_jobs())
    time.sleep(1)
  
    total_saved = save_jobs_to_db(all_jobs)
    result = {
        "total_fetched": len(all_jobs),
        "total_saved":   total_saved,
        "timestamp":     datetime.now(timezone.utc).isoformat(),
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
        "goiânia": "GO",
        "florianópolis": "SC",
        "belém": "PA",
        "maceió": "AL",
        "natal": "RN",
        "teresina": "PI",
        "campo grande": "MS",
    }
    return mapping.get(cidade.lower().strip(), "")

def _extract_tags(tags: list) -> str:
    if isinstance(tags, list):
        return ", ".join(str(t) for t in tags[:10])
    return ""

def _strip_html(html: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
