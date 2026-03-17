"""TRAMPO v8 — Admin"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Job, Application
from datetime import datetime, timezone

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _require_admin():
    uid  = int(get_jwt_identity())
    user = db.session.get(User, uid)
    if not user or user.role != "admin":
        return None, (jsonify({"error": "Acesso negado"}), 403)
    return user, None


# ── Scraping público (protegido por chave) ────────────────────
@admin_bp.route("/scrape-jobs", methods=["GET", "POST"])
def scrape_jobs_public():
    secret = request.args.get("key") or (request.get_json() or {}).get("key", "")
    if secret != current_app.config.get("SCRAPE_SECRET", "trampo-scrape-2025"):
        return jsonify({"error": "Chave inválida"}), 403
    try:
        from services.job_scraper import run_full_scrape
        result = run_full_scrape()
        return jsonify({
            "message":      f"✅ {result['total_saved']} novas vagas salvas!",
            "total_fetched": result["total_fetched"],
            "total_saved":   result["total_saved"],
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Stats ─────────────────────────────────────────────────────
@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    user, err = _require_admin()
    if err: return err
    return jsonify({
        "users":        User.query.count(),
        "candidates":   User.query.filter_by(role="candidate").count(),
        "recruiters":   User.query.filter_by(role="recruiter").count(),
        "premium":      User.query.filter_by(is_premium=True).count(),
        "jobs":         Job.query.count(),
        "active_jobs":  Job.query.filter_by(status="active").count(),
        "applications": Application.query.count(),
    }), 200


# ── Publicar vaga manualmente (admin) ─────────────────────────
@admin_bp.route("/jobs", methods=["POST"])
def admin_post_job():
    """Publica vaga direto sem pagamento. Protegido por chave."""
    secret = request.args.get("key") or (request.get_json() or {}).get("key", "")
    if secret != current_app.config.get("SCRAPE_SECRET", "trampo-scrape-2025"):
        return jsonify({"error": "Chave inválida"}), 403

    data  = request.get_json() or {}
    title = (data.get("title") or "").strip()
    company = (data.get("company") or "").strip()
    description = (data.get("description") or "").strip()

    if not title or not company or not description:
        return jsonify({"error": "title, company e description são obrigatórios"}), 400

    job = Job(
        title            = title,
        company          = company,
        description      = description,
        location         = data.get("location", ""),
        cidade           = data.get("cidade", ""),
        estado           = data.get("estado", ""),
        work_mode        = data.get("work_mode", "onsite"),
        contract_type    = data.get("contract_type", "clt"),
        salary_min       = data.get("salary_min"),
        salary_max       = data.get("salary_max"),
        required_skills  = data.get("required_skills", ""),
        required_experience = data.get("required_experience", 0),
        contact_email    = data.get("contact_email", ""),
        benefits         = data.get("benefits", ""),
        source           = "admin",
        status           = "active",
        is_paid          = True,
        posted_at        = datetime.now(timezone.utc),
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "✅ Vaga publicada!", "job_id": job.id}), 201


# ── Listar vagas (admin) ──────────────────────────────────────
@admin_bp.route("/jobs", methods=["GET"])
def admin_list_jobs():
    secret = request.args.get("key", "")
    if secret != current_app.config.get("SCRAPE_SECRET", "trampo-scrape-2025"):
        return jsonify({"error": "Chave inválida"}), 403
    jobs = Job.query.order_by(Job.posted_at.desc()).limit(50).all()
    return jsonify({"jobs": [
        {"id": j.id, "title": j.title, "company": j.company,
         "cidade": j.cidade, "status": j.status, "posted_at": j.posted_at.isoformat()}
        for j in jobs
    ]}), 200


# ── Deletar vaga (admin) ──────────────────────────────────────
@admin_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
def admin_delete_job(job_id):
    secret = request.args.get("key", "")
    if secret != current_app.config.get("SCRAPE_SECRET", "trampo-scrape-2025"):
        return jsonify({"error": "Chave inválida"}), 403
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Vaga não encontrada"}), 404
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "✅ Vaga deletada"}), 200


# ── Listar usuários ───────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    user, err = _require_admin()
    if err: return err
    page     = max(1, int(request.args.get("page", 1)))
    per_page = 20
    total    = User.query.count()
    users    = User.query.order_by(User.created_at.desc()) \
                   .offset((page-1)*per_page).limit(per_page).all()
    return jsonify({"users": [u.to_dict() for u in users], "total": total, "page": page}), 200


# ── Promover usuário ──────────────────────────────────────────
@admin_bp.route("/promote/<int:user_id>", methods=["POST"])
@jwt_required()
def promote_user(user_id):
    admin, err = _require_admin()
    if err: return err
    data   = request.get_json() or {}
    role   = data.get("role", "admin")
    target = db.session.get(User, user_id)
    if not target:
        return jsonify({"error": "Usuário não encontrado"}), 404
    target.role = role
    db.session.commit()
    return jsonify({"message": f"Usuário {target.name} promovido para {role}. ✅"}), 200
