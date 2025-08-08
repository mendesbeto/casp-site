import streamlit as st
import pandas as pd
import os
import secrets
from datetime import datetime, timedelta

# Importa a função de hash do nosso novo módulo
from auth import hash_password
from email_utils import send_recovery_email

st.set_page_config(page_title="Recuperar Senha", layout="centered")

# --- FUNÇÕES DE DADOS ---

def carregar_usuarios():
    """Carrega o arquivo de usuários, criando-o se não existir."""
    filepath = 'data/usuarios.csv'
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        cols = ['ID','NOME','CPF','EMAIL','CEP','LOGRADOURO','NUMERO','COMPLEMENTO','BAIRRO','CIDADE','ESTADO','SENHA_HASH','STATUS','DATA_CADASTRO','NIVEL_ACESSO','TOKEN_RECUPERACAO','DATA_EXPIRACAO_TOKEN']
        pd.DataFrame(columns=cols).to_csv(filepath, index=False)
        return pd.DataFrame(columns=cols)
    return pd.read_csv(filepath)

def atualizar_usuario(df_usuarios):
    """Salva o DataFrame de usuários de volta no CSV."""
    filepath = 'data/usuarios.csv'
    df_usuarios.to_csv(filepath, index=False)

# --- LÓGICA DA PÁGINA ---

st.title("🔑 Recuperação de Senha")

# --- ETAPA 1: SOLICITAR TOKEN DE RECUPERAÇÃO ---
st.header("Etapa 1: Solicitar Token")
st.write("Digite seu email para receber um token de recuperação.")

with st.form("form_request_token"):
    email_solicitacao = st.text_input("Seu email de cadastro")
    request_button = st.form_submit_button("Gerar Token")

    if request_button and email_solicitacao:
        df_usuarios = carregar_usuarios()
        # Garante que a coluna de email seja do tipo string para evitar erros
        df_usuarios['EMAIL'] = df_usuarios['EMAIL'].astype(str)
        user_index = df_usuarios[df_usuarios['EMAIL'].str.lower() == email_solicitacao.lower()].index

        if not user_index.empty:
            # Gera token e data de expiração (15 minutos)
            token = secrets.token_urlsafe(32)
            expiration_date = datetime.now() + timedelta(minutes=15)
            
            # Atualiza o DataFrame
            df_usuarios.loc[user_index, 'TOKEN_RECUPERACAO'] = token
            df_usuarios.loc[user_index, 'DATA_EXPIRACAO_TOKEN'] = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Salva as alterações no arquivo
            atualizar_usuario(df_usuarios)
            
            # Envia o token por email
            if send_recovery_email(email_solicitacao, token):
                st.success("✅ Token de recuperação enviado para o seu email. Verifique sua caixa de entrada (e spam).")
            else:
                st.error("❌ Ocorreu um erro ao tentar enviar o email. Por favor, contate o suporte.")
        else:
            st.error("Email não encontrado em nosso sistema.")

st.divider()

# --- ETAPA 2: REDEFINIR A SENHA ---
st.header("Etapa 2: Redefinir Senha")
st.write("Cole o token recebido e defina sua nova senha.")

with st.form("form_reset_password", clear_on_submit=True):
    token_input = st.text_input("Token de Recuperação")
    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_nova_senha = st.text_input("Confirme a Nova Senha", type="password")
    reset_button = st.form_submit_button("Redefinir Senha")

    if reset_button:
        if not all([token_input, nova_senha, confirmar_nova_senha]):
            st.warning("Por favor, preencha todos os campos.")
        elif nova_senha != confirmar_nova_senha:
            st.error("As senhas não coincidem.")
        else:
            df_usuarios = carregar_usuarios()
            user_data = df_usuarios[df_usuarios['TOKEN_RECUPERACAO'] == token_input]

            if not user_data.empty:
                user_index = user_data.index[0]
                expiration_str = str(user_data.iloc[0]['DATA_EXPIRACAO_TOKEN'])
                
                if pd.notna(expiration_str) and datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S") > datetime.now():
                    df_usuarios.loc[user_index, 'SENHA_HASH'] = hash_password(nova_senha)
                    df_usuarios.loc[user_index, 'TOKEN_RECUPERACAO'] = ''
                    df_usuarios.loc[user_index, 'DATA_EXPIRACAO_TOKEN'] = ''
                    atualizar_usuario(df_usuarios)
                    st.success("✅ Senha redefinida com sucesso! Você já pode fazer o login.")
                else:
                    st.error("Token inválido ou expirado. Por favor, gere um novo token.")
            else:
                st.error("Token inválido ou expirado. Por favor, gere um novo token.")