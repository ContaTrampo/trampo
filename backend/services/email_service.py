"""TRAMPO v8 — Email via Brevo SMTP (gratuito, 300/dia) + WhatsApp via CallMeBot (gratuito)"""
import os
import smtplib
import requests  # necessário para WhatsApp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta


def _saudacao() -> str:
    """Retorna 'Bom dia', 'Boa tarde' ou 'Boa noite' baseado no horário de Brasília."""
    hora = datetime.now(timezone(timedelta(hours=-3))).hour
    if hora < 12:
        return "Bom dia"
    if hora < 18:
        return "Boa tarde"
    return "Boa noite"


def _send(to: str, subject: str, html: str, text: str = "") -> bool:
    user = os.environ.get("BREVO_SMTP_USER", "")
    pwd  = os.environ.get("BREVO_SMTP_PASS", "")
    from_email = os.environ.get("MAIL_USERNAME", "bemvindo.trampo@gmail.com")

    if not user or not pwd:
        print(f"⚠️ BREVO_SMTP_USER ou BREVO_SMTP_PASS não configurados")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"TRAMPO <{from_email}>"
        msg["To"]      = to

        if text:
            msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP("smtp-relay.brevo.com", 587, timeout=20) as srv:
            srv.ehlo()
            srv.starttls()
            srv.login(user, pwd)
            srv.sendmail(from_email, to, msg.as_string())

        print(f"✅ Email enviado via Brevo → {to}")
        return True
    except Exception as e:
        print(f"❌ Erro email Brevo {to}: {e}")
        return False


def _wrap(body_html: str, title: str = "TRAMPO") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{title}</title></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;background:#f8fafc;margin:0;padding:0">
<div style="max-width:600px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)">
  <div style="background:linear-gradient(135deg,#10b981,#059669);padding:32px 40px;text-align:center">
    <div style="font-size:28px;font-weight:800;color:#fff;letter-spacing:-1px">TRAMP<span style="color:#d1fae5">O</span></div>
    <div style="color:rgba(255,255,255,.8);font-size:13px;margin-top:4px">Conectando talentos a oportunidades</div>
  </div>
  <div style="padding:40px">{body_html}</div>
  <div style="background:#f8fafc;padding:24px 40px;text-align:center;border-top:1px solid #e2e8f0">
    <p style="color:#94a3b8;font-size:12px;margin:0">© 2025 TRAMPO · <a href="mailto:bemvindo.trampo@gmail.com" style="color:#10b981">bemvindo.trampo@gmail.com</a></p>
  </div>
</div>
</body></html>"""


def _btn(url: str, label: str, color: str = "#10b981") -> str:
    return f"""<div style="text-align:center;margin:28px 0">
  <a href="{url}" style="background:{color};color:#fff;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:700;font-size:15px;display:inline-block">{label}</a>
</div>"""


def send_verification_email(user, token: str) -> bool:
    base = os.environ.get("BASE_URL", "https://trampo-gamma.vercel.app")
    url  = f"{base}/pages/verify-email.html?token={token}"
    saud = _saudacao()
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Bem-vindo ao TRAMPO, {user.name.split()[0]}! 🎉</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 20px">
        {saud}, <strong>{user.name.split()[0]}</strong>! Confirme seu email para ativar sua conta e começar a encontrar vagas incríveis.
      </p>
      {_btn(url, '✉️ Confirmar meu Email')}
      <p style="color:#94a3b8;font-size:13px;text-align:center">Este link expira em <strong>24 horas</strong>.</p>
    """, "Confirme seu email — TRAMPO")
    return _send(user.email, "✉️ Confirme seu email no TRAMPO", html)


def send_password_reset_email(user, token: str) -> bool:
    base = os.environ.get("BASE_URL", "https://trampo-gamma.vercel.app")
    url  = f"{base}/pages/forgot-password.html?token={token}"
    saud = _saudacao()
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Redefinição de Senha 🔐</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 20px">
        {saud}, <strong>{user.name.split()[0]}</strong>! Recebemos uma solicitação para redefinir a senha de <strong>{user.email}</strong>.
      </p>
      {_btn(url, '🔑 Redefinir minha Senha', '#6366f1')}
      <p style="color:#94a3b8;font-size:13px;text-align:center">
        Este link expira em <strong>2 horas</strong>.<br>
        Se não foi você, ignore este email.
      </p>
    """, "Redefinição de senha — TRAMPO")
    return _send(user.email, "🔑 Redefinição de senha no TRAMPO", html)


def send_welcome_email(user) -> bool:
    base = os.environ.get("BASE_URL", "https://trampo-gamma.vercel.app")
    saud = _saudacao()
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Conta ativada! Vamos começar 🚀</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        {saud}, <strong>{user.name.split()[0]}</strong>! Sua conta foi ativada!
        Complete seu perfil para receber vagas compatíveis.
      </p>
      {_btn(f"{base}/pages/profile.html", '👤 Completar meu Perfil')}
    """, "Bem-vindo ao TRAMPO!")
    return _send(user.email, "🎉 Bem-vindo ao TRAMPO! Sua conta está ativa", html)


def send_application_email(user, job, application) -> bool:
    score_color = "#10b981" if application.match_score >= 75 else "#f59e0b"
    saud = _saudacao()
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Currículo enviado! ✅</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        {saud}, <strong>{user.name.split()[0]}</strong>! Seu currículo chegou em <strong>{job.company}</strong>!
      </p>
      <div style="background:#f8fafc;border-radius:12px;padding:24px;margin-bottom:24px;border-left:4px solid #10b981">
        <div><span style="color:#64748b;font-size:13px">Vaga</span>
             <div style="font-weight:700;color:#0f172a">{job.title}</div></div>
        <div style="margin-top:10px"><span style="color:#64748b;font-size:13px">Empresa</span>
             <div style="font-weight:700;color:#0f172a">{job.company}</div></div>
        <div style="margin-top:10px"><span style="color:#64748b;font-size:13px">Compatibilidade</span>
             <div style="font-weight:800;color:{score_color};font-size:20px">{round(application.match_score)}%</div></div>
      </div>
      <p style="color:#94a3b8;font-size:13px;text-align:center">Boa sorte! 🤞</p>
    """, "Currículo enviado — TRAMPO")
    _send(user.email, f"✅ Currículo enviado para {job.company}", html)
    if job.contact_email:
        html2 = _wrap(f"""
          <h2 style="color:#0f172a;margin:0 0 8px">Nova candidatura 🎯</h2>
          <p style="color:#475569;font-size:15px">
            {saud}, <strong>{job.company}</strong>! <strong>{user.name}</strong> se candidatou à vaga <strong>{job.title}</strong>
            com <strong style="color:#10b981">{round(application.match_score)}%</strong> de compatibilidade.
            Email: {user.email}
          </p>
        """, "Nova candidatura — TRAMPO")
        _send(job.contact_email, f"🎯 Candidatura: {user.name} — {job.title}", html2)
    return True


def send_support_confirmation(user, ticket) -> bool:
    sla  = "2 horas" if user.is_premium else "24 horas"
    saud = _saudacao()
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Mensagem recebida ✅</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7">
        {saud}, <strong>{user.name.split()[0]}</strong>! Responderemos em até <strong>{sla}</strong>.
      </p>
      <div style="background:#f8fafc;border-radius:12px;padding:20px;margin-top:16px">
        <div><span style="color:#64748b;font-size:13px">Ticket #{ticket.id}</span>
             <div style="font-weight:700;color:#0f172a">{ticket.subject}</div></div>
      </div>
    """, "Suporte — TRAMPO")
    return _send(user.email, f"[Ticket #{ticket.id}] Mensagem recebida — TRAMPO", html)


def send_premium_activated(user) -> bool:
    saud = _saudacao()
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Você é Premium! 💎</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7">
        {saud}, <strong>{user.name.split()[0]}</strong>! Parabéns!
        Agora você tem 30 envios/dia e candidatura em destaque.
      </p>
    """, "Premium ativado — TRAMPO")
    # Opcional: enviar também WhatsApp
    if user.phone:
        send_whatsapp(user.phone, f"{saud} {user.name.split()[0]}! Você agora é Premium no TRAMPO. 30 envios/dia, destaques e muito mais. 🚀")
    return _send(user.email, "💎 Bem-vindo ao TRAMPO Premium!", html)


def send_job_payment_confirmation(user, job) -> bool:
    saud = _saudacao()
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Vaga publicada! 🚀</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7">
        {saud}, <strong>{user.name.split()[0]}</strong>! Sua vaga <strong>{job.title}</strong> está no ar!
      </p>
    """, "Vaga publicada — TRAMPO")
    return _send(user.email, f"🚀 Vaga publicada: {job.title}", html)


# ───────────────────────────────────────────────────────────────
# WhatsApp gratuito via CallMeBot (requer cadastro e chave pessoal)
# Alternativas gratuitas caso o CallMeBot não funcione:
#   - Telegram Bot (gratuito, mas usuário precisa ter Telegram)
#   - Twilio (tem trial gratuito, mas depois cobra)
#   - Z-API (não gratuito)
#   - Evolution API (self-hosted, gratuito)
# Por simplicidade, mantemos CallMeBot – o usuário deve obter sua chave em callmebot.com
# ───────────────────────────────────────────────────────────────

def send_whatsapp(phone: str, message: str) -> bool:
    """Envia mensagem WhatsApp via CallMeBot (gratuito para teste)."""
    try:
        import urllib.parse
        api_key = os.environ.get("CALLMEBOT_API_KEY", "")
        if not api_key:
            print("⚠️ CALLMEBOT_API_KEY não configurada")
            return False

        # Remove caracteres não numéricos e adiciona código do Brasil se necessário
        phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not phone_clean.startswith("55"):
            phone_clean = "55" + phone_clean

        url = f"https://api.callmebot.com/whatsapp.php?phone={phone_clean}&text={urllib.parse.quote(message)}&apikey={api_key}"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            print(f"✅ WhatsApp enviado para {phone_clean}")
            return True
        else:
            print(f"❌ WhatsApp falhou: {resp.text}")
            return False
    except Exception as e:
        print(f"⚠️ Erro WhatsApp: {e}")
        return False
