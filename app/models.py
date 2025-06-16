from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from datetime import date

class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cnpj = Column(String(20), nullable=False, unique=True)
    email = Column(String, nullable=True)
    telefone = Column(String, nullable=True)
    segmento = Column(String, nullable=True)

    produtos = relationship("Produto", back_populates="fornecedor")
    pedidos = relationship("Pedido", back_populates="fornecedor")  

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    estoque_atual = Column(Integer, default=0)
    preco = Column(Numeric(10, 2), nullable=False)

    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    fornecedor = relationship("Fornecedor", back_populates="produtos")

    vendas = relationship("Venda", back_populates="produto")
    pedidos = relationship("Pedido", back_populates="produto")  

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"))
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pendente")
    data_pedido = Column(Date, default=date.today)

    produto = relationship("Produto", back_populates="pedidos")      
    fornecedor = relationship("Fornecedor", back_populates="pedidos")  

class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"))
    quantidade = Column(Integer, nullable=False)
    data_venda = Column(Date, nullable=False)

    produto = relationship("Produto", back_populates="vendas")

class Usuario(Base):
    __tablename__ = "usuarios"

    username = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
