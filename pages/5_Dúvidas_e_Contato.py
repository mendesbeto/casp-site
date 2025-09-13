
import streamlit as st
import pandas as pd
from datetime import datetime
from social_utils import display_social_media_links
from auth import get_db_connection, insert_record, get_max_id

display_social_media_links()
st.set_page_config(page_title="Dúvidas e Contato", layout="wide")

# --- FUNÇÕES DE BANCO DE DADOS ---
@st.cache_data
def carregar_dados_institucionais():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM institucional LIMIT 1", conn)
        return df.iloc[0]
    except Exception as e:
        st.error(f"Erro ao carregar dados institucionais: {e}")
        return None
    finally:
        conn.close()

def salvar_contato(nome, email, telefone, assunto, mensagem):
    """Salva a mensagem de contato no banco de dados."""
    new_id = get_max_id('contatos', 'ID') + 1
    novo_contato = {
        'ID': int(new_id),
        'TIMESTAMP': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'NOME': nome,
        'EMAIL': email,
        'TELEFONE': telefone,
        'ASSUNTO': assunto,
        'MENSAGEM': mensagem,
        'STATUS_ATENDIMENTO': 'NOVO'
    }
    insert_record('contatos', novo_contato)

# --- CARREGAMENTO DOS DADOS ---
institucional = carregar_dados_institucionais()

# --- LAYOUT DA PÁGINA ---
st.title("Dúvidas e Contato")
st.write("Tem alguma pergunta ou sugestão? Entre em contato conosco!")

if institucional is not None:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Nossas Informações")
        st.markdown(f"**📧 Email:** {institucional['EMAIL_CONTATO']}")
        st.markdown(f"**📞 Telefone:** {institucional['TELEFONE_CONTATO']}")
        st.markdown(f"**📍 Endereço:** {institucional['ENDERECO']}")

    with col2:
        st.subheader("Envie-nos uma Mensagem")
        with st.form(key="form_contato", clear_on_submit=True):
            nome = st.text_input("Nome Completo", placeholder="Seu nome")
            email = st.text_input("Email", placeholder="seu@email.com")
            telefone = st.text_input("Telefone (Opcional)")
            assunto = st.text_input("Assunto")
            mensagem = st.text_area("Mensagem", height=150)
            
            submit_button = st.form_submit_button(label="Enviar Mensagem")

            if submit_button:
                if not nome or not email or not assunto or not mensagem:
                    st.warning("Por favor, preencha todos os campos obrigatórios.")
                else:
                    salvar_contato(nome, email, telefone, assunto, mensagem)
                    st.success("✅ Mensagem enviada com sucesso! Entraremos em contato em breve.")
else:
    st.error("Não foi possível carregar as informações de contato.")
