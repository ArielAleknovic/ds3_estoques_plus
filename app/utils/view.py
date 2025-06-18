from datetime import date, timedelta
import base64

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import func
from sqlalchemy.orm import Session

from utils.db import SessionLocal, engine, Base
from models.models import *
from utils.auth import *
from utils.services import *
from utils.utils import *
from utils.view import *

from utils.services import *


sns.set_theme(style="whitegrid")


def home():
    st.title("Bem-vindo ao Sistema de Monitoramento de Estoques")
    st.markdown("Este sistema permite acompanhar estoques, vendas, pedidos e fornecedores de forma simples e eficiente.")

    if st.button("Logout"):
                st.session_state.usuario = None
                st.rerun()  # força atualização da página para voltar ao login

def exibir_pedidos(db):
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
                valido, erro = validar_quantidade(quantidade)
                if not valido:
                    st.error(f"Erro na quantidade: {erro}")
                else:
                    atualizar_pedido(db, pedido_id, int(quantidade), status)
                    st.success("Pedido atualizado com sucesso.")
                    st.rerun()

            if st.button("Excluir pedido"):
                deletar_pedido(db, pedido_id)
                st.success("Pedido excluído com sucesso.")
                st.rerun()
        else:
            st.info("Pedido não encontrado.")
    else:
        st.info("Não há pedidos registrados.")

def criar_pedido_view(db):
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
            valido, erro = validar_quantidade(quantidade)
            if not valido:
                st.error(f"Erro na quantidade: {erro}")
            else:
                criar_pedido(db, produto_obj.id, fornecedor_obj.id, int(quantidade))
                st.success("Pedido criado com sucesso.")
                st.rerun()

def criar_fornecedores(db):
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
                    erros = []

                    validacoes = {
                        "Nome": validar_nome(nome),
                        "CNPJ": validar_cnpj(cnpj),
                        "Email": validar_email(email) if email else (True, None),
                        "Telefone": validar_telefone(telefone) if telefone else (True, None),
                    }

                    for campo, (valido, msg) in validacoes.items():
                        if not valido:
                            erros.append(f"{campo}: {msg}")

                    if erros:
                        for erro in erros:
                            st.error(erro)
                    else:
                        criar_fornecedor(db, nome, cnpj, email, telefone, segmento)
                        st.success(f"Fornecedor '{nome}' criado com sucesso.")
                        st.rerun()

def fornecedores(db):
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
                    erros = []

                    validacoes = {
                        "Nome": validar_nome(nome_edit),
                        "CNPJ": validar_cnpj(cnpj_edit),
                        "Email": validar_email(email_edit) if email_edit else (True, None),
                        "Telefone": validar_telefone(telefone_edit) if telefone_edit else (True, None),
                    }

                    for campo, (valido, msg) in validacoes.items():
                        if not valido:
                            erros.append(f"{campo}: {msg}")

                    if erros:
                        for erro in erros:
                            st.error(erro)
                    else:
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

def produtos(db):
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
                    st.rerun()
            
                if st.button("Excluir produto"):
                    deletar_produto(db, produto_id)
                    st.success("Produto excluído com sucesso.")
                    st.rerun()
            else:
                st.info("Produto não encontrado.")

def criar_produtos(db):
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

def cadastrar_usuario():
            st.subheader("Novo Usuário")
            with st.form("form_cadastro"):
                nome = st.text_input("Nome")
                email = st.text_input("Email")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Cadastrar"):
                    db = SessionLocal()
                    criar_usuario(db, nome, email, senha)
                    st.success("Usuário criado com sucesso!")


def login_page():
    st.markdown(
        """
        <style>
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1, 2, 1])  # proporções
    
    with col2:  # Centralizar o formulário
        st.title("Sistema de Estoque Plus")
        with st.form("login_form"):
            st.subheader("Login")
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


def exibir_dashboard(db):
    st.subheader("Visão Geral dos Estoques e Recomendações de Pedido")
    produtos = get_produtos(db)

    if not produtos:
        st.info("Não há produtos cadastrados.")
        return

    df = pd.DataFrame([{
        "Produto": p.nome,
        "Estoque Atual": p.estoque_atual,
        "Preço (R$)": float(p.preco),
        "Média diária de vendas (últimos 30 dias)": round(calcular_media_vendas(db, p.id), 2)
    } for p in produtos])

    st.dataframe(df, use_container_width=True)

    # Sugestão de pedidos
    sugestoes = [
        {"Produto": p.nome, "Quantidade Sugerida": max(0, int(calcular_media_vendas(db, p.id) * 30 - p.estoque_atual))}
        for p in produtos
    ]
    df_sugestoes = pd.DataFrame(sugestoes)
    st.dataframe(df_sugestoes, use_container_width=True)

    # Estoque Atual com Plotly
    st.markdown("### Estoque Atual por Produto")
    fig_estoque = px.bar(df, x='Produto', y='Estoque Atual', color='Produto', title='Estoque Atual por Produto')
    st.plotly_chart(fig_estoque, use_container_width=True)

    # Vendas Diárias (Últimos 30 dias)
    st.markdown("### Vendas Diárias nos Últimos 30 Dias")
    data_limite = date.today() - timedelta(days=30)
    vendas_30d = db.query(Venda.data_venda, func.sum(Venda.quantidade)).filter(
        Venda.data_venda >= data_limite
    ).group_by(Venda.data_venda).order_by(Venda.data_venda).all()

    if vendas_30d:
        df_vendas = pd.DataFrame(vendas_30d, columns=["Data", "Quantidade"])
        fig_vendas = px.line(df_vendas, x="Data", y="Quantidade", markers=True, title="Vendas Diárias (Últimos 30 dias)")
        st.plotly_chart(fig_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda nos últimos 30 dias.")

    # Status dos Pedidos
    st.markdown("### Status dos Pedidos")
    pedidos = get_pedidos(db)
    if pedidos:
        status_counts = pd.Series([p.status for p in pedidos]).value_counts()
        fig_status = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title="Status dos Pedidos")
        st.plotly_chart(fig_status)
    else:
        st.info("Nenhum pedido registrado.")

    # Quantidade Sugerida
    st.markdown("### Quantidade Sugerida para Pedido (30 dias)")
    fig_sugestoes = px.bar(df_sugestoes, x="Produto", y="Quantidade Sugerida", color="Produto",
                           title="Sugestão de Reposição")
    st.plotly_chart(fig_sugestoes, use_container_width=True)

    # Top 5 Produtos mais Vendidos
    st.markdown("### Top 5 Produtos mais Vendidos (30 dias)")
    vendas_por_produto = db.query(
        Produto.nome,
        func.sum(Venda.quantidade)
    ).join(Venda).filter(
        Venda.data_venda >= data_limite
    ).group_by(Produto.nome).order_by(func.sum(Venda.quantidade).desc()).limit(5).all()

    if vendas_por_produto:
        df_top5 = pd.DataFrame(vendas_por_produto, columns=["Produto", "Quantidade Vendida"])
        fig_top5 = px.bar(df_top5, x="Produto", y="Quantidade Vendida", color="Produto", title="Top 5 Produtos Vendidos")
        st.plotly_chart(fig_top5)

    # Correlação Preço x Estoque
    st.markdown("### Correlação: Preço x Estoque")
    fig_corr = px.scatter(df, x="Preço (R$)", y="Estoque Atual", color="Produto", size="Média diária de vendas (últimos 30 dias)",
                          title="Relação Preço x Estoque x Demanda")
    st.plotly_chart(fig_corr)

    # Giro de Estoque
    st.markdown("### Análise de Giro de Estoque")
    df['Giro Estoque (30 dias)'] = df['Média diária de vendas (últimos 30 dias)'] / df['Estoque Atual'].replace(0, 1)
    df_sorted = df.sort_values(by='Giro Estoque (30 dias)', ascending=False)
    st.dataframe(df_sorted)

    # Relatório de Vendas por Produto, Período e Fornecedor
    st.markdown("### Relatório de Vendas Personalizado")
    produtos_opcoes = [p.nome for p in produtos]
    produto_selecionado = st.selectbox("Produto:", ["Todos"] + produtos_opcoes)
    fornecedores_opcoes = list({f.nome for f in get_fornecedores(db)})
    fornecedor_selecionado = st.selectbox("Fornecedor:", ["Todos"] + fornecedores_opcoes)
    data_ini = st.date_input("Data inicial", value=date.today() - timedelta(days=30))
    data_fim = st.date_input("Data final", value=date.today())

    query = db.query(Produto.nome.label("Produto"), Venda.data_venda.label("Data"), Venda.quantidade.label("Quantidade"),
                     Fornecedor.nome.label("Fornecedor")).join(Venda).join(Fornecedor)
    query = query.filter(Venda.data_venda.between(data_ini, data_fim))
    if produto_selecionado != "Todos":
        query = query.filter(Produto.nome == produto_selecionado)
    if fornecedor_selecionado != "Todos":
        query = query.filter(Fornecedor.nome == fornecedor_selecionado)

    df_relatorio = pd.read_sql(query.statement, db.bind)
    st.dataframe(df_relatorio)

    from sklearn.linear_model import LinearRegression
    import numpy as np
    import plotly.graph_objects as go

    # --- Vendas completas (últimos 30 dias) ---
    data_limite = date.today() - timedelta(days=30)
    vendas = db.query(Venda.data_venda, Produto.nome, func.sum(Venda.quantidade)).join(Produto).filter(
        Venda.data_venda >= data_limite
    ).group_by(Venda.data_venda, Produto.nome).order_by(Venda.data_venda).all()

    if vendas:
        df_sim = pd.DataFrame(vendas, columns=["Data", "Produto", "Quantidade"])
        df_sim["Data"] = pd.to_datetime(df_sim["Data"])

        produto_selecionado = st.selectbox("Selecione o produto para simulação de demanda:", df_sim["Produto"].unique())

        df_item = df_sim[df_sim["Produto"] == produto_selecionado].copy()
        df_item = df_item.set_index("Data").resample("D").sum().fillna(0)
        df_item.reset_index(inplace=True)

        # Média móvel
        df_item["MediaMovel_7d"] = df_item["Quantidade"].rolling(window=7, min_periods=1).mean()

        # Regressão linear
        df_item["Dias"] = (df_item["Data"] - df_item["Data"].min()).dt.days
        X = df_item[["Dias"]]
        y = df_item["Quantidade"]
        modelo = LinearRegression().fit(X, y)
        df_item["Previsao_Linear"] = modelo.predict(X)

        # Gráfico interativo
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(x=df_item["Data"], y=df_item["Quantidade"], name="Real", mode="lines+markers"))
        fig_sim.add_trace(go.Scatter(x=df_item["Data"], y=df_item["MediaMovel_7d"], name="Média Móvel 7d"))
        fig_sim.add_trace(go.Scatter(x=df_item["Data"], y=df_item["Previsao_Linear"], name="Tendência das vendas"))
        fig_sim.update_layout(title=f"Simulação de Demanda Futura - {produto_selecionado}")
        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.info("Não há dados suficientes para simulação.")
