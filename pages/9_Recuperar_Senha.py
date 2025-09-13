
import streamlit as st
import sqlite3
import secrets
from datetime import datetime, timedelta
from social_utils import display_social_media_links
from auth import hash_password, get_user_by_email, get_db_connection
from email_utils import send_recovery_email

display_social_media_links()
st.set_page_config(page_title="Recuperar Senha", layout="centered")

# --- FUNÇÕES DE BANCO DE DADOS ---
def update_user_token(user_id, token, expiration_date):
    """Atualiza o token de recuperação e a data de expiração de um usuário."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "UPDATE usuarios SET TOKEN_RECUPERACAO = ?, DATA_EXPIRACAO_TOKEN = ? WHERE ID = ?"
        cursor.execute(query, (token, expiration_date.strftime("%Y-%m-%d %H:%M:%S"), user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro de banco de dados: {e}")
        return False
    finally:
        conn.close()

def get_user_by_token(token):
    """Busca um usuário pelo token de recuperação."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE TOKEN_RECUPERACAO = ?", (token,))
    user = cursor.fetchone()
    conn.close()
    return user

def reset_user_password(user_id, new_password_hash):
    """Redefine a senha do usuário e limpa o token."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "UPDATE usuarios SET SENHA_HASH = ?, TOKEN_RECUPERACAO = NULL, DATA_EXPIRACAO_TOKEN = NULL WHERE ID = ?"
        cursor.execute(query, (new_password_hash, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro de banco de dados ao redefinir a senha: {e}")
        return False
    finally:
        conn.close()

# --- LÓGICA DA PÁGINA ---
st.title("🔑 Recuperação de Senha")

# --- ETAPA 1: SOLICITAR TOKEN ---
st.header("Etapa 1: Solicitar Token")
st.write("Digite seu email para receber um token de recuperação.")

with st.form("form_request_token"):
    email_solicitacao = st.text_input("Seu email de cadastro")
    request_button = st.form_submit_button("Gerar Token")

    if request_button and email_solicitacao:
        user = get_user_by_email(email_solicitacao)

        if user:
            token = secrets.token_urlsafe(32)
            expiration_date = datetime.now() + timedelta(minutes=15)
            
            if update_user_token(user['ID'], token, expiration_date):
                try:
                    email_creds = st.secrets["email_credentials"]
                    base_url = st.secrets["app_config"]["base_url"]
                    email_config = {
                        "email_address": email_creds["email_address"],
                        "email_password": email_creds["email_password"],
                        "base_url": base_url
                    }
                    if send_recovery_email(email_solicitacao, token, email_config):
                        st.success("✅ Token de recuperação enviado para o seu email. Verifique sua caixa de entrada (e spam).")
                    else:
                        st.error("❌ Ocorreu um erro ao tentar enviar o email. Por favor, contate o suporte.")
                except (KeyError, FileNotFoundError):
                    st.error("As configurações de email não foram encontradas. O administrador precisa configurar o arquivo secrets.toml.")
        else:
            st.error("Email não encontrado em nosso sistema.")

st.divider()

# --- ETAPA 2: REDEFINIR A SENHA ---
st.header("Etapa 2: Redefinir Senha")
st.write("Cole o token recebido e defina sua nova senha.")

query_params = st.query_params
pre_filled_token = query_params.get("token", "")

with st.form("form_reset_password", clear_on_submit=True):
    token_input = st.text_input("Token de Recuperação", value=pre_filled_token)
    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_nova_senha = st.text_input("Confirme a Nova Senha", type="password")
    reset_button = st.form_submit_button("Redefinir Senha")

    if reset_button:
        if not all([token_input, nova_senha, confirmar_nova_senha]):
            st.warning("Por favor, preencha todos os campos.")
        elif nova_senha != confirmar_nova_senha:
            st.error("As senhas não coincidem.")
        else:
            user = get_user_by_token(token_input)

            if user:
                expiration_str = user['DATA_EXPIRACAO_TOKEN']
                if expiration_str and datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S") > datetime.now():
                    new_hash = hash_password(nova_senha)
                    if reset_user_password(user['ID'], new_hash):
                        st.success("✅ Senha redefinida com sucesso! Você já pode fazer o login.")
                else:
                    st.error("Token inválido ou expirado. Por favor, gere um novo token.")
            else:
                st.error("Token inválido ou expirado. Por favor, gere um novo token.")
