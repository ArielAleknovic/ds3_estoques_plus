import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt

from db import SessionLocal, engine, Base
from models import Produto, Venda, Pedido, Fornecedor, Usuario
from utils import normalizar_cnpj, validar_cnpj, normalizar_email, validar_email, validar_telefone
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

#CRUD de produto
def get_produtos(db: Session):
    return db.query(Produto).all()

def criar_produto(db: Session, nome: str, estoque: int, preco: float):
    produto = Produto(nome=nome, estoque_atual=estoque, preco=preco)
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto

def atualizar_produto(db: Session, produto_id: int, nome: str, estoque: int, preco: float):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto:
        produto.nome = nome
        produto.estoque_atual = estoque
        produto.preco = preco
        db.commit()
        db.refresh(produto)
        return produto
    else:
        raise ValueError("Produto não encontrado.")

def deletar_produto(db: Session, produto_id: int):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto:
        db.delete(produto)
        db.commit()
    else:
        raise ValueError("Produto não encontrado.")

# CRUD Fornecedor (sem alterações)
def get_fornecedores(db: Session):
    return db.query(Fornecedor).all()

def criar_fornecedor(db: Session, nome, cnpj, email, telefone, segmento):
    #validação sem rejects
    if not validar_cnpj(cnpj):
        raise ValueError("CNPJ inválido") 
    if email and not validar_email(email):
        raise ValueError("Email inválido")
    if telefone and not validar_telefone(telefone):
        raise ValueError("Telefone inválido")

    fornecedor = Fornecedor(nome=nome, cnpj=normalizar_cnpj(cnpj), email=normalizar_email(email), telefone=telefone, segmento=segmento)
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor

def atualizar_fornecedor(db: Session, fornecedor_id, nome, cnpj, email, telefone, segmento):
        #validação sem rejects
    if not validar_cnpj(cnpj):
        raise ValueError("CNPJ inválido") 
    if email and not validar_email(email):
        raise ValueError("Email inválido")
    if telefone and not validar_telefone(telefone):
        raise ValueError("Telefone inválido")
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if fornecedor:
        fornecedor.nome = nome
        fornecedor.cnpj = normalizar_cnpj(cnpj)
        fornecedor.email = normalizar_email(email)
        fornecedor.telefone = telefone
        fornecedor.segmento = segmento
        db.commit()
        db.refresh(fornecedor)
    return fornecedor

def deletar_fornecedor(db: Session, fornecedor_id):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if fornecedor:
        db.delete(fornecedor)
        db.commit()
        return True
    return False

# CRUD Produto, Venda e Pedido
def get_pedidos(db: Session):
    return db.query(Pedido).all()

def get_vendas_ultimos_30_dias(db: Session):
    data_limite = date.today() - timedelta(days=30)
    return db.query(Venda).filter(Venda.data_venda >= data_limite).all()

def calcular_media_vendas(db: Session, produto_id: int):
    data_limite = date.today() - timedelta(days=30)
    soma_vendas = db.query(func.sum(Venda.quantidade)).filter(
        Venda.produto_id == produto_id,
        Venda.data_venda >= data_limite
    ).scalar() or 0
    return soma_vendas / 30  # média diária


def criar_pedido(db: Session, produto_id: int, fornecedor_id: int, quantidade: int):
    pedido = Pedido(
        produto_id=produto_id, 
        fornecedor_id=fornecedor_id, 
        quantidade=quantidade, 
        status='pendente', 
        data_pedido=date.today()
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido

def atualizar_pedido(db: Session, pedido_id: int, quantidade: int, status: str):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        pedido.quantidade = quantidade
        pedido.status = status
        db.commit()
        db.refresh(pedido)
    return pedido

def deletar_pedido(db: Session, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        db.delete(pedido)
        db.commit()
        return True
    return False

#CRUD  de login
def login_tela():
    credentials = get_credentials()
    authenticator = stauth.Authenticate(
        credentials,
        "estoque_monitor_key",  # cookie name
        "estoque_cookie",       # cookie key
        cookie_expiry_days=1
    )

    nome, auth_status, username = authenticator.login("Login", "main")
    if auth_status is False:
        st.error("Usuário ou senha incorretos.")
    elif auth_status is None:
        st.warning("Por favor, insira suas credenciais.")
    return authenticator, auth_status, nome, username

def cadastro_tela():
    st.subheader("Criar nova conta")
    nome = st.text_input("Nome completo")
    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Registrar"):
        if nome and username and senha:
            criar_usuario(username, nome, senha)
            st.success("Usuário criado com sucesso!")
        else:
            st.error("Preencha todos os campos.")

def reset_tela():
    
    st.subheader("Resetar senha")
    st.warning("Entre em contato com o administrador ou recrie o usuário.")

def criar_usuario(username: str, name: str, password: str) -> bool:
    novo_usuario = Usuario(username=username, name=name, password=password)
    with SessionLocal() as db:
        try:
            db.add(novo_usuario)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False

def autenticar_usuario(username: str, password: str):
    with SessionLocal() as db:
        usuario = db.query(Usuario).filter_by(username=username, password=password).first()
        return usuario