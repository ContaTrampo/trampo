"""TRAMPO v7 — Validadores"""
import re


def validate_cpf(cpf: str) -> bool:
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    s = sum(int(cpf[i]) * (10 - i) for i in range(9))
    r = (s * 10) % 11
    d1 = 0 if r >= 10 else r
    if d1 != int(cpf[9]):
        return False
    s = sum(int(cpf[i]) * (11 - i) for i in range(10))
    r = (s * 10) % 11
    d2 = 0 if r >= 10 else r
    return d2 == int(cpf[10])


def format_cpf(cpf: str) -> str:
    cpf = re.sub(r"\D", "", cpf)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf


def validate_password(password: str) -> tuple:
    if len(password) < 7:
        return False, "Senha precisa ter no mínimo 7 caracteres"
    if not re.search(r"[A-Z]", password):
        return False, "Senha precisa ter ao menos 1 letra maiúscula"
    if not re.search(r"[a-z]", password):
        return False, "Senha precisa ter ao menos 1 letra minúscula"
    if not re.search(r"\d", password):
        return False, "Senha precisa ter ao menos 1 número"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Senha precisa ter ao menos 1 caractere especial (!@#$%...)"
    return True, ""


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def format_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return phone
