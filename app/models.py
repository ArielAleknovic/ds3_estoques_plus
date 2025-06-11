from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    estoque_atual = Column(Integer, default=0)
    preco = Column(Numeric(10,2), nullable=False)

    vendas = relationship("Venda", back_populates="produto")
    pedidos = relationship("Pedido", back_populates="produto")

class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"))
    quantidade = Column(Integer, nullable=False)
    data_venda = Column(Date, nullable=False)

    produto = relationship("Produto", back_populates="vendas")

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"))
    quantidade = Column(Integer, nullable=False)
    status = Column(String, default="pendente")
    data_pedido = Column(Date, nullable=False)

    produto = relationship("Produto", back_populates="pedidos")
