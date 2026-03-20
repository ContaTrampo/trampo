"""TRAMPO v8 — Autenticação"""
import os, secrets
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from database import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ── Registro ──────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json() or {}
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "")
    role     = data.get("role", "candidate")

    if not name or not email or not password:
        return jsonify({"error": "Nome, email e senha são obrigatórios"}), 400
    if len(password) < 6:
        return jsonify({"error": "Senha precisa ter pelo menos 6 caracteres"}), 400
    if role not in ("candidate", "recruiter"):
        role = "candidate"
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Este email já está cadastrado"}), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    # Email em background — não bloqueia a resposta
    try:
        from services.email_service import send_welcome_email
        send_welcome_email(user)
    except Exception as e:
        print(f"⚠️ Email boas-vindas falhou (não crítico): {e}")

    return jsonify({
        "message": "Conta criada com sucesso! ✅",
        "token":   token,
        "user":    user.to_dict(),
    }), 201


# ── Login ─────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Email ou senha incorretos"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login realizado! ✅",
        "token":   token,
        "user":    user.to_dict(),
    }), 200


# ── Meu perfil ────────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify({"user": user.to_dict()}), 200


# ── Esqueci a senha ───────────────────────────────────────────
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data  = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Email obrigatório"}), 400

    user = User.query.filter_by(email=email).first()

    # Sempre retorna sucesso (segurança — não revela se email existe)
    if not user:
        return jsonify({"message": "Se este email existir, você receberá um link em breve."}), 200

    # Gera token seguro com validade de 2 horas
    token  = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(hours=2)

    user.reset_token        = token
    user.reset_token_expiry = expiry
    db.session.commit()

    try:
        from services.email_service import send_password_reset_email
        send_password_reset_email(user, token)
    except Exception as e:
        print(f"⚠️ Email reset falhou: {e}")
        return jsonify({"error": "Erro ao enviar email. Tente novamente."}), 500

    return jsonify({"message": "Link de recuperação enviado! Verifique seu email. ✅"}), 200


# ── Redefinir senha ───────────────────────────────────────────
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data         = request.get_json() or {}
    token        = (data.get("token") or "").strip()
    new_password = (data.get("password") or "")

    if not token or not new_password:
        return jsonify({"error": "Token e nova senha são obrigatórios"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "Senha precisa ter pelo menos 6 caracteres"}), 400

    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return jsonify({"error": "Token inválido"}), 400

    # Verifica se não expirou
    if user.reset_token_expiry:
        expiry = user.reset_token_expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry:
            return jsonify({"error": "Token expirado. Solicite um novo link."}), 400

    user.set_password(new_password)
    user.reset_token        = None
    user.reset_token_expiry = None
    db.session.commit()

    return jsonify({"message": "Senha redefinida com sucesso! ✅"}), 200


# ── Alterar senha (logado) ────────────────────────────────────
@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user_id      = int(get_jwt_identity())
    user         = db.session.get(User, user_id)
    data         = request.get_json() or {}
    current_pass = data.get("current_password", "")
    new_pass     = data.get("new_password", "")

    if not user.check_password(current_pass):
        return jsonify({"error": "Senha atual incorreta"}), 400
    if len(new_pass) < 6:
        return jsonify({"error": "Nova senha precisa ter pelo menos 6 caracteres"}), 400

    user.set_password(new_pass)
    db.session.commit()
    return jsonify({"message": "Senha alterada com sucesso! ✅"}), 200


# ── Testar email ──────────────────────────────────────────────
@auth_bp.route("/test-email", methods=["GET"])
def test_email():
    try:
        from services.email_service import _send, _wrap
        html = _wrap("""
          <h2 style="color:#0f172a">Teste de Email ✅</h2>
          <p style="color:#475569;font-size:15px">
            O sistema de email do TRAMPO está funcionando corretamente!
          </p>
        """, "Teste — TRAMPO")
        ok = _send(
            to      = os.environ.get("MAIL_USERNAME", "bemvindo.trampo@gmail.com"),
            subject = "✅ Teste TRAMPO — Email funcionando!",
            html    = html,
        )
        if ok:
            return jsonify({"enviado": True,  "para": os.environ.get("MAIL_USERNAME")}), 200
        else:
            return jsonify({"enviado": False, "dica": "Verifique os logs do Render"}), 500
    except Exception as e:
        return jsonify({"enviado": False, "erro": str(e)}), 500
