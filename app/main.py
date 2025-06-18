import streamlit as st
from utils.db import SessionLocal, engine, Base
from models.models import Produto, Venda, Pedido, Fornecedor, Usuario
from utils.auth import *
from utils.services import *
from utils.utils import *
from utils.view import *
from utils.styles import styles

st.set_page_config(page_title="Sistema de Monitoramento de Estoques", layout="wide")

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

        opcoes = {
            "Home": home,
            "Dashboard": lambda: exibir_dashboard(db),
            "Pedidos": lambda: exibir_pedidos(db),
            "Criar Pedido": lambda: criar_pedido_view(db),
            "Criar Fornecedor": lambda: criar_fornecedores(db),
            "Fornecedores": lambda: fornecedores(db),
            "Produtos": lambda: produtos(db),
            "Criar Produtos": lambda: criar_produtos(db),
        }

        if menu in opcoes:
            opcoes[menu]()
        else:
            st.warning("Opção inválida.")

if __name__ == "__main__":
    main()
