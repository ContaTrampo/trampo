"""TRAMPO v8 — App Factory"""
import os
from flask import Flask, jsonify, send_from_directory, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from database import db
from config import ActiveConfig


def create_app():
    app = Flask(__name__)
    app.config.from_object(ActiveConfig)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)
    JWTManager(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Blueprints ──────────────────────────────────────────────
    from routes.auth         import auth_bp
    from routes.candidates   import candidates_bp
    from routes.recruiters   import recruiters_bp
    from routes.jobs         import jobs_bp
    from routes.applications import applications_bp
    from routes.payments     import payments_bp
    from routes.support      import support_bp
    from routes.routes_api   import routes_bp
    from routes.matching     import matching_bp
    from routes.admin        import admin_bp
    from routes.reviews      import reviews_bp

    for bp in (auth_bp, candidates_bp, recruiters_bp, jobs_bp,
               applications_bp, payments_bp, support_bp,
               routes_bp, matching_bp, admin_bp, reviews_bp):
        app.register_blueprint(bp)

    # ── Health ────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "8.0"}), 200

    # ── Error handlers ────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Rota não encontrada"}), 404
        frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
        return send_from_directory(frontend, "index.html"), 200

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Método não permitido"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({"error": "Erro interno do servidor"}), 500

    # ── Frontend estático ─────────────────────────────────────
    frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")

    @app.route("/")
    def index():
        return send_from_directory(frontend, "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        if filename.startswith("api/"):
            return jsonify({"error": "Rota não encontrada"}), 404
        return send_from_directory(frontend, filename)

    # ── Bootstrap DB ──────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_demo_jobs()

    # ── Agendamento automático de scraping ────────────────────
    if os.environ.get("FLASK_ENV") == "production":
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            scheduler = BackgroundScheduler(timezone="America/Bahia")

            def scheduled_scrape():
                with app.app_context():
                    from services.job_scraper import run_full_scrape
                    result = run_full_scrape()
                    print(f"✅ Scraping automático: {result}")

            scheduler.add_job(
                scheduled_scrape,
                trigger="cron",
                hour=6,
                minute=0,
            )
            scheduler.start()
            print("⏰ Scraping automático agendado para 06:00h")
        except Exception as e:
            print(f"⚠️ Agendador não iniciou: {e}")

    return app


def _seed_demo_jobs():
    from models import Job
    try:
        if Job.query.count() > 0:
            return
        demo = [
            {"title": "Desenvolvedor Python Sr.", "company": "Tech Corp Brasil",
             "description": "Desenvolvimento com Python, Django e FastAPI.",
             "location": "Salvador, BA", "cidade": "Salvador", "estado": "BA",
             "latitude": -12.9714, "longitude": -38.5014,
             "work_mode": "hybrid", "contract_type": "clt",
             "salary_min": 8000, "salary_max": 12000,
             "required_skills": "Python, Django, FastAPI, PostgreSQL, Docker",
             "required_experience": 4, "contact_email": "jobs@techcorp.com.br",
             "is_paid": True},
            {"title": "Desenvolvedor React Frontend", "company": "StartupX",
             "description": "Interfaces modernas com React, TypeScript e Next.js.",
             "location": "Remoto", "cidade": "Salvador", "estado": "BA",
             "work_mode": "remote", "contract_type": "pj",
             "salary_min": 7000, "salary_max": 11000,
             "required_skills": "React, TypeScript, NextJS, CSS, Git",
             "required_experience": 2, "contact_email": "vagas@startupx.com.br",
             "is_paid": True},
            {"title": "Analista de Marketing Digital", "company": "Agência Digital BA",
             "description": "Gestão de redes sociais, campanhas Google Ads e Meta Ads.",
             "location": "Salvador, BA", "cidade": "Salvador", "estado": "BA",
             "latitude": -12.9714, "longitude": -38.5014,
             "work_mode": "hybrid", "contract_type": "clt",
             "salary_min": 3500, "salary_max": 6000,
             "required_skills": "Google Ads, Meta Ads, SEO, Analytics, Canva",
             "required_experience": 2, "contact_email": "rh@agenciadigital.com.br",
             "is_paid": True},
            {"title": "DevOps Engineer", "company": "CloudBR",
             "description": "Infra em AWS, CI/CD, Kubernetes e Terraform. 100% remoto.",
             "location": "Remoto", "cidade": "Salvador", "estado": "BA",
             "work_mode": "remote", "contract_type": "pj",
             "salary_min": 12000, "salary_max": 20000,
             "required_skills": "AWS, Docker, Kubernetes, Terraform, Linux",
             "required_experience": 4, "contact_email": "hr@cloudbr.io",
             "is_paid": True},
            {"title": "Assistente Administrativo", "company": "Escritório Salvador",
             "description": "Organização de documentos, atendimento ao cliente.",
             "location": "Salvador, BA", "cidade": "Salvador", "estado": "BA",
             "latitude": -12.9714, "longitude": -38.5014,
             "work_mode": "onsite", "contract_type": "clt",
             "salary_min": 1800, "salary_max": 2500,
             "required_skills": "Excel, Word, Organização, Atendimento",
             "required_experience": 1, "contact_email": "rh@escritoriossa.com.br",
             "is_paid": True},
            {"title": "Data Scientist", "company": "Analytics BR",
             "description": "Modelos de machine learning e análise de dados.",
             "location": "São Paulo, SP", "cidade": "São Paulo", "estado": "SP",
             "latitude": -23.5505, "longitude": -46.6333,
             "work_mode": "hybrid", "contract_type": "clt",
             "salary_min": 9000, "salary_max": 15000,
             "required_skills": "Python, Pandas, Scikit-learn, SQL, Tableau",
             "required_experience": 3, "contact_email": "rh@analyticsbr.com",
             "is_paid": True},
            {"title": "UX/UI Designer", "company": "Design Co.",
             "description": "Criação de experiências digitais. Figma e pesquisa com usuários.",
             "location": "Remoto", "cidade": "Curitiba", "estado": "PR",
             "work_mode": "remote", "contract_type": "clt",
             "salary_min": 5000, "salary_max": 9000,
             "required_skills": "Figma, UX Research, UI Design, Prototyping",
             "required_experience": 2, "contact_email": "designers@designco.com.br",
             "is_paid": True},
            {"title": "Analista de Dados Jr.", "company": "iFood",
             "description": "SQL, Python e dashboards no Power BI.",
             "location": "Osasco, SP", "cidade": "Osasco", "estado": "SP",
             "latitude": -23.5329, "longitude": -46.7919,
             "work_mode": "hybrid", "contract_type": "clt",
             "salary_min": 4000, "salary_max": 7000,
             "required_skills": "SQL, Python, Excel, Power BI",
             "required_experience": 1, "contact_email": "vagas@ifood.com.br",
             "is_paid": True},
        ]
        for j in demo:
            db.session.add(Job(**j))
        db.session.commit()
        print(f"✅ {len(demo)} vagas demo criadas.")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Seed falhou: {e}")


if __name__ == "__main__":
    app  = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print(f"\n🚀  TRAMPO v8 em http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
