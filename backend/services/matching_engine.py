"""TRAMPO v7 — Motor de Match IA
Calcula compatibilidade candidato ↔ vaga com base em:
  - Skills (60 pts)
  - Nível de experiência (20 pts)
  - Modo de trabalho (10 pts)
  - Localização / cidade (10 pts)
"""
from __future__ import annotations
import math


def _skill_score(candidate_skills: list[str], required_skills: list[str]) -> float:
    """Retorna 0-60 baseado na % de skills da vaga que o candidato tem."""
    if not required_skills:
        return 45.0
    candidate_set = {s.lower().strip() for s in candidate_skills}
    matches = sum(
        1 for skill in required_skills
        if skill.lower().strip() in candidate_set
        or any(skill.lower() in cs for cs in candidate_set)
    )
    return round((matches / len(required_skills)) * 60, 1)


def _experience_score(candidate_years: int, required_years: int) -> float:
    """Retorna 0-20 baseado na experiência."""
    if required_years == 0:
        return 20.0
    ratio = candidate_years / required_years
    if ratio >= 1.0:
        return 20.0
    if ratio >= 0.75:
        return 15.0
    if ratio >= 0.5:
        return 10.0
    return 5.0


def _work_mode_score(candidate_mode: str, job_mode: str) -> float:
    """Retorna 0-10 baseado no modo de trabalho."""
    if not candidate_mode or candidate_mode == "any":
        return 10.0
    if candidate_mode == job_mode:
        return 10.0
    compat = {
        ("hybrid", "remote"): 7,
        ("hybrid", "onsite"): 7,
        ("remote", "hybrid"): 5,
        ("onsite", "hybrid"): 5,
    }
    return float(compat.get((candidate_mode, job_mode), 3))


def _location_score(candidate_city: str, job_city: str) -> float:
    """Retorna 0-10 baseado na cidade."""
    if not candidate_city or not job_city:
        return 5.0
    if candidate_city.lower().strip() == job_city.lower().strip():
        return 10.0
    return 3.0


def calculate_match(candidate_profile, job) -> dict:
    """
    Recebe CandidateProfile e Job, retorna dict com score e razões.
    """
    from database import db
    from models import User

    user = db.session.get(User, candidate_profile.user_id)

    c_skills    = candidate_profile.get_skills_list()
    j_skills    = job.get_skills_list()
    c_years     = candidate_profile.years_experience or 0
    j_years     = job.required_experience or 0
    c_mode      = candidate_profile.work_mode or "any"
    j_mode      = job.work_mode or "onsite"
    c_city      = (user.cidade or "") if user else ""
    j_city      = job.cidade or ""

    skill_pts   = _skill_score(c_skills, j_skills)
    exp_pts     = _experience_score(c_years, j_years)
    mode_pts    = _work_mode_score(c_mode, j_mode)
    loc_pts     = _location_score(c_city, j_city)
    total       = round(skill_pts + exp_pts + mode_pts + loc_pts, 1)

    # Razões legíveis
    reasons = []
    if j_skills:
        matched = [s for s in j_skills if s.lower() in {x.lower() for x in c_skills}]
        if matched:
            reasons.append(f"{len(matched)} skill{'s' if len(matched)>1 else ''} compatível: {', '.join(matched[:3])}")
    if exp_pts == 20:
        reasons.append(f"Experiência suficiente ({c_years} anos)")
    if mode_pts == 10:
        reasons.append(f"Modo de trabalho compatível ({j_mode})")
    if loc_pts == 10:
        reasons.append(f"Mesma cidade: {j_city}")

    return {
        "score":         total,
        "breakdown":     {"skills": skill_pts, "experience": exp_pts, "work_mode": mode_pts, "location": loc_pts},
        "reasons":       reasons,
        "grade":         "Excelente" if total >= 80 else "Boa" if total >= 60 else "Parcial" if total >= 40 else "Baixa",
    }


def find_top_jobs(user_id: int, limit: int = 20, min_score: float = 30) -> list[dict]:
    """Retorna lista de vagas ranqueadas para um candidato."""
    from database import db
    from models import CandidateProfile, Job

    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return []

    jobs = Job.query.filter_by(status="active").order_by(Job.is_featured.desc(), Job.posted_at.desc()).all()
    results = []
    for job in jobs:
        m = calculate_match(profile, job)
        if m["score"] >= min_score:
            d = job.to_dict()
            d["match_score"]   = m["score"]
            d["match_grade"]   = m["grade"]
            d["match_reasons"] = m["reasons"]
            results.append(d)

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:limit]


def find_top_candidates(job_id: int, limit: int = 10, min_score: float = 30) -> list[dict]:
    """Retorna candidatos ranqueados para uma vaga."""
    from database import db
    from models import Job, CandidateProfile, User

    job = db.session.get(Job, job_id)
    if not job:
        return []

    profiles = CandidateProfile.query.join(User, CandidateProfile.user_id == User.id).all()
    results  = []
    for p in profiles:
        m = calculate_match(p, job)
        if m["score"] >= min_score:
            u = db.session.get(User, p.user_id)
            results.append({
                "user_id":      u.id,
                "name":         u.name,
                "email":        u.email,
                "city":         u.cidade or "",
                "is_premium":   u.is_premium,
                "profile":      p.to_dict(),
                "match_score":  m["score"],
                "match_grade":  m["grade"],
                "match_reasons":m["reasons"],
                "initials":     "".join(n[0] for n in u.name.split()[:2]).upper(),
            })

    results.sort(key=lambda x: (x["is_premium"], x["match_score"]), reverse=True)
    return results[:limit]
