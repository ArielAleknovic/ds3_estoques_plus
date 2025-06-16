import re

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