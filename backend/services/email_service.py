"""TRAMPO v8 — Email via Resend (HTTP, funciona no Render free)"""
import os, json, urllib.request, urllib.error
from flask import current_app


def _send(to: str, subject: str, html: str, text: str = "") -> bool:
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        print(f"⚠️ RESEND_API_KEY não configurada → {to} | {subject}")
        return False
    try:
        payload = json.dumps({
            "from":    "TRAMPO <onboarding@resend.dev>",
            "to":      [to],
            "subject": subject,
            "html":    html,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"✅ Email enviado → {to} | id: {result.get('id')}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"❌ Resend erro {e.code}: {body}")
        return False
    except Exception as e:
        print(f"❌ Erro email {to}: {e}")
        return False


def _wrap(body_html: str, title: str = "TRAMPO") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title></head>
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
    base = os.environ.get("BASE_URL", "https://trampoinc.netlify.app")
    url  = f"{base}/pages/verify-email.html?token={token}"
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Bem-vindo ao TRAMPO, {user.name.split()[0]}! 🎉</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 20px">
        Confirme seu email para ativar sua conta e começar a encontrar vagas incríveis.
      </p>
      {_btn(url, '✉️ Confirmar meu Email')}
      <p style="color:#94a3b8;font-size:13px;text-align:center">Este link expira em <strong>24 horas</strong>.</p>
    """, "Confirme seu email — TRAMPO")
    return _send(user.email, "✉️ Confirme seu email no TRAMPO", html)


def send_password_reset_email(user, token: str) -> bool:
    base = os.environ.get("BASE_URL", "https://trampoinc.netlify.app")
    url  = f"{base}/pages/forgot-password.html?token={token}"
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Redefinição de Senha 🔐</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 20px">
        Recebemos uma solicitação para redefinir a senha de <strong>{user.email}</strong>.
      </p>
      {_btn(url, '🔑 Redefinir minha Senha', '#6366f1')}
      <p style="color:#94a3b8;font-size:13px;text-align:center">
        Este link expira em <strong>2 horas</strong>.<br>
        Se não foi você, ignore este email.
      </p>
    """, "Redefinição de senha — TRAMPO")
    return _send(user.email, "🔑 Redefinição de senha no TRAMPO", html)


def send_welcome_email(user) -> bool:
    base = os.environ.get("BASE_URL", "https://trampoinc.netlify.app")
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Conta ativada! Vamos começar 🚀</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        Olá <strong>{user.name.split()[0]}</strong>, sua conta foi ativada!
        Complete seu perfil para receber vagas compatíveis.
      </p>
      {_btn(f"{base}/pages/profile.html", '👤 Completar meu Perfil')}
    """, "Bem-vindo ao TRAMPO!")
    return _send(user.email, "🎉 Bem-vindo ao TRAMPO! Sua conta está ativa", html)


def send_application_email(user, job, application) -> bool:
    score_color = "#10b981" if application.match_score >= 75 else "#f59e0b"
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Currículo enviado! ✅</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        Olá <strong>{user.name.split()[0]}</strong>, seu currículo chegou em <strong>{job.company}</strong>!
      </p>
      <div style="background:#f8fafc;border-radius:12px;padding:24px;margin-bottom:24px;border-left:4px solid #10b981">
        <div><span style="color:#64748b;font-size:13px">Vaga</span>
             <div style="font-weight:700;color:#0f172a">{job.title}</div></div>
        <div style="margin-top:10px"><span style="color:#64748b;font-size:13px">Empresa</span>
             <div style="font-weight:700;color:#0f172a">{job.company}</div></div>
        <div style="margin-top:10px"><span style="color:#64748b;font-size:13px">Compatibilidade</span>
             <div style="font-weight:800;color:{score_color};font-size:20px">{round(application.match_score)}%</div></div>
      </div>
      <p style="color:#94a3b8;font-size:13px;text-align:center">Tempo médio de resposta: 2 a 7 dias úteis. Boa sorte! 🤞</p>
    """, "Currículo enviado — TRAMPO")
    _send(user.email, f"✅ Currículo enviado para {job.company}", html)
    if job.contact_email:
        html2 = _wrap(f"""
          <h2 style="color:#0f172a;margin:0 0 8px">Nova candidatura recebida 🎯</h2>
          <p style="color:#475569;font-size:15px">
            <strong>{user.name}</strong> se candidatou à vaga <strong>{job.title}</strong>
            com <strong style="color:#10b981">{round(application.match_score)}%</strong> de compatibilidade.
          </p>
          <p style="color:#64748b;font-size:14px">Email: {user.email}</p>
        """, "Nova candidatura — TRAMPO")
        _send(job.contact_email, f"🎯 Candidatura: {user.name} — {job.title}", html2)
    return True


def send_support_confirmation(user, ticket) -> bool:
    sla  = "2 horas" if user.is_premium else "24 horas"
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Mensagem recebida ✅</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7">
        Olá <strong>{user.name.split()[0]}</strong>, responderemos em até <strong>{sla}</strong>.
      </p>
      <div style="background:#f8fafc;border-radius:12px;padding:20px;margin-top:16px">
        <div><span style="color:#64748b;font-size:13px">Ticket nº</span>
             <div style="font-weight:700;color:#0f172a">#{ticket.id}</div></div>
        <div style="margin-top:10px"><span style="color:#64748b;font-size:13px">Assunto</span>
             <div style="font-weight:700;color:#0f172a">{ticket.subject}</div></div>
      </div>
    """, "Suporte — TRAMPO")
    return _send(user.email, f"[Ticket #{ticket.id}] Mensagem recebida — TRAMPO", html)


def send_premium_activated(user) -> bool:
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Você é Premium! 💎</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7">
        Parabéns, <strong>{user.name.split()[0]}</strong>! Seu plano Premium foi ativado.
        Agora você tem 30 envios/dia e candidatura em destaque.
      </p>
    """, "Premium ativado — TRAMPO")
    return _send(user.email, "💎 Bem-vindo ao TRAMPO Premium!", html)


def send_job_payment_confirmation(user, job) -> bool:
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Vaga publicada! 🚀</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7">
        Olá <strong>{user.name.split()[0]}</strong>, sua vaga <strong>{job.title}</strong> está no ar!
      </p>
    """, "Vaga publicada — TRAMPO")
    return _send(user.email, f"🚀 Vaga publicada: {job.title}", html)
