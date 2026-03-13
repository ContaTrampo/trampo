"""TRAMPO v7 — Rotas dos Recrutadores"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Job, Application, CandidateProfile, RecruiterProfile
from services.matching_engine import find_top_candidates

recruiters_bp = Blueprint("recruiters", __name__, url_prefix="/api/recruiters")


@recruiters_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    rec     = RecruiterProfile.query.filter_by(user_id=user_id).first()
    user    = db.session.get(User, user_id)
    return jsonify({
        "profile": rec.to_dict() if rec else None,
        "user":    user.to_dict() if user else None,
    }), 200


@recruiters_bp.route("/profile", methods=["POST", "PUT"])
@jwt_required()
def save_profile():
    user_id = int(get_jwt_identity())
    data    = request.get_json() or {}
    rec     = RecruiterProfile.query.filter_by(user_id=user_id).first()
    if not rec:
        rec = RecruiterProfile(user_id=user_id)
        db.session.add(rec)
    for f in ["company_name", "company_cnpj", "company_website", "company_size", "industry"]:
        if f in data:
            setattr(rec, f, data[f])
    db.session.commit()
    return jsonify({"message": "Perfil atualizado! ✅", "profile": rec.to_dict()}), 200


@recruiters_bp.route("/my-jobs", methods=["GET"])
@jwt_required()
def my_jobs():
    user_id = int(get_jwt_identity())
    jobs = Job.query.filter_by(recruiter_id=user_id) \
               .order_by(Job.posted_at.desc()).all()
    return jsonify({"jobs": [j.to_dict() for j in jobs]}), 200


@recruiters_bp.route("/jobs/<int:job_id>/candidates", methods=["GET"])
@jwt_required()
def job_candidates(job_id):
    user_id = int(get_jwt_identity())
    job     = db.get_or_404(Job, job_id)
    if job.recruiter_id is not None and job.recruiter_id != user_id:
        return jsonify({"error": "Sem permissão"}), 403

    apps = Application.query.filter_by(job_id=job_id) \
               .order_by(Application.is_featured.desc(), Application.match_score.desc()).all()
    result = []
    for app in apps:
        u = db.session.get(User, app.user_id)
        p = CandidateProfile.query.filter_by(user_id=app.user_id).first()
        result.append({
            "application_id": app.id,
            "match_score":    round(app.match_score, 1),
            "status":         app.status,
            "is_featured":    app.is_featured,
            "cover_letter":   app.cover_letter,
            "sent_at":        app.sent_at.isoformat() if app.sent_at else None,
            "user":           u.to_dict() if u else {},
            "profile":        p.to_dict() if p else {},
        })
    return jsonify({"candidates": result, "total": len(result)}), 200


@recruiters_bp.route("/jobs/<int:job_id>/top-candidates", methods=["GET"])
@jwt_required()
def top_candidates_route(job_id):
    candidates = find_top_candidates(job_id, limit=10, min_score=0)
    return jsonify({"candidates": candidates}), 200


@recruiters_bp.route("/applications/<int:app_id>/status", methods=["PUT"])
@jwt_required()
def update_application_status(app_id):
    user_id    = int(get_jwt_identity())
    data       = request.get_json() or {}
    new_status = data.get("status")
    allowed    = ["viewed", "responded", "interview", "offer", "rejected"]

    if new_status not in allowed:
        return jsonify({"error": f"Status inválido. Use: {allowed}"}), 400

    app = db.get_or_404(Application, app_id)
    job = db.session.get(Job, app.job_id)
    if job and job.recruiter_id is not None and job.recruiter_id != user_id:
        return jsonify({"error": "Sem permissão"}), 403

    app.status = new_status
    if data.get("notes"):
        app.recruiter_notes = data["notes"]
    db.session.commit()
    return jsonify({"message": "Status atualizado!", "status": new_status}), 200


@recruiters_bp.route("/stats", methods=["GET"])
@jwt_required()
def recruiter_stats():
    user_id  = int(get_jwt_identity())
    jobs     = Job.query.filter_by(recruiter_id=user_id).all()
    total_apps  = sum(len(j.applications) for j in jobs)
    active_jobs = sum(1 for j in jobs if j.status == "active")
    interviews  = sum(
        1 for j in jobs for a in j.applications if a.status == "interview"
    )
    paid_jobs = sum(1 for j in jobs if j.is_paid)
    return jsonify({
        "total_jobs":         len(jobs),
        "active_jobs":        active_jobs,
        "paid_jobs":          paid_jobs,
        "total_applications": total_apps,
        "interviews":         interviews,
    }), 200
