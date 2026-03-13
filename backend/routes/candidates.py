"""TRAMPO v7 — Rotas de Candidatos"""
import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from database import db
from models import User, CandidateProfile, Application

candidates_bp = Blueprint("candidates", __name__, url_prefix="/api/candidates")

ALLOWED_EXT = {"pdf"}

def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ── Perfil ────────────────────────────────────────────────────

@candidates_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = CandidateProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return jsonify({"user": user.to_dict(), "profile": profile.to_dict()}), 200


@candidates_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    data    = request.get_json() or {}

    # Atualiza campos do User
    for field in ["name", "phone", "cep", "logradouro", "numero", "complemento",
                  "bairro", "cidade", "estado", "email_notifications"]:
        if field in data:
            setattr(user, field, data[field])

    # Atualiza CandidateProfile
    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = CandidateProfile(user_id=user_id)
        db.session.add(profile)

    for field in ["job_title", "years_experience", "seniority", "salary_min", "salary_max",
                  "availability", "work_mode", "bio", "linkedin_url", "github_url",
                  "portfolio_url", "whatsapp"]:
        if field in data:
            setattr(profile, field, data[field])

    if "skills" in data:
        skills = data["skills"]
        if isinstance(skills, list):
            profile.skills = ", ".join(skills)
        else:
            profile.skills = skills

    db.session.commit()
    return jsonify({"message": "Perfil atualizado! ✅", "profile": profile.to_dict()}), 200


# ── Upload de currículo ───────────────────────────────────────

@candidates_bp.route("/resume/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = int(get_jwt_identity())
    if "resume" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["resume"]
    if file.filename == "" or not _allowed(file.filename):
        return jsonify({"error": "Arquivo inválido. Envie um PDF."}), 400

    filename = secure_filename(f"resume_{user_id}.pdf")
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Extrai dados
    try:
        from services.resume_parser import parse_resume
        data = parse_resume(filepath)
    except Exception as e:
        data = {"text": "", "error": str(e)}

    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = CandidateProfile(user_id=user_id)
        db.session.add(profile)

    profile.resume_filename = filename
    if data.get("text"):
        profile.resume_text = data["text"][:10000]

    # Aplica extração automaticamente se campos vazios
    if data.get("job_title") and not profile.job_title:
        profile.job_title = data["job_title"]
    if data.get("years_experience") and not profile.years_experience:
        profile.years_experience = data["years_experience"]
    if data.get("skills") and not profile.skills:
        profile.skills = ", ".join(data["skills"])
    if data.get("bio") and not profile.bio:
        profile.bio = data["bio"]
    if data.get("linkedin_url") and not profile.linkedin_url:
        profile.linkedin_url = data["linkedin_url"]
    if data.get("github_url") and not profile.github_url:
        profile.github_url = data["github_url"]

    user = db.session.get(User, user_id)
    if data.get("phone") and not user.phone:
        user.phone = data["phone"]

    db.session.commit()
    return jsonify({
        "message":  "Currículo enviado e dados extraídos! ✅",
        "extracted": {
            "job_title":        data.get("job_title"),
            "years_experience": data.get("years_experience"),
            "skills":           data.get("skills", []),
            "bio":              data.get("bio"),
            "linkedin_url":     data.get("linkedin_url"),
        },
        "profile": profile.to_dict(),
    }), 200


@candidates_bp.route("/resume/download", methods=["GET"])
@jwt_required()
def download_resume():
    user_id = int(get_jwt_identity())
    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    if not profile or not profile.resume_filename:
        return jsonify({"error": "Nenhum currículo encontrado"}), 404
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], profile.resume_filename, as_attachment=True)


# ── Candidaturas ──────────────────────────────────────────────

@candidates_bp.route("/applications", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = int(get_jwt_identity())
    apps = Application.query.filter_by(user_id=user_id) \
               .order_by(Application.sent_at.desc()).all()
    return jsonify({"applications": [a.to_dict() for a in apps], "total": len(apps)}), 200


# ── Lista pública de candidatos (para recrutadores) ───────────

@candidates_bp.route("/search", methods=["GET"])
@jwt_required()
def search_candidates():
    q        = (request.args.get("q") or "").strip().lower()
    city     = (request.args.get("city") or "").strip().lower()
    skill    = (request.args.get("skill") or "").strip().lower()
    page     = max(1, int(request.args.get("page", 1)))
    per_page = 12

    query = CandidateProfile.query.join(User, CandidateProfile.user_id == User.id)

    if q:
        query = query.filter(
            db.or_(
                User.name.ilike(f"%{q}%"),
                CandidateProfile.job_title.ilike(f"%{q}%"),
                CandidateProfile.skills.ilike(f"%{q}%"),
            )
        )
    if city:
        query = query.filter(User.cidade.ilike(f"%{city}%"))
    if skill:
        query = query.filter(CandidateProfile.skills.ilike(f"%{skill}%"))

    total    = query.count()
    profiles = query.order_by(
        User.is_premium.desc(), CandidateProfile.avg_rating.desc()
    ).offset((page - 1) * per_page).limit(per_page).all()

    results = []
    for p in profiles:
        u = db.session.get(User, p.user_id)
        results.append({
            "user_id":      u.id,
            "name":         u.name,
            "city":         u.cidade or "",
            "estado":       u.estado or "",
            "is_premium":   u.is_premium,
            "profile":      p.to_dict(),
            "initials":     "".join(n[0] for n in u.name.split()[:2]).upper(),
        })

    return jsonify({
        "candidates": results,
        "total":      total,
        "page":       page,
        "pages":      (total + per_page - 1) // per_page,
    }), 200
