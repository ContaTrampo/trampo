"""TRAMPO v7 — Suporte"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, SupportTicket
from services.email_service import send_support_confirmation

support_bp = Blueprint("support", __name__, url_prefix="/api/support")


@support_bp.route("/", methods=["POST"])
@jwt_required()
def create_ticket():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    data    = request.get_json() or {}
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not subject or not message:
        return jsonify({"error": "Assunto e mensagem são obrigatórios"}), 400

    ticket = SupportTicket(
        user_id  = user_id,
        subject  = subject[:200],
        message  = message[:5000],
        priority = "high" if user.is_premium else "normal",
    )
    db.session.add(ticket)
    db.session.commit()

    try:
        send_support_confirmation(user, ticket)
    except Exception as e:
        print(f"⚠️ Email suporte falhou: {e}")

    return jsonify({
        "message":   f"Ticket #{ticket.id} criado! Respondemos em {'2 horas' if user.is_premium else '24 horas'}. ✅",
        "ticket_id": ticket.id,
    }), 201


@support_bp.route("/", methods=["GET"])
@jwt_required()
def my_tickets():
    user_id = int(get_jwt_identity())
    tickets = SupportTicket.query.filter_by(user_id=user_id) \
                  .order_by(SupportTicket.created_at.desc()).all()
    return jsonify({"tickets": [
        {"id": t.id, "subject": t.subject, "status": t.status,
         "priority": t.priority, "created_at": t.created_at.isoformat()}
        for t in tickets
    ]}), 200
