"""TRAMPO v7 — Autenticação completa"""
import secrets
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, CandidateProfile, RecruiterProfile
from services.validators import validate_cpf, format_cpf, validate_password, validate_email
from services.email_service import send_verification_email, send_welcome_email, send_password_reset_email

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json() or {}
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role     = data.get("role", "candidate")
    cpf_raw  = re.sub(r"\D", "", data.get("cpf") or "") if data.get("cpf") else None

    # Importar re localmente
    import re

    # Validações básicas
    if not name or not email or not password:
        return jsonify({"error": "Nome, email e senha são obrigatórios"}), 400
    if not validate_email(email):
        return jsonify({"error": "Email inválido"}), 400

    ok, msg = validate_password(password)
    if not ok:
        return jsonify({"error": msg}), 400

    if cpf_raw:
        if not validate_cpf(cpf_raw):
            return jsonify({"error": "CPF inválido"}), 400
        if User.query.filter_by(cpf=format_cpf(cpf_raw)).first():
            return jsonify({"error": "CPF já cadastrado"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Este email já está cadastrado"}), 409

    if role not in ("candidate", "recruiter"):
        role = "candidate"

    # Gera token de verificação
    token   = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        cpf=format_cpf(cpf_raw) if cpf_raw else None,
        phone=(data.get("phone") or "").strip() or None,
        sexo=data.get("sexo") or None,
        cep=(data.get("cep") or "").strip() or None,
        logradouro=(data.get("logradouro") or "").strip() or None,
        numero=(data.get("numero") or "").strip() or None,
        complemento=(data.get("complemento") or "").strip() or None,
        bairro=(data.get("bairro") or "").strip() or None,
        cidade=(data.get("cidade") or "").strip() or None,
        estado=(data.get("estado") or "").strip() or None,
        email_verified=False,
        email_verification_token=token,
        email_verification_expires=expires,
    )

    if data.get("birth_date"):
        try:
            from datetime import date
            user.birth_date = date.fromisoformat(data["birth_date"])
        except Exception:
            pass

    db.session.add(user)
    db.session.flush()

    if role == "candidate":
        db.session.add(CandidateProfile(user_id=user.id))
    elif role == "recruiter":
        db.session.add(RecruiterProfile(
            user_id=user.id,
            company_name=(data.get("company_name") or "").strip() or None,
        ))

    db.session.commit()

    try:
        send_verification_email(user, token)
    except Exception as e:
        print(f"⚠️ Email de verificação falhou: {e}")

    jwt_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token":   jwt_token,
        "user":    user.to_dict(),
        "message": "Conta criada! Verifique seu email para ativar a conta. ✉️",
    }), 201


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    data  = request.get_json() or {}
    token = (data.get("token") or "").strip()
    if not token:
        return jsonify({"error": "Token inválido"}), 400

    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        return jsonify({"error": "Link de verificação inválido ou já usado"}), 404

    if user.email_verification_expires:
        exp = user.email_verification_expires
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            return jsonify({"error": "Link expirado. Solicite um novo."}), 410

    user.email_verified = True
    user.email_verification_token   = None
    user.email_verification_expires = None
    db.session.commit()

    try:
        send_welcome_email(user)
    except Exception:
        pass

    jwt_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token":   jwt_token,
        "user":    user.to_dict(),
        "message": "Email confirmado! Bem-vindo ao TRAMPO! 🎉",
    }), 200


@auth_bp.route("/resend-verification", methods=["POST"])
@jwt_required()
def resend_verification():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    if user.email_verified:
        return jsonify({"message": "Email já verificado"}), 200

    token   = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    user.email_verification_token   = token
    user.email_verification_expires = expires
    db.session.commit()

    send_verification_email(user, token)
    return jsonify({"message": "Email de verificação reenviado! ✉️"}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Email ou senha incorretos"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "token":          token,
        "user":           user.to_dict(),
        "email_verified": user.email_verified,
    }), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data  = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email é obrigatório"}), 400

    user = User.query.filter_by(email=email).first()
    # Sempre retorna 200 para não revelar se email existe
    if user:
        token   = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=2)
        user.password_reset_token   = token
        user.password_reset_expires = expires
        db.session.commit()
        try:
            send_password_reset_email(user, token)
        except Exception as e:
            print(f"⚠️ Email reset falhou: {e}")

    return jsonify({
        "message": "Se este email estiver cadastrado, você receberá as instruções. ✉️"
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data     = request.get_json() or {}
    token    = (data.get("token") or "").strip()
    password = data.get("password") or ""

    if not token or not password:
        return jsonify({"error": "Token e senha são obrigatórios"}), 400

    ok, msg = validate_password(password)
    if not ok:
        return jsonify({"error": msg}), 400

    user = User.query.filter_by(password_reset_token=token).first()
    if not user:
        return jsonify({"error": "Link inválido ou já utilizado"}), 404

    if user.password_reset_expires:
        exp = user.password_reset_expires
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            return jsonify({"error": "Link expirado. Solicite um novo."}), 410

    user.password_hash          = generate_password_hash(password)
    user.password_reset_token   = None
    user.password_reset_expires = None
    db.session.commit()

    return jsonify({"message": "Senha redefinida com sucesso! Faça login. 🔓"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id  = int(get_jwt_identity())
    user     = db.session.get(User, user_id)
    data     = request.get_json() or {}
    current  = data.get("current_password", "")
    new_pass = data.get("new_password", "")

    if not check_password_hash(user.password_hash, current):
        return jsonify({"error": "Senha atual incorreta"}), 400

    ok, msg = validate_password(new_pass)
    if not ok:
        return jsonify({"error": msg}), 400

    user.password_hash = generate_password_hash(new_pass)
    db.session.commit()
    return jsonify({"message": "Senha alterada com sucesso! ✅"}), 200
