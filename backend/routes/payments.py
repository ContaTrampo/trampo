"""TRAMPO v7 — Pagamentos Stripe
  • Recrutador: R$ 50 por vaga publicada (pagamento único)
  • Candidato:  R$ 29/mês ou R$ 280/ano (assinatura Premium)
"""
import stripe
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Job
from services.email_service import send_premium_activated, send_job_payment_confirmation

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


def _stripe():
    key = current_app.config.get("STRIPE_SECRET_KEY", "")
    if not key:
        raise ValueError("Stripe não configurado")
    stripe.api_key = key
    return stripe


# ─── CANDIDATO: Assinar Premium ───────────────────────────────

@payments_bp.route("/create-checkout", methods=["POST"])
@jwt_required()
def create_checkout():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    data    = request.get_json() or {}
    plan    = data.get("plan", "monthly")
    base    = current_app.config.get("BASE_URL", "http://localhost:5000")

    try:
        s = _stripe()
    except ValueError as e:
        return jsonify({"error": str(e)}), 503

    amount   = 2900  if plan == "monthly" else 28000
    interval = "month" if plan == "monthly" else "year"

    try:
        params = {
            "payment_method_types": ["card"],
            "mode":                 "subscription",
            "line_items": [{
                "price_data": {
                    "currency":     "brl",
                    "product_data": {"name": "TRAMPO Premium"},
                    "unit_amount":  amount,
                    "recurring":    {"interval": interval},
                },
                "quantity": 1,
            }],
            "success_url": f"{base}/pages/premium.html?success=1",
            "cancel_url":  f"{base}/pages/premium.html",
            "metadata":    {"user_id": str(user_id), "type": "premium"},
        }
        if user.stripe_customer_id:
            params["customer"] = user.stripe_customer_id
        else:
            params["customer_email"] = user.email

        session = s.checkout.Session.create(**params)
        return jsonify({"checkout_url": session.url}), 200
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e.user_message or e)}), 500


# ─── RECRUTADOR: Pagar R$50 por vaga ──────────────────────────

@payments_bp.route("/pay-job/<int:job_id>", methods=["POST"])
@jwt_required()
def pay_for_job(job_id):
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    job     = db.session.get(Job, job_id)
    base    = current_app.config.get("BASE_URL", "http://localhost:5000")

    if not job:
        return jsonify({"error": "Vaga não encontrada"}), 404
    if job.recruiter_id != user_id:
        return jsonify({"error": "Sem permissão"}), 403
    if job.is_paid:
        return jsonify({"error": "Esta vaga já foi paga"}), 409

    try:
        s = _stripe()
    except ValueError as e:
        return jsonify({"error": str(e)}), 503

    try:
        params = {
            "payment_method_types": ["card"],
            "mode":                 "payment",
            "line_items": [{
                "price_data": {
                    "currency":     "brl",
                    "product_data": {"name": f"Publicação de Vaga: {job.title}"},
                    "unit_amount":  5000,   # R$ 50,00
                },
                "quantity": 1,
            }],
            "success_url": f"{base}/pages/recruiter.html?job_paid={job_id}",
            "cancel_url":  f"{base}/pages/recruiter.html",
            "metadata":    {
                "user_id": str(user_id),
                "job_id":  str(job_id),
                "type":    "job_payment",
            },
        }
        if user.stripe_customer_id:
            params["customer"] = user.stripe_customer_id
        else:
            params["customer_email"] = user.email

        session = s.checkout.Session.create(**params)
        # Salva intent provisório
        job.payment_intent_id = session.id
        db.session.commit()
        return jsonify({"checkout_url": session.url}), 200
    except stripe.error.StripeError as e:
        return jsonify({"error": str(e.user_message or e)}), 500


# ─── Webhook Stripe ────────────────────────────────────────────

@payments_bp.route("/webhook", methods=["POST"])
def webhook():
    payload    = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    secret     = current_app.config.get("STRIPE_WEBHOOK_SECRET", "")

    if not secret:
        return jsonify({"error": "Webhook secret não configurado"}), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except Exception:
        return jsonify({"error": "Webhook inválido"}), 400

    obj  = event["data"]["object"]
    meta = obj.get("metadata", {})

    # ── Checkout concluído ────────────────────────────────────
    if event["type"] == "checkout.session.completed":
        tipo = meta.get("type")

        if tipo == "premium":
            uid = meta.get("user_id")
            if uid:
                user = db.session.get(User, int(uid))
                if user:
                    user.is_premium             = True
                    user.premium_expires_at     = datetime.now(timezone.utc) + timedelta(days=31)
                    user.stripe_customer_id     = obj.get("customer")
                    user.stripe_subscription_id = obj.get("subscription")
                    db.session.commit()
                    try:
                        send_premium_activated(user)
                    except Exception:
                        pass

        elif tipo == "job_payment":
            uid = meta.get("user_id")
            jid = meta.get("job_id")
            if uid and jid:
                job  = db.session.get(Job, int(jid))
                user = db.session.get(User, int(uid))
                if job and user:
                    job.is_paid = True
                    job.status  = "active"
                    db.session.commit()
                    try:
                        send_job_payment_confirmation(user, job)
                    except Exception:
                        pass

    # ── Renovação ─────────────────────────────────────────────
    elif event["type"] == "invoice.payment_succeeded":
        sub_id = obj.get("subscription")
        if sub_id:
            user = User.query.filter_by(stripe_subscription_id=sub_id).first()
            if user:
                user.premium_expires_at = datetime.now(timezone.utc) + timedelta(days=31)
                user.is_premium = True
                db.session.commit()

    # ── Cancelamento ──────────────────────────────────────────
    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
        sub_id = obj.get("id")
        if sub_id:
            user = User.query.filter_by(stripe_subscription_id=sub_id).first()
            if user:
                user.is_premium             = False
                user.stripe_subscription_id = None
                db.session.commit()

    return jsonify({"received": True}), 200


@payments_bp.route("/status", methods=["GET"])
@jwt_required()
def premium_status():
    user_id = int(get_jwt_identity())
    user    = db.session.get(User, user_id)
    return jsonify({
        "is_premium":         user.is_premium,
        "premium_expires_at": user.premium_expires_at.isoformat() if user.premium_expires_at else None,
        "daily_limit":        user.get_daily_limit(),
    }), 200
