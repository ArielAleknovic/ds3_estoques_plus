import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from datetime import date, timedelta

from db import SessionLocal, engine, Base
from models import Produto, Venda, Pedido

Base.metadata.create_all(bind=engine)

def get_produtos(db: Session):
    return db.query(Produto).all()

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

def criar_pedido(db: Session, produto_id: int, quantidade: int):
    pedido = Pedido(produto_id=produto_id, quantidade=quantidade, status='pendente', data_pedido=date.today())
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

def main():
    st.set_page_config(page_title="Estoques Plus Monitor", layout="wide", page_icon="📦")

    # Título personalizado
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='color:#2c3e50;'>📦 Estoques Plus Monitor</h1>
            <h4 style='color:#7f8c8d;'>Gestão inteligente de estoques baseada na média de vendas</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()

    menu = st.sidebar.radio("Navegação", ["📊 Dashboard", "🧾 Pedidos", "➕ Criar Pedido"])

    if menu == "📊 Dashboard":
        st.subheader("📊 Visão Geral de Estoques e Sugestões de Pedido")
        produtos = get_produtos(db)
        df = pd.DataFrame([{
            "Produto": p.nome,
            "Estoque Atual": p.estoque_atual,
            "Preço (R$)": float(p.preco),
            "Média diária vendas (30d)": round(calcular_media_vendas(db, p.id), 2)
        } for p in produtos])
        st.dataframe(df, use_container_width=True)

        st.markdown("### 💡 Sugestão de pedidos baseada na média diária para 30 dias")
        sugestoes = []
        for p in produtos:
            media = calcular_media_vendas(db, p.id)
            sugerido = max(0, int(media * 30 - p.estoque_atual))
            sugestoes.append({"Produto": p.nome, "Quantidade Sugerida": sugerido})
        df_sugestoes = pd.DataFrame(sugestoes)
        st.dataframe(df_sugestoes, use_container_width=True)

    elif menu == "🧾 Pedidos":
        st.subheader("🧾 Lista de Pedidos")
        pedidos = get_pedidos(db)
        df = pd.DataFrame([{
            "ID": ped.id,
            "Produto": ped.produto.nome,
            "Quantidade": ped.quantidade,
            "Status": ped.status,
            "Data": ped.data_pedido
        } for ped in pedidos])
        st.dataframe(df, use_container_width=True)

        st.markdown("### ✏️ Editar ou 🗑️ Deletar Pedido")
        pedido_id = st.number_input("ID do pedido", min_value=1, step=1)
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if pedido:
            quantidade = st.number_input("Quantidade", value=pedido.quantidade, min_value=1)
            status = st.selectbox("Status", ["pendente", "enviado", "cancelado"], index=["pendente", "enviado", "cancelado"].index(pedido.status))
            if st.button("Atualizar Pedido"):
                atualizar_pedido(db, pedido_id, quantidade, status)
                st.success("Pedido atualizado!")
            if st.button("Deletar Pedido"):
                deletar_pedido(db, pedido_id)
                st.success("Pedido deletado!")
        else:
            st.info("Pedido não encontrado")

    elif menu == "➕ Criar Pedido":
        st.subheader("➕ Criar novo pedido")
        produtos = get_produtos(db)
        if not produtos:
            st.warning("Nenhum produto cadastrado.")
        else:
            produto_nomes = [p.nome for p in produtos]
            produto_sel = st.selectbox("Produto", produto_nomes)
            produto_obj = next(p for p in produtos if p.nome == produto_sel)

            quantidade = st.number_input("Quantidade", min_value=1, value=1)

            media = calcular_media_vendas(db, produto_obj.id)
            sugestao = max(1, int(media * 30 - produto_obj.estoque_atual))
            st.write(f"📈 Sugestão de quantidade para repor 30 dias: **{sugestao}** unidades.")

            if st.button("Criar Pedido"):
                criar_pedido(db, produto_obj.id, quantidade)
                st.success("✅ Pedido criado com sucesso!")

    db.close()

if __name__ == "__main__":
    main()
