import streamlit as st
st.set_page_config(page_title="Sistema de Monitoramento de Estoques", layout="wide")

import matplotlib.pyplot as plt
import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from db import SessionLocal, engine, Base
from models import Produto, Venda, Pedido, Fornecedor, Usuario
from auth import autenticar_usuario, criar_usuario
from services import *



Base.metadata.create_all(bind=engine)

#pagina de login 
def login_page():
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            usuario = autenticar_usuario(username, password)
            if usuario:
                st.session_state.usuario = usuario
                st.success(f"Bem-vindo, {usuario.name}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    st.markdown("---")
    with st.form("cadastro_form"):
        st.subheader("Cadastrar novo usuário")
        new_username = st.text_input("Usuário para cadastro")
        new_name = st.text_input("Nome completo")
        new_password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirme a senha", type="password")
        cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            if new_password != confirm_password:
                st.error("As senhas não conferem.")
            else:
                sucesso = criar_usuario(new_username, new_name, new_password)
                if sucesso:
                    st.success("Usuário cadastrado com sucesso!")
                else:
                    st.warning("Usuário já existe.")

#aplicação
def main():
    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    usuario = st.session_state.usuario

    if not usuario:
        login_page()
        return

    st.sidebar.write(f"Usuário logado: {usuario.name}")


    st.markdown(
        """
        <style>
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )
#tela de fundo
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

#navegação
    with SessionLocal() as db:
        menu = st.sidebar.radio("Navegação", ["Home", "Dashboard", "Pedidos", "Criar Pedido", "Relatórios", "Criar Fornecedor", "Fornecedores", "Criar Produtos", "Produtos"])

        if menu == "Home":
            st.title("Bem-vindo ao Sistema de Monitoramento de Estoques")
            st.markdown("Este sistema permite acompanhar estoques, vendas, pedidos e fornecedores de forma simples e eficiente.")

            if st.button("Logout"):
                st.session_state.usuario = None
                st.rerun()  # força atualização da página para voltar ao login

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

        elif menu == "Criar Fornecedor":
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
                        st.rerun()
        
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

            fornecedor_id = st.number_input("Informe o ID do fornecedor", min_value=1, step=1)
            fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()

            if fornecedor:
                nome_edit = st.text_input("Nome", value=fornecedor.nome, key="edit_nome")
                cnpj_edit = st.text_input("CNPJ", value=fornecedor.cnpj, key="edit_cnpj")
                email_edit = st.text_input("Email", value=fornecedor.email, key="edit_email")
                telefone_edit = st.text_input("Telefone", value=fornecedor.telefone, key="edit_telefone")
                segmento_edit = st.text_input("Segmento", value=fornecedor.segmento, key="edit_segmento")

                if st.button("Atualizar fornecedor"):
                    try:
                        atualizar_fornecedor(db, fornecedor_id, nome_edit, cnpj_edit, email_edit, telefone_edit, segmento_edit)
                        st.success("Fornecedor atualizado com sucesso.")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Erro ao atualizar: {e}")

                if st.button("Excluir fornecedor"):
                    deletar_fornecedor(db, fornecedor_id)
                    st.success("Fornecedor excluído com sucesso.")
                    st.rerun()
            else:
                st.info("Fornecedor não encontrado.")
        
        elif menu == "Produtos":
            st.subheader("Gestão de Produtos")

            produtos = get_produtos(db)
            if produtos:
                df_produtos = pd.DataFrame([{
                    "ID": p.id,
                    "Nome": p.nome,
                    "Estoque Atual": p.estoque_atual,
                    "Preço (R$)": float(p.preco)
                } for p in produtos])
                st.dataframe(df_produtos, use_container_width=True)
            else:
                st.info("Nenhum produto cadastrado.")

            produto_id = st.number_input("Informe o ID do produto", min_value=1, step=1)
            produto = db.query(Produto).filter(Produto.id == produto_id).first()

            if produto:
                nome_edit = st.text_input("Nome", value=produto.nome, key="edit_nome_prod")
                estoque_edit = st.number_input("Estoque", value=produto.estoque_atual, key="edit_estoque_prod")
                preco_edit = st.number_input("Preço", value=float(produto.preco), format="%.2f", key="edit_preco_prod")                
                if st.button("Atualizar produto"):
                    atualizar_produto(db, produto_id, nome_edit, estoque_edit, preco_edit)
                    st.success("Produto atualizado com sucesso.")
                    st.experimental_rerun()
            
                if st.button("Excluir produto"):
                    deletar_produto(db, produto_id)
                    st.success("Produto excluído com sucesso.")
                    st.rerun()
            else:
                st.info("Produto não encontrado.")

        elif menu == "Criar Produtos":
            st.subheader("Adicionar novo produto")
            with st.form("form_produto"):
                nome_prod = st.text_input("Nome do Produto")
                estoque = st.number_input("Estoque Inicial", min_value=0, value=0)
                preco = st.number_input("Preço", min_value=0.0, value=0.0, format="%.2f")

                submitted = st.form_submit_button("Adicionar produto")
                if submitted:
                    if not nome_prod:
                        st.error("O nome do produto é obrigatório.")
                    else:
                        criar_produto(db, nome_prod, estoque, preco)
                        st.success(f"Produto '{nome_prod}' adicionado com sucesso.")
                        st.rerun()
        
        elif menu == "Cadastrar Usuário":
            st.subheader("Novo Usuário")
            with st.form("form_cadastro"):
                nome = st.text_input("Nome")
                email = st.text_input("Email")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Cadastrar"):
                    db = SessionLocal()
                    criar_usuario(db, nome, email, senha)
                    st.success("Usuário criado com sucesso!")

if __name__ == "__main__":
    main()
