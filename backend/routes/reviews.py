"""TRAMPO v7 — Avaliações de Candidatos"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Review, CandidateProfile, Application

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")


@reviews_bp.route("/candidate/<int:candidate_id>", methods=["GET"])
def get_reviews(candidate_id):
    """Retorna avaliações públicas de um candidato."""
    reviews = Review.query.filter_by(
        candidate_id=candidate_id, is_public=True
    ).order_by(Review.created_at.desc()).all()
    return jsonify({"reviews": [r.to_dict() for r in reviews]}), 200


@reviews_bp.route("/", methods=["POST"])
@jwt_required()
def create_review():
    """Recrutador avalia um candidato (precisa ter candidatura na vaga)."""
    reviewer_id  = int(get_jwt_identity())
    reviewer     = db.session.get(User, reviewer_id)
    data         = request.get_json() or {}
    candidate_id = data.get("candidate_id")
    job_id       = data.get("job_id")
    rating       = data.get("rating")
    comment      = (data.get("comment") or "").strip()

    if reviewer.role != "recruiter":
        return jsonify({"error": "Apenas recrutadores podem avaliar candidatos"}), 403

    if not candidate_id or not rating:
        return jsonify({"error": "candidate_id e rating são obrigatórios"}), 400

    if not isinstance(rating, int) or not 1 <= rating <= 5:
        return jsonify({"error": "Rating deve ser um número entre 1 e 5"}), 400

    candidate = db.session.get(User, candidate_id)
    if not candidate:
        return jsonify({"error": "Candidato não encontrado"}), 404

    # Verifica se o recrutador já avaliou este candidato para esta vaga
    existing = Review.query.filter_by(
        candidate_id=candidate_id,
        reviewer_id=reviewer_id,
        job_id=job_id,
    ).first()
    if existing:
        return jsonify({"error": "Você já avaliou este candidato para esta vaga"}), 409

    review = Review(
        candidate_id=candidate_id,
        reviewer_id=reviewer_id,
        job_id=job_id,
        rating=rating,
        comment=comment[:1000] if comment else None,
        is_public=True,
    )
    db.session.add(review)
    db.session.flush()

    # Recalcula média do candidato
    _update_avg_rating(candidate_id)
    db.session.commit()

    return jsonify({
        "message": "Avaliação registrada! ✅",
        "review":  review.to_dict(),
    }), 201


@reviews_bp.route("/top-candidates", methods=["GET"])
def top_candidates():
    """Candidatos premium com melhores avaliações para a home."""
    profiles = (
        CandidateProfile.query
        .join(User, CandidateProfile.user_id == User.id)
        .filter(User.is_premium == True, CandidateProfile.avg_rating >= 4.0)
        .order_by(CandidateProfile.avg_rating.desc(), CandidateProfile.rating_count.desc())
        .limit(6)
        .all()
    )
    result = []
    for p in profiles:
        u = db.session.get(User, p.user_id)
        result.append({
            "user_id":        u.id,
            "name":           u.name,
            "city":           u.cidade or "",
            "job_title":      p.job_title or "Profissional",
            "skills":         p.get_skills_list()[:4],
            "avg_rating":     p.avg_rating,
            "rating_count":   p.rating_count,
            "initials":       "".join(n[0] for n in u.name.split()[:2]).upper(),
        })
    return jsonify({"candidates": result}), 200


def _update_avg_rating(candidate_id: int):
    """Recalcula e salva a média de avaliações do candidato."""
    reviews = Review.query.filter_by(candidate_id=candidate_id, is_public=True).all()
    profile = CandidateProfile.query.filter_by(user_id=candidate_id).first()
    if profile:
        if reviews:
            profile.avg_rating   = sum(r.rating for r in reviews) / len(reviews)
            profile.rating_count = len(reviews)
        else:
            profile.avg_rating   = 0.0
            profile.rating_count = 0
