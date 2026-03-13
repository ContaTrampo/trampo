"""TRAMPO v7 — Rotas de Vagas"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from database import db
from models import Job, User

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


def _geocode_cep(cep: str) -> tuple[float | None, float | None]:
    """Geocodifica CEP via ViaCEP + Nominatim (gratuito)."""
    import re, requests
    cep_clean = re.sub(r"\D", "", cep)
    if len(cep_clean) != 8:
        return None, None
    try:
        via = requests.get(f"https://viacep.com.br/ws/{cep_clean}/json/", timeout=5)
        data = via.json()
        if data.get("erro"):
            return None, None
        addr = f"{data.get('logradouro','')}, {data.get('localidade','')}, {data.get('uf','')}, Brazil"
        nom = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": addr, "format": "json", "limit": 1},
            headers={"User-Agent": "trampo-app/7.0"},
            timeout=8
        )
        results = nom.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"⚠️ Geocode falhou: {e}")
    return None, None


@jobs_bp.route("/", methods=["GET"])
def list_jobs():
    """Lista vagas com filtros. Público."""
    q            = (request.args.get("q") or "").strip()
    city         = (request.args.get("city") or "").strip()
    work_mode    = request.args.get("work_mode")
    contract     = request.args.get("contract_type")
    salary_min   = request.args.get("salary_min", type=int)
    with_map     = request.args.get("map") == "1"  # inclui lat/lng
    page         = max(1, int(request.args.get("page", 1)))
    per_page     = int(request.args.get("per_page", 12))

    query = Job.query.filter_by(status="active")
    if q:
        query = query.filter(
            db.or_(
                Job.title.ilike(f"%{q}%"),
                Job.company.ilike(f"%{q}%"),
                Job.required_skills.ilike(f"%{q}%"),
                Job.description.ilike(f"%{q}%"),
            )
        )
    if city:
        query = query.filter(Job.cidade.ilike(f"%{city}%"))
    if work_mode:
        query = query.filter(Job.work_mode == work_mode)
    if contract:
        query = query.filter(Job.contract_type == contract)
    if salary_min:
        query = query.filter(db.or_(Job.salary_min >= salary_min, Job.salary_min == None))

    source = request.args.get("source")
    if source:
        query = query.filter(Job.source == source)

    total = query.count()
    jobs  = query.order_by(Job.is_featured.desc(), Job.posted_at.desc()) \
                 .offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "jobs":     [j.to_dict() for j in jobs],
        "total":    total,
        "page":     page,
        "pages":    (total + per_page - 1) // per_page,
    }), 200


@jobs_bp.route("/map", methods=["GET"])
def jobs_for_map():
    """Retorna vagas com coordenadas para o mapa."""
    city = (request.args.get("city") or "").strip()
    query = Job.query.filter(Job.status == "active", Job.latitude != None)
    if city:
        query = query.filter(Job.cidade.ilike(f"%{city}%"))
    jobs  = query.limit(200).all()
    return jsonify({"jobs": [
        {"id": j.id, "title": j.title, "company": j.company,
         "lat": j.latitude, "lng": j.longitude,
         "work_mode": j.work_mode, "salary_min": j.salary_min}
        for j in jobs
    ]}), 200


@jobs_bp.route("/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = db.get_or_404(Job, job_id)
    return jsonify({"job": job.to_dict()}), 200


@jobs_bp.route("/", methods=["POST"])
@jwt_required()
def create_job():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    if user.role not in ("recruiter", "admin"):
        return jsonify({"error": "Apenas recrutadores podem publicar vagas"}), 403

    data = request.get_json() or {}
    required = ["title", "company", "description"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"'{f}' é obrigatório"}), 400

    # Geocodifica se tiver CEP
    lat = lng = None
    if data.get("cep"):
        lat, lng = _geocode_cep(data["cep"])

    job = Job(
        recruiter_id        = user_id,
        title               = data["title"][:200],
        company             = data["company"][:200],
        description         = data["description"],
        location            = data.get("location", ""),
        cidade              = data.get("cidade", ""),
        estado              = data.get("estado", ""),
        latitude            = lat or data.get("latitude"),
        longitude           = lng or data.get("longitude"),
        contract_type       = data.get("contract_type", "clt"),
        salary_min          = data.get("salary_min"),
        salary_max          = data.get("salary_max"),
        work_mode           = data.get("work_mode", "onsite"),
        required_skills     = data.get("required_skills", ""),
        required_experience = data.get("required_experience", 0),
        contact_email       = data.get("contact_email", ""),
        contact_whatsapp    = data.get("contact_whatsapp", ""),
        benefits            = data.get("benefits", ""),
        # Vaga publicada pelo recrutador fica pendente de pagamento
        status              = "pending_payment",
        is_paid             = False,
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({
        "message":  "Vaga criada! Efetue o pagamento para publicar. 💳",
        "job":      job.to_dict(),
        "job_id":   job.id,
    }), 201


@jobs_bp.route("/<int:job_id>", methods=["PUT"])
@jwt_required()
def update_job(job_id):
    user_id = int(get_jwt_identity())
    job     = db.get_or_404(Job, job_id)
    if job.recruiter_id != user_id:
        return jsonify({"error": "Sem permissão"}), 403

    data = request.get_json() or {}
    editable = ["title", "company", "description", "location", "cidade", "estado",
                "contract_type", "salary_min", "salary_max", "work_mode",
                "required_skills", "required_experience", "contact_email",
                "contact_whatsapp", "benefits", "status"]
    for f in editable:
        if f in data:
            setattr(job, f, data[f])

    if data.get("cep"):
        lat, lng = _geocode_cep(data["cep"])
        if lat:
            job.latitude, job.longitude = lat, lng

    db.session.commit()
    return jsonify({"message": "Vaga atualizada! ✅", "job": job.to_dict()}), 200


@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    job     = db.get_or_404(Job, job_id)
    if job.recruiter_id != user_id and user.role != "admin":
        return jsonify({"error": "Sem permissão"}), 403
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Vaga removida."}), 200


@jobs_bp.route("/matching", methods=["GET"])
@jwt_required()
def matched_jobs():
    """Vagas ranqueadas por compatibilidade com o candidato logado."""
    user_id   = int(get_jwt_identity())
    min_score = float(request.args.get("min_score", 0))
    limit     = int(request.args.get("limit", 20))
    from services.matching_engine import find_top_jobs
    jobs = find_top_jobs(user_id, limit=limit, min_score=min_score)
    return jsonify({"jobs": jobs, "total": len(jobs)}), 200
