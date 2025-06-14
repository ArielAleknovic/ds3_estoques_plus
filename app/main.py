import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt

from db import SessionLocal, engine, Base
from models import Produto, Venda, Pedido, Fornecedor 
from services import *

Base.metadata.create_all(bind=engine)


def main():
    st.set_page_config(page_title="Sistema de Monitoramento de Estoques", layout="wide")

    # Esconder barra superior
    st.markdown(
        """
        <style>
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://banco.bradesco/assets/classic/img/produtos-servicos/imoveis/produtos/banner-cdc-material-de-construcao.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .css-18e3th9 {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

    with SessionLocal() as db:
        menu = st.sidebar.radio("Navegação", ["Home", "Dashboard", "Pedidos", "Criar Pedido", "Relatórios", "Fornecedores"])

        if menu == "Home":
            st.title("Bem-vindo ao Sistema de Monitoramento de Estoques")
            st.markdown("Este sistema permite acompanhar estoques, vendas, pedidos e fornecedores de forma simples e eficiente.")

        elif menu == "Dashboard":
            st.subheader("Visão Geral dos Estoques e Recomendações de Pedido")
            produtos = get_produtos(db)
            if produtos:
                df = pd.DataFrame([{
                    "Produto": p.nome,
                    "Estoque Atual": p.estoque_atual,
                    "Preço (R$)": float(p.preco),
                    "Média diária de vendas (últimos 30 dias)": round(calcular_media_vendas(db, p.id), 2)
                } for p in produtos])

                st.dataframe(df, use_container_width=True)

                # Sugestão de pedidos
                sugestoes = []
                for p in produtos:
                    media = calcular_media_vendas(db, p.id)
                    sugerido = max(0, int(media * 30 - p.estoque_atual))
                    sugestoes.append({"Produto": p.nome, "Quantidade Sugerida": sugerido})
                df_sugestoes = pd.DataFrame(sugestoes)
                st.dataframe(df_sugestoes, use_container_width=True)

                # 1. Gráfico de barras: Estoque atual por produto
                st.markdown("### Estoque Atual por Produto")
                fig1, ax1 = plt.subplots(figsize=(10, 5))
                ax1.bar(df['Produto'], df['Estoque Atual'], color='skyblue')
                ax1.set_ylabel("Estoque Atual")
                ax1.set_xlabel("Produto")
                ax1.set_xticklabels(df['Produto'], rotation=45, ha='right')
                st.pyplot(fig1)

                # 2. Gráfico de linhas: Vendas diárias últimos 30 dias (total)
                st.markdown("### Vendas Diárias nos Últimos 30 Dias (Total)")
                data_limite = date.today() - timedelta(days=30)
                vendas_30d = db.query(Venda.data_venda, func.sum(Venda.quantidade)).filter(
                    Venda.data_venda >= data_limite).group_by(Venda.data_venda).order_by(Venda.data_venda).all()
                if vendas_30d:
                    df_vendas = pd.DataFrame(vendas_30d, columns=["Data", "Quantidade"])
                    fig2, ax2 = plt.subplots(figsize=(10, 5))
                    ax2.plot(df_vendas["Data"], df_vendas["Quantidade"], marker='o')
                    ax2.set_xlabel("Data")
                    ax2.set_ylabel("Quantidade Vendida")
                    ax2.set_title("Vendas Diárias (Últimos 30 dias)")
                    ax2.grid(True)
                    st.pyplot(fig2)
                else:
                    st.info("Nenhuma venda nos últimos 30 dias.")

                # 3. Gráfico pizza: Status dos pedidos
                st.markdown("### Status dos Pedidos")
                pedidos = get_pedidos(db)
                if pedidos:
                    status_counts = pd.Series([p.status for p in pedidos]).value_counts()
                    fig3, ax3 = plt.subplots()
                    ax3.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140, colors=['orange', 'green', 'red'])
                    ax3.axis('equal')
                    st.pyplot(fig3)
                else:
                    st.info("Nenhum pedido registrado.")

                # 4. Gráfico de barras: Quantidade sugerida para pedido
                st.markdown("### Quantidade Sugerida para Pedido por Produto (próximos 30 dias)")
                fig4, ax4 = plt.subplots(figsize=(10, 5))
                ax4.bar(df_sugestoes['Produto'], df_sugestoes['Quantidade Sugerida'], color='lightcoral')
                ax4.set_ylabel("Quantidade Sugerida")
                ax4.set_xlabel("Produto")
                ax4.set_xticklabels(df_sugestoes['Produto'], rotation=45, ha='right')
                st.pyplot(fig4)

            else:
                st.info("Não há produtos cadastrados.")

        elif menu == "Pedidos":
            st.subheader("Lista de Pedidos")
            pedidos = get_pedidos(db)
            if pedidos:
                df = pd.DataFrame([{
                    "ID": ped.id,
                    "Produto": ped.produto.nome if ped.produto else "Não disponível",
                    "Fornecedor": ped.fornecedor.nome if ped.fornecedor else "Não disponível",
                    "Quantidade": ped.quantidade,
                    "Status": ped.status,
                    "Data do pedido": ped.data_pedido
                } for ped in pedidos])
                st.dataframe(df, use_container_width=True)

                st.markdown("Editar ou excluir pedido")
                pedido_id = st.number_input("Informe o ID do pedido", min_value=1, step=1)
                pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
                if pedido:
                    quantidade = st.number_input("Quantidade", value=pedido.quantidade, min_value=1)
                    status_options = ["pendente", "enviado", "cancelado"]
                    index = status_options.index(pedido.status) if pedido.status in status_options else 0
                    status = st.selectbox("Status", status_options, index=index)
                    if st.button("Atualizar pedido"):
                        atualizar_pedido(db, pedido_id, quantidade, status)
                        st.success("Pedido atualizado com sucesso.")
                    if st.button("Excluir pedido"):
                        deletar_pedido(db, pedido_id)
                        st.success("Pedido excluído com sucesso.")
                else:
                    st.info("Pedido não encontrado.")
            else:
                st.info("Não há pedidos registrados.")

        elif menu == "Criar Pedido":
            st.subheader("Criar novo pedido")
            produtos = get_produtos(db)
            fornecedores = get_fornecedores(db)

            if not produtos:
                st.warning("Nenhum produto cadastrado.")
            elif not fornecedores:
                st.warning("Nenhum fornecedor cadastrado.")
            else:
                produto_nomes = [p.nome for p in produtos]
                produto_sel = st.selectbox("Selecione o produto", produto_nomes)
                produto_obj = next(p for p in produtos if p.nome == produto_sel)

                fornecedor_nomes = [f.nome for f in fornecedores]
                fornecedor_sel = st.selectbox("Selecione o fornecedor", fornecedor_nomes)
                fornecedor_obj = next(f for f in fornecedores if f.nome == fornecedor_sel)

                quantidade = st.number_input("Quantidade", min_value=1, value=1)

                media = calcular_media_vendas(db, produto_obj.id)
                sugestao = max(1, int(media * 30 - produto_obj.estoque_atual))
                st.write(f"Quantidade sugerida para repor estoque para 30 dias: {sugestao} unidades.")

                if st.button("Criar pedido"):
                    criar_pedido(db, produto_obj.id, fornecedor_obj.id, quantidade)
                    st.success("Pedido criado com sucesso.")

        elif menu == "Relatórios":
            st.subheader("Relatórios Resumidos")
            total_produtos = db.query(func.count(Produto.id)).scalar()
            total_vendas_30d = sum(v.quantidade for v in get_vendas_ultimos_30_dias(db))
            total_pedidos = db.query(func.count(Pedido.id)).scalar()

            st.markdown(f"- Total de produtos cadastrados: {total_produtos}")
            st.markdown(f"- Total de vendas nos últimos 30 dias: {total_vendas_30d} unidades")
            st.markdown(f"- Total de pedidos realizados: {total_pedidos}")

        elif menu == "Fornecedores":
            st.subheader("Gestão de fornecedores")

            fornecedores = get_fornecedores(db)
            if fornecedores:
                df_fornecedores = pd.DataFrame([{
                    "ID": f.id,
                    "Nome": f.nome,
                    "CNPJ": f.cnpj,
                    "Email": f.email,
                    "Telefone": f.telefone,
                    "Segmento": f.segmento
                } for f in fornecedores])
                st.dataframe(df_fornecedores, use_container_width=True)
            else:
                st.info("Nenhum fornecedor cadastrado.")

            st.markdown("Adicionar novo fornecedor")
            with st.form("form_fornecedor"):
                nome = st.text_input("Nome")
                cnpj = st.text_input("CNPJ")
                email = st.text_input("Email")
                telefone = st.text_input("Telefone")
                segmento = st.text_input("Segmento")

                submitted = st.form_submit_button("Adicionar fornecedor")
                if submitted:
                    if not nome or not cnpj:
                        st.error("Nome e CNPJ são obrigatórios.")
                    else:
                        criar_fornecedor(db, nome, cnpj, email, telefone, segmento)
                        st.success(f"Fornecedor '{nome}' criado com sucesso.")
                        st.experimental_rerun()

if __name__ == "__main__":
    main()
