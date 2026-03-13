"""TRAMPO v7 — Modelos de Dados"""
from datetime import datetime, date, timezone
from database import db


class User(db.Model):
    __tablename__ = "users"
    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(100), nullable=False)
    email            = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash    = db.Column(db.String(255), nullable=False)
    role             = db.Column(db.String(20), default="candidate")  # candidate|recruiter|admin

    # Dados pessoais
    cpf              = db.Column(db.String(14), unique=True, nullable=True, index=True)
    phone            = db.Column(db.String(20), nullable=True)
    sexo             = db.Column(db.String(1), nullable=True)   # M|F|O
    birth_date       = db.Column(db.Date, nullable=True)

    # Endereço
    cep              = db.Column(db.String(10), nullable=True)
    logradouro       = db.Column(db.String(200), nullable=True)
    numero           = db.Column(db.String(20), nullable=True)
    complemento      = db.Column(db.String(100), nullable=True)
    bairro           = db.Column(db.String(100), nullable=True)
    cidade           = db.Column(db.String(100), nullable=True)
    estado           = db.Column(db.String(2), nullable=True)

    # Email verification
    email_verified              = db.Column(db.Boolean, default=False)
    email_verification_token    = db.Column(db.String(128), nullable=True, index=True)
    email_verification_expires  = db.Column(db.DateTime, nullable=True)

    # Password reset
    password_reset_token        = db.Column(db.String(128), nullable=True, index=True)
    password_reset_expires      = db.Column(db.DateTime, nullable=True)

    # Premium
    is_premium          = db.Column(db.Boolean, default=False)
    premium_expires_at  = db.Column(db.DateTime, nullable=True)

    # Stripe
    stripe_customer_id      = db.Column(db.String(100), nullable=True)
    stripe_subscription_id  = db.Column(db.String(100), nullable=True)

    # Limites diários
    daily_sends_used  = db.Column(db.Integer, default=0)
    last_reset_date   = db.Column(db.Date, default=date.today)

    email_notifications = db.Column(db.Boolean, default=True)
    created_at          = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    profile      = db.relationship("CandidateProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    applications = db.relationship("Application", backref="user", lazy=True, cascade="all, delete-orphan")
    jobs         = db.relationship("Job", backref="recruiter", lazy=True, foreign_keys="Job.recruiter_id")
    reviews_received = db.relationship("Review", foreign_keys="Review.candidate_id", backref="candidate", lazy=True)

    def get_daily_limit(self) -> int:
        return 30 if self.is_premium else 5

    def reset_daily_if_needed(self) -> None:
        today = date.today()
        if self.last_reset_date is None or self.last_reset_date != today:
            self.daily_sends_used = 0
            self.last_reset_date  = today

    def can_send_today(self) -> bool:
        self.reset_daily_if_needed()
        return self.daily_sends_used < self.get_daily_limit()

    def get_full_address(self) -> str:
        parts = [p for p in [self.logradouro, self.numero, self.bairro, self.cidade, self.estado] if p]
        return ", ".join(parts) if parts else ""

    def to_dict(self) -> dict:
        if self.is_premium and self.premium_expires_at:
            exp = self.premium_expires_at.replace(tzinfo=timezone.utc) if self.premium_expires_at.tzinfo is None else self.premium_expires_at
            if exp < datetime.now(timezone.utc):
                self.is_premium = False
                db.session.commit()
        return {
            "id":               self.id,
            "name":             self.name,
            "email":            self.email,
            "role":             self.role,
            "cpf":              self.cpf,
            "phone":            self.phone,
            "cidade":           self.cidade,
            "estado":           self.estado,
            "is_premium":       self.is_premium,
            "email_verified":   self.email_verified,
            "daily_limit":      self.get_daily_limit(),
            "daily_sends_used": self.daily_sends_used,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
        }


class CandidateProfile(db.Model):
    __tablename__ = "candidate_profiles"
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True, index=True)
    job_title        = db.Column(db.String(100), nullable=True)
    years_experience = db.Column(db.Integer, default=0)
    seniority        = db.Column(db.String(30), nullable=True)   # junior|mid|senior|lead
    salary_min       = db.Column(db.Integer, nullable=True)
    salary_max       = db.Column(db.Integer, nullable=True)
    availability     = db.Column(db.String(30), default="immediate")
    work_mode        = db.Column(db.String(30), default="any")   # remote|hybrid|onsite|any
    bio              = db.Column(db.Text, nullable=True)
    skills           = db.Column(db.Text, nullable=True)         # CSV: "Python, React, AWS"
    linkedin_url     = db.Column(db.String(300), nullable=True)
    github_url       = db.Column(db.String(300), nullable=True)
    portfolio_url    = db.Column(db.String(300), nullable=True)
    whatsapp         = db.Column(db.String(20), nullable=True)
    resume_filename  = db.Column(db.String(255), nullable=True)
    resume_text      = db.Column(db.Text, nullable=True)

    # Avaliação média (calculada)
    avg_rating       = db.Column(db.Float, default=0.0)
    rating_count     = db.Column(db.Integer, default=0)

    created_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_skills_list(self) -> list:
        if self.skills:
            return [s.strip() for s in self.skills.split(",") if s.strip()]
        return []

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "job_title":        self.job_title,
            "years_experience": self.years_experience,
            "seniority":        self.seniority,
            "skills":           self.get_skills_list(),
            "bio":              self.bio,
            "salary_min":       self.salary_min,
            "salary_max":       self.salary_max,
            "availability":     self.availability,
            "work_mode":        self.work_mode,
            "linkedin_url":     self.linkedin_url,
            "github_url":       self.github_url,
            "portfolio_url":    self.portfolio_url,
            "whatsapp":         self.whatsapp,
            "has_resume":       self.resume_filename is not None,
            "avg_rating":       round(self.avg_rating, 1),
            "rating_count":     self.rating_count,
        }


class RecruiterProfile(db.Model):
    __tablename__ = "recruiter_profiles"
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True, index=True)
    company_name    = db.Column(db.String(200), nullable=True)
    company_cnpj    = db.Column(db.String(18), nullable=True)
    company_website = db.Column(db.String(300), nullable=True)
    company_size    = db.Column(db.String(50), nullable=True)
    industry        = db.Column(db.String(100), nullable=True)
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "company_name":     self.company_name,
            "company_website":  self.company_website,
            "industry":         self.industry,
        }


class Job(db.Model):
    __tablename__ = "jobs"
    id                  = db.Column(db.Integer, primary_key=True)
    recruiter_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    title               = db.Column(db.String(200), nullable=False)
    company             = db.Column(db.String(200), nullable=False)
    description         = db.Column(db.Text, nullable=False)
    location            = db.Column(db.String(200), nullable=True)
    cidade              = db.Column(db.String(100), nullable=True, index=True)
    estado              = db.Column(db.String(2), nullable=True)
    latitude            = db.Column(db.Float, nullable=True)
    longitude           = db.Column(db.Float, nullable=True)
    contract_type       = db.Column(db.String(20), default="clt")  # clt|pj|freelancer|internship
    salary_min          = db.Column(db.Integer, nullable=True)
    salary_max          = db.Column(db.Integer, nullable=True)
    work_mode           = db.Column(db.String(20), default="onsite")
    required_skills     = db.Column(db.Text, nullable=True)
    required_experience = db.Column(db.Integer, default=0)
    contact_email       = db.Column(db.String(150), nullable=True)
    contact_whatsapp    = db.Column(db.String(20), nullable=True)
    source_url          = db.Column(db.String(500), nullable=True)  # URL original (scraping)
    benefits            = db.Column(db.Text, nullable=True)
    status              = db.Column(db.String(20), default="active")  # active|closed|pending_payment
    source              = db.Column(db.String(50), default="manual")  # manual|scraped
    payment_intent_id   = db.Column(db.String(100), nullable=True)    # Stripe payment
    is_paid             = db.Column(db.Boolean, default=False)        # R$50 pago
    is_featured         = db.Column(db.Boolean, default=False)
    posted_at           = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship("Application", backref="job", lazy=True, cascade="all, delete-orphan")

    def get_skills_list(self) -> list:
        if self.required_skills:
            return [s.strip() for s in self.required_skills.split(",") if s.strip()]
        return []

    def to_dict(self) -> dict:
        return {
            "id":                  self.id,
            "title":               self.title,
            "company":             self.company,
            "description":         self.description,
            "location":            self.location,
            "cidade":              self.cidade,
            "estado":              self.estado,
            "latitude":            self.latitude,
            "longitude":           self.longitude,
            "contract_type":       self.contract_type,
            "salary_min":          self.salary_min,
            "salary_max":          self.salary_max,
            "work_mode":           self.work_mode,
            "required_skills":     self.get_skills_list(),
            "required_experience": self.required_experience,
            "contact_email":       self.contact_email,
            "contact_whatsapp":    self.contact_whatsapp,
            "source_url":          self.source_url,
            "benefits":            self.benefits,
            "status":              self.status,
            "source":              self.source,
            "is_featured":         self.is_featured,
            "posted_at":           self.posted_at.isoformat() if self.posted_at else None,
            "applications_count":  len(self.applications) if self.applications else 0,
        }


class Application(db.Model):
    __tablename__ = "applications"
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    job_id          = db.Column(db.Integer, db.ForeignKey("jobs.id"),  nullable=False, index=True)
    match_score     = db.Column(db.Float, default=0.0)
    cover_letter    = db.Column(db.Text, nullable=True)
    email_sent_to   = db.Column(db.String(150), nullable=True)
    status          = db.Column(db.String(30), default="sent")
    is_featured     = db.Column(db.Boolean, default=False)  # candidatura destacada (premium)
    sent_at         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    viewed_at       = db.Column(db.DateTime, nullable=True)
    responded_at    = db.Column(db.DateTime, nullable=True)
    recruiter_notes = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "job":           self.job.to_dict() if self.job else None,
            "match_score":   round(self.match_score, 1),
            "status":        self.status,
            "is_featured":   self.is_featured,
            "sent_at":       self.sent_at.isoformat() if self.sent_at else None,
            "cover_letter":  self.cover_letter,
            "email_sent_to": self.email_sent_to,
        }


class Review(db.Model):
    """Avaliação de candidato por recrutador (pós entrevista)"""
    __tablename__ = "reviews"
    id           = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    reviewer_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    job_id       = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    rating       = db.Column(db.Integer, nullable=False)    # 1-5
    comment      = db.Column(db.Text, nullable=True)
    is_public    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reviewer = db.relationship("User", foreign_keys=[reviewer_id], backref="reviews_given")

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "rating":        self.rating,
            "comment":       self.comment,
            "reviewer_name": self.reviewer.name if self.reviewer else "—",
            "created_at":    self.created_at.isoformat() if self.created_at else None,
        }


class SupportTicket(db.Model):
    __tablename__ = "support_tickets"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject     = db.Column(db.String(200), nullable=False)
    message     = db.Column(db.Text, nullable=False)
    status      = db.Column(db.String(30), default="open")
    priority    = db.Column(db.String(20), default="normal")
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime, nullable=True)
