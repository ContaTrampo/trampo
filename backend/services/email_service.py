"""TRAMPO v7 — Serviço de Email com templates HTML profissionais"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

_BASE_STYLE = """
  font-family: 'Segoe UI', Arial, sans-serif;
  background: #f8fafc;
  margin: 0; padding: 0;
"""

def _wrap(body_html: str, title: str = "TRAMPO") -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title></head>
<body style="{_BASE_STYLE}">
<div style="max-width:600px;margin:40px auto;background:#fff;border-radius:16px;
     overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08)">
  <!-- Header -->
  <div style="background:linear-gradient(135deg,#10b981,#059669);padding:32px 40px;text-align:center">
    <div style="font-family:'Segoe UI',sans-serif;font-size:28px;font-weight:800;
         color:#fff;letter-spacing:-1px">TRAMP<span style="color:#d1fae5">O</span></div>
    <div style="color:rgba(255,255,255,0.8);font-size:13px;margin-top:4px">
      Conectando talentos a oportunidades
    </div>
  </div>
  <!-- Body -->
  <div style="padding:40px">
    {body_html}
  </div>
  <!-- Footer -->
  <div style="background:#f8fafc;padding:24px 40px;text-align:center;
       border-top:1px solid #e2e8f0">
    <p style="color:#94a3b8;font-size:12px;margin:0">
      © 2025 TRAMPO · <a href="mailto:bemvindo.trampo@gmail.com"
      style="color:#10b981">bemvindo.trampo@gmail.com</a>
    </p>
    <p style="color:#cbd5e1;font-size:11px;margin:8px 0 0">
      Você está recebendo este email porque tem uma conta no TRAMPO.
    </p>
  </div>
</div>
</body></html>"""


def _btn(url: str, label: str, color: str = "#10b981") -> str:
    return f"""<div style="text-align:center;margin:28px 0">
  <a href="{url}" style="background:{color};color:#fff;padding:14px 32px;
     border-radius:8px;text-decoration:none;font-weight:700;font-size:15px;
     display:inline-block">{label}</a>
</div>"""


def _send(to: str, subject: str, html: str, text: str = "") -> bool:
    try:
        username = current_app.config.get("MAIL_USERNAME", "")
        password = current_app.config.get("MAIL_PASSWORD", "")
        if not username or not password:
            print(f"⚠️ Email não configurado → {to} | {subject}")
            return False
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"TRAMPO <{username}>"
        msg["To"]      = to
        if text:
            msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP("smtp.gmail.com", 587) as srv:
            srv.ehlo(); srv.starttls(); srv.login(username, password)
            srv.sendmail(username, to, msg.as_string())
        print(f"✅ Email enviado → {to}")
        return True
    except Exception as e:
        print(f"❌ Erro email {to}: {e}")
        return False


# ─── Templates ────────────────────────────────────────────────

def send_verification_email(user, token: str) -> bool:
    base = current_app.config.get("BASE_URL", "http://localhost:5000")
    url  = f"{base}/pages/verify-email.html?token={token}"
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Bem-vindo ao TRAMPO, {user.name.split()[0]}! 🎉</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 20px">
        Obrigado por se cadastrar! Confirme seu email para ativar sua conta e começar 
        a encontrar as melhores oportunidades.
      </p>
      {_btn(url, '✉️ Confirmar meu Email')}
      <p style="color:#94a3b8;font-size:13px;text-align:center">
        Este link expira em <strong>24 horas</strong>.<br>
        Se não foi você, ignore este email.
      </p>
    """, "Confirme seu email — TRAMPO")
    return _send(user.email, "✉️ Confirme seu email no TRAMPO", html)


def send_password_reset_email(user, token: str) -> bool:
    base = current_app.config.get("BASE_URL", "http://localhost:5000")
    url  = f"{base}/pages/reset-password.html?token={token}"
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Redefinição de Senha 🔐</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 20px">
        Recebemos uma solicitação para redefinir a senha da conta associada 
        ao email <strong>{user.email}</strong>.
      </p>
      {_btn(url, '🔑 Redefinir minha Senha', '#6366f1')}
      <p style="color:#94a3b8;font-size:13px;text-align:center">
        Este link expira em <strong>2 horas</strong>.<br>
        Se não foi você, sua conta está segura — ignore este email.
      </p>
    """, "Redefinição de senha — TRAMPO")
    return _send(user.email, "🔑 Redefinição de senha no TRAMPO", html)


def send_welcome_email(user) -> bool:
    base = current_app.config.get("BASE_URL", "http://localhost:5000")
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Conta ativada! Vamos começar 🚀</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        Olá <strong>{user.name.split()[0]}</strong>, sua conta foi ativada com sucesso!
        Complete seu perfil agora para receber vagas compatíveis com você.
      </p>
      <div style="background:#f0fdf4;border-radius:12px;padding:20px;margin-bottom:24px">
        <h4 style="color:#166534;margin:0 0 12px">📋 Próximos passos:</h4>
        <ol style="color:#15803d;margin:0;padding-left:20px;line-height:2">
          <li>Complete seu perfil profissional</li>
          <li>Faça upload do seu currículo (PDF)</li>
          <li>Veja as vagas compatíveis com você</li>
          <li>Se candidate com 1 clique!</li>
        </ol>
      </div>
      {_btn(f"{base}/pages/profile.html", '👤 Completar meu Perfil')}
    """, "Bem-vindo ao TRAMPO!")
    return _send(user.email, "🎉 Bem-vindo ao TRAMPO! Sua conta está ativa", html)


def send_application_email(user, job, application) -> bool:
    score_color = "#10b981" if application.match_score >= 75 else "#f59e0b"
    # Para o candidato
    html_cand = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Currículo enviado! ✅</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        Olá <strong>{user.name.split()[0]}</strong>, seu currículo chegou em 
        <strong>{job.company}</strong>!
      </p>
      <div style="background:#f8fafc;border-radius:12px;padding:24px;margin-bottom:24px;
           border-left:4px solid #10b981">
        <div style="display:grid;gap:10px">
          <div><span style="color:#64748b;font-size:13px">Vaga</span>
               <div style="font-weight:700;color:#0f172a">{job.title}</div></div>
          <div><span style="color:#64748b;font-size:13px">Empresa</span>
               <div style="font-weight:700;color:#0f172a">{job.company}</div></div>
          <div><span style="color:#64748b;font-size:13px">Local</span>
               <div style="font-weight:700;color:#0f172a">{job.location or 'Não informado'}</div></div>
          <div><span style="color:#64748b;font-size:13px">Compatibilidade</span>
               <div style="font-weight:800;color:{score_color};font-size:20px">
                 {round(application.match_score)}%
               </div></div>
        </div>
      </div>
      <p style="color:#94a3b8;font-size:13px;text-align:center">
        Tempo médio de resposta: 2 a 7 dias úteis. Boa sorte! 🤞
      </p>
    """, "Currículo enviado — TRAMPO")
    _send(user.email, f"✅ Currículo enviado para {job.company}", html_cand)

    # Para a empresa
    if job.contact_email:
        profile = user.profile
        skills_html = "".join(
            f'<span style="background:#d1fae5;color:#065f46;padding:3px 10px;'
            f'border-radius:20px;font-size:12px;margin:2px;display:inline-block">{s}</span>'
            for s in (profile.get_skills_list()[:6] if profile else [])
        )
        html_comp = _wrap(f"""
          <h2 style="color:#0f172a;margin:0 0 8px">Nova candidatura recebida 🎯</h2>
          <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
            Você recebeu uma nova candidatura via <strong>TRAMPO</strong> para a vaga 
            <strong>{job.title}</strong>.
          </p>
          <div style="background:#f8fafc;border-radius:12px;padding:24px;margin-bottom:20px">
            <div style="display:flex;gap:16px;align-items:center;margin-bottom:16px">
              <div style="width:48px;height:48px;background:#10b981;border-radius:50%;
                   display:flex;align-items:center;justify-content:center;
                   color:#fff;font-weight:800;font-size:18px;flex-shrink:0">
                {user.name[0].upper()}
              </div>
              <div>
                <div style="font-weight:700;color:#0f172a;font-size:16px">{user.name}</div>
                <div style="color:#64748b;font-size:13px">{user.email}</div>
              </div>
            </div>
            <div style="display:grid;gap:8px;font-size:14px">
              <div><span style="color:#64748b">Cargo:</span> 
                   <strong>{profile.job_title if profile else '—'}</strong></div>
              <div><span style="color:#64748b">Experiência:</span> 
                   <strong>{profile.years_experience if profile else 0} anos</strong></div>
              <div><span style="color:#64748b">Match com a vaga:</span> 
                   <strong style="color:#10b981">{round(application.match_score)}%</strong></div>
            </div>
            {f'<div style="margin-top:12px">{skills_html}</div>' if skills_html else ''}
          </div>
          <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
               padding:20px;margin-bottom:24px">
            <h4 style="color:#0f172a;margin:0 0 10px;font-size:14px">💌 Carta de Apresentação:</h4>
            <p style="color:#475569;font-size:14px;line-height:1.7;margin:0;white-space:pre-line">
              {application.cover_letter or '(Sem carta de apresentação)'}
            </p>
          </div>
          <p style="color:#94a3b8;font-size:12px;text-align:center">
            Candidatura recebida via TRAMPO · trampo.com.br
          </p>
        """, "Nova candidatura — TRAMPO")
        _send(job.contact_email,
              f"🎯 Candidatura: {user.name} — {job.title} ({round(application.match_score)}% match)",
              html_comp)
    return True


def send_premium_activated(user) -> bool:
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Você é Premium! 💎</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        Parabéns, <strong>{user.name.split()[0]}</strong>! Seu plano Premium foi ativado.
      </p>
      <div style="background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;
           padding:24px;margin-bottom:24px">
        <h4 style="color:#10b981;margin:0 0 16px">✨ Seus benefícios Premium:</h4>
        <ul style="color:#e2e8f0;margin:0;padding-left:20px;line-height:2.2;font-size:14px">
          <li><strong style="color:#10b981">30 envios/dia</strong> (era 5)</li>
          <li>Candidatura <strong style="color:#10b981">destacada</strong> — aparece primeiro</li>
          <li>Notificações de vagas em <strong style="color:#10b981">tempo real</strong></li>
          <li>Suporte prioritário em <strong style="color:#10b981">2 horas</strong></li>
          <li>Avaliações visíveis no seu perfil</li>
        </ul>
      </div>
    """, "Premium ativado — TRAMPO")
    return _send(user.email, "💎 Bem-vindo ao TRAMPO Premium!", html)


def send_support_confirmation(user, ticket) -> bool:
    sla  = "2 horas" if user.is_premium else "24 horas"
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Mensagem recebida ✅</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        Olá <strong>{user.name.split()[0]}</strong>, recebemos seu contato e 
        responderemos em até <strong>{sla}</strong>.
      </p>
      <div style="background:#f8fafc;border-radius:12px;padding:20px">
        <div><span style="color:#64748b;font-size:13px">Ticket nº</span>
             <div style="font-weight:700;color:#0f172a">#{ticket.id}</div></div>
        <div style="margin-top:12px"><span style="color:#64748b;font-size:13px">Assunto</span>
             <div style="font-weight:700;color:#0f172a">{ticket.subject}</div></div>
        <div style="margin-top:12px"><span style="color:#64748b;font-size:13px">Prioridade</span>
             <div style="font-weight:700;color:{'#10b981' if ticket.priority == 'high' else '#64748b'}">
               {'⭐ Alta (Premium)' if ticket.priority == 'high' else 'Normal'}
             </div></div>
      </div>
    """, "Suporte — TRAMPO")
    return _send(user.email, f"[Ticket #{ticket.id}] Mensagem recebida — TRAMPO", html)


def send_job_payment_confirmation(user, job) -> bool:
    html = _wrap(f"""
      <h2 style="color:#0f172a;margin:0 0 8px">Vaga publicada com sucesso! 🚀</h2>
      <p style="color:#475569;font-size:15px;line-height:1.7;margin:0 0 24px">
        Olá <strong>{user.name.split()[0]}</strong>, o pagamento foi confirmado e sua 
        vaga está no ar!
      </p>
      <div style="background:#f0fdf4;border-radius:12px;padding:20px;
           border-left:4px solid #10b981;margin-bottom:24px">
        <div style="font-weight:700;color:#0f172a;font-size:16px">{job.title}</div>
        <div style="color:#64748b;font-size:13px;margin-top:4px">{job.company} · {job.location or '—'}</div>
      </div>
      <p style="color:#94a3b8;font-size:13px;text-align:center">
        A IA já está ranqueando candidatos compatíveis com sua vaga. 🎯
      </p>
    """, "Vaga publicada — TRAMPO")
    return _send(user.email, f"🚀 Vaga publicada: {job.title}", html)
