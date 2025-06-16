import re
from pydantic import BaseModel, validator, EmailStr, constr
from email.utils import parseaddr

def normalizar_cnpj(cnpj: str) -> str:
    return re.sub(r'\D', '', cnpj)

def validar_cnpj(cnpj: str) -> bool:
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    return len(cnpj_limpo) == 14 and cnpj_limpo.isdigit()


def normalizar_email(email: str) -> str:
    return email.strip().lower() if email else None 

def validar_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip()
    estrutura = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(estrutura, email) is not None


def normalizar_telefone(telefone: str) -> str: 
    return re.sub(r'\D', '', telefone)

def validar_telefone(telefone: str) -> bool:
    if not telefone:
        return True  
    telefone_limpo = re.sub(r'[^\d]', '', telefone)
    return 10 <= len(telefone_limpo) <= 13 and telefone_limpo.isdigit()





def validar_nome(nome: str) -> tuple[bool, str | None]:
    nome = nome.strip()
    if not nome:
        return False, "Nome não pode ser vazio."
    if not re.fullmatch(r"[A-Za-zÀ-ÿ\s]{2,100}", nome):
        return False, "Nome deve conter apenas letras e espaços (mín. 2, máx. 100 caracteres)."
    return True, None

def validar_telefone(telefone: str) -> tuple[bool, str | None]:
    telefone = telefone.strip()
    if not telefone.isdigit():
        return False, "Telefone deve conter apenas números."
    if len(telefone) < 8:
        return False, "Telefone muito curto. Deve ter no mínimo 8 dígitos."
    if len(telefone) > 20:
        return False, "Telefone muito longo. Máximo permitido é 20 dígitos."
    return True, None

def validar_email(email: str) -> tuple[bool, str | None]:
    if "@" not in parseaddr(email)[1]:
        return False, "Formato de email inválido."
    return True, None

def validar_cnpj(cnpj: str) -> tuple[bool, str | None]:
    cnpj = cnpj.strip()
    if not cnpj.isdigit():
        return False, "CNPJ deve conter apenas números."
    if len(cnpj) < 14:
        return False, f"CNPJ incompleto. Faltam {14 - len(cnpj)} dígitos."
    if len(cnpj) > 14:
        return False, f"CNPJ muito longo. Excedeu {len(cnpj) - 14} dígitos."
    return True, None

def validar_valor_monetario(valor: str) -> tuple[bool, str | None]:
    valor = valor.strip().replace(',', '.')
    if not re.fullmatch(r"^\d+(\.\d{1,2})?$", valor):
        return False, "Valor inválido. Use números com até duas casas decimais (ex: 100.00)."
    return True, None

def validar_quantidade(qtd: int | float) -> tuple[bool, str | None]:
    if not isinstance(qtd, (int, float)):
        return False, "Quantidade deve ser um número."
    if qtd <= 0:
        return False, "Quantidade deve ser maior que zero."
    if isinstance(qtd, float) and not qtd.is_integer():
        return False, "Quantidade deve ser um número inteiro."
    return True, None
