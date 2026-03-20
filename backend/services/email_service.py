"""TRAMPO v8 — Email via Brevo HTTP API (funciona no Render free)"""
import os, json, requests
from datetime import datetime, timezone, timedelta


def _saudacao() -> str:
    hora = datetime.now(timezone(timedelta(hours=-3))).hour
    if hora < 12:  return "Bom dia"
    if hora < 18:  return "Boa tarde"
    return "Boa noite"


def _send(to: str, subject: str, html: str, text: str = "") -> bool:
    api_key    = os.environ.get("BREVO_API_KEY", "")
    from_email = os.environ.get("MAIL_USERNAME", "bemvindo.trampo@gmail.com")
    from_name  = "TRAMPO"

    if not api_key:
        print(f"⚠️ BREVO_API_KEY não configurada")
        return False
    try:
        payload = {
            "sender":      {"name": from_name, "email": from_email},
            "to":          [{"email": to}],
            "subject":     subject,
            "htmlContent": html,
        }
        if text:
            payload["textContent"] = text

        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key":      api_key,
                "Content-Type": "application/json",
                "Accept":       "application/json",
            },
            json=payload,
            timeout=15,
        )

        if resp.status_code in (200, 201):
            print(f"✅ Email enviado via Brevo API → {to}")
            return True
        else:
            print(f"❌ Brevo API erro {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Erro email {to}: {e}")
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
    <p style="color:#94a3b8;font-size:12px;margin:0">© 2026 TRAMPO · <a href="mailto:bemvindo.trampo@gmail.com" style="color:#10b981">bemvindo.trampo@gmail.com</a></p>
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
        {saud}, <strong>{user.name.split()[0]}</strong>! Confirme seu email para ativar sua conta.
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
        {saud}, <strong>{user.name.split()[0]}</strong>! Recebemos uma solicitação para redefinir sua senha.
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
        {saud}, <strong>{user.name.split()[0]}</strong>! Sua conta foi ativada.
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
        saud2 = _saudacao()
        html2 = _wrap(f"""
          <h2 style="color:#0f172a;margin:0 0 8px">Nova candidatura 🎯</h2>
          <p style="color:#475569;font-size:15px">
            {saud2}! <strong>{user.name}</strong> se candidatou à vaga <strong>{job.title}</strong>
            com <strong style="color:#10b981">{round(application.match_score)}%</strong> de compatibilidade.<br>
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
        Agora você tem 30 envios/dia e candidatura em destaque. 🚀
      </p>
    """, "Premium ativado — TRAMPO")
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


def send_whatsapp(phone: str, message: str) -> bool:
    """WhatsApp pausado — implementar futuramente."""
    print(f"⚠️ WhatsApp não configurado para {phone}")
    return False
```
