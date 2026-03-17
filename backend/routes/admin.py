"""TRAMPO v8 — Admin"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Job, Application

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
@admin_bp.route("/scrape-jobs", methods=["GET", "POST"])
def scrape_jobs_public():
    """Dispara scraping sem login — protegido por chave secreta."""
    from flask import current_app
    secret = request.args.get("key") or (request.get_json() or {}).get("key", "")
    if secret != current_app.config.get("SCRAPE_SECRET", "trampo-scrape-2025"):
        return jsonify({"error": "Chave inválida"}), 403
    try:
        from services.job_scraper import run_full_scrape
        result = run_full_scrape()
        return jsonify({
            "message": f"✅ {result['total_saved']} novas vagas salvas!",
            "total_fetched": result["total_fetched"],
            "total_saved":   result["total_saved"],
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Commit changes.**

Depois que o Render atualizar (~2 min), acessa:
```
https://trampo-api-9nux.onrender.com/api/admin/scrape-jobs?key=trampo-scrape-2025

def _require_admin():
    uid  = int(get_jwt_identity())
    user = db.session.get(User, uid)
    if not user or user.role != "admin":
        return None, (jsonify({"error": "Acesso negado"}), 403)
    return user, None


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    user, err = _require_admin()
    if err:
        return err
    return jsonify({
        "users":        User.query.count(),
        "candidates":   User.query.filter_by(role="candidate").count(),
        "recruiters":   User.query.filter_by(role="recruiter").count(),
        "premium":      User.query.filter_by(is_premium=True).count(),
        "jobs":         Job.query.count(),
        "active_jobs":  Job.query.filter_by(status="active").count(),
        "applications": Application.query.count(),
    }), 200


@admin_bp.route("/scrape-jobs", methods=["POST"])
@jwt_required()
def scrape_jobs():
    """Dispara scraping de vagas manualmente (só admin)."""
    user, err = _require_admin()
    if err:
        return err

    try:
        from services.job_scraper import run_full_scrape
        result = run_full_scrape()
        return jsonify({
            "message": f"Scraping concluído! {result['total_saved']} novas vagas salvas. ✅",
            "result":  result,
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro no scraping: {str(e)}"}), 500


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    user, err = _require_admin()
    if err:
        return err
    page     = max(1, int(request.args.get("page", 1)))
    per_page = 20
    total    = User.query.count()
    users    = User.query.order_by(User.created_at.desc()) \
                   .offset((page-1)*per_page).limit(per_page).all()
    return jsonify({
        "users": [u.to_dict() for u in users],
        "total": total,
        "page":  page,
    }), 200


@admin_bp.route("/promote/<int:user_id>", methods=["POST"])
@jwt_required()
def promote_user(user_id):
    admin, err = _require_admin()
    if err:
        return err
    data = request.get_json() or {}
    role = data.get("role", "admin")
    target = db.session.get(User, user_id)
    if not target:
        return jsonify({"error": "Usuário não encontrado"}), 404
    target.role = role
    db.session.commit()
    return jsonify({"message": f"Usuário {target.name} promovido para {role}. ✅"}), 200
