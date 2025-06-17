import hashlib
from utils.db import SessionLocal
from models.models import Usuario

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def criar_usuario(username: str, name: str, password: str):
    db = SessionLocal()
    if db.query(Usuario).filter(Usuario.username == username).first():
        return False  # Usuário já existe
    novo_usuario = Usuario(
        username=username,
        name=name,
        password=hash_password(password)
    )
    db.add(novo_usuario)
    db.commit()
    return True
