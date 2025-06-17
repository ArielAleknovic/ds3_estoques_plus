import streamlit as st
st.set_page_config(page_title="Sistema de Monitoramento de Estoques", layout="wide")

from utils.db import SessionLocal, engine, Base
from models.models import Produto, Venda, Pedido, Fornecedor, Usuario
from utils.auth import *
from utils.services import *
from utils.utils import *
from utils.view import *
from utils.styles import styles

Base.metadata.create_all(bind=engine)

def main():
    st.markdown("<style>header {visibility: hidden;}</style>", unsafe_allow_html=True)
    img_base64 = get_base64_image("/app/.streamlit/fundo 1.jpeg")
    st.markdown(styles(img_base64), unsafe_allow_html=True)

    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    usuario = st.session_state.usuario

    if not usuario:
        login_page()
        return

    st.sidebar.write(f"Usuário logado: {usuario.name}")

    with SessionLocal() as db:
        menu = st.sidebar.radio("Navegação", [
            "Home", "Dashboard", "Pedidos", "Criar Pedido", "Relatórios",
            "Criar Fornecedor", "Fornecedores", "Criar Produtos", "Produtos"
        ])

        if menu == "Home":
            home()
        elif menu == "Dashboard":
            exibir_dashboard(db)
        elif menu == "Pedidos":
            exibir_pedidos(db)
        elif menu == "Criar Pedido":
            criar_pedido_view(db)
        elif menu == "Relatórios":
            gerar_relatorio(db)
        elif menu == "Criar Fornecedor":
            criar_fornecedores(db)
        elif menu == "Fornecedores":
            fornecedores(db)
        elif menu == "Produtos":
            produtos(db)
        elif menu == "Criar Produtos":
            criar_produtos(db)

if __name__ == "__main__":
    main()
