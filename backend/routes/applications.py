"""TRAMPO v7 — Candidaturas"""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Job, Application, CandidateProfile
from services.matching_engine import calculate_match
from services.email_service import send_application_email

applications_bp = Blueprint("applications", __name__, url_prefix="/api/applications")


@applications_bp.route("/", methods=["POST"])
@jwt_required()
def send_application():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)

    if user.role != "candidate":
        return jsonify({"error": "Apenas candidatos podem se candidatar"}), 403

    data   = request.get_json() or {}
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"error": "job_id é obrigatório"}), 400

    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Vaga não encontrada"}), 404
    if job.status != "active":
        return jsonify({"error": "Esta vaga não está ativa"}), 409

    # Verifica duplicata
    existing = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing:
        return jsonify({"error": "Você já se candidatou a esta vaga"}), 409

    # Verifica limite diário
    user.reset_daily_if_needed()
    if not user.can_send_today():
        limit = user.get_daily_limit()
        return jsonify({
            "error":   f"Limite diário atingido ({limit} envios/dia). Faça upgrade para Premium!",
            "upgrade": True,
        }), 429

    # Calcula match
    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    match_data  = calculate_match(profile, job) if profile else {"score": 0, "reasons": []}
    cover_letter = (data.get("cover_letter") or "").strip()[:2000]

    app = Application(
        user_id      = user_id,
        job_id       = job_id,
        match_score  = match_data["score"],
        cover_letter = cover_letter or None,
        email_sent_to= job.contact_email or None,
        status       = "sent",
        is_featured  = user.is_premium,
    )
    db.session.add(app)
    user.daily_sends_used += 1
    db.session.commit()

    try:
        send_application_email(user, job, app)
    except Exception as e:
        print(f"⚠️ Email de candidatura falhou: {e}")

    return jsonify({
        "message":       f"Candidatura enviada! Match: {round(match_data['score'])}% 🎯",
        "application":   app.to_dict(),
        "match_score":   match_data["score"],
        "match_reasons": match_data.get("reasons", []),
        "sends_left":    user.get_daily_limit() - user.daily_sends_used,
    }), 201


@applications_bp.route("/", methods=["GET"])
@jwt_required()
def list_applications():
    user_id = int(get_jwt_identity())
    apps = Application.query.filter_by(user_id=user_id) \
               .order_by(Application.sent_at.desc()).all()
    return jsonify({"applications": [a.to_dict() for a in apps]}), 200
