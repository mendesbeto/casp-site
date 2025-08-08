import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Dúvidas e Contato", layout="wide")

# --- FUNÇÕES ---
@st.cache_data
def carregar_dados_institucionais():
    return pd.read_csv('data/institucional.csv').iloc[0]

def salvar_contato(nome, email, telefone, assunto, mensagem):
    """Salva a mensagem de contato no arquivo CSV."""
    filepath = 'data/contatos.csv'
    
    # Define o próximo ID
    new_id = 1
    file_exists = os.path.exists(filepath)
    if file_exists:
        try:
            df_contatos = pd.read_csv(filepath)
            if not df_contatos.empty:
                new_id = df_contatos['ID'].max() + 1
        except pd.errors.EmptyDataError:
            # O arquivo existe mas está vazio
            pass

    # Cria um novo DataFrame com os dados do formulário
    novo_contato = pd.DataFrame([{
        'ID': new_id,
        'TIMESTAMP': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'NOME': nome,
        'EMAIL': email,
        'TELEFONE': telefone,
        'ASSUNTO': assunto,
        'MENSAGEM': mensagem,
        'STATUS_ATENDIMENTO': 'NOVO'
    }])

    # Adiciona o novo contato ao CSV, criando o cabeçalho se o arquivo não existir
    novo_contato.to_csv(filepath, mode='a', header=not file_exists or os.path.getsize(filepath) == 0, index=False)

# --- CARREGAMENTO DOS DADOS ---
institucional = carregar_dados_institucionais()

# --- LAYOUT DA PÁGINA ---
st.title("Dúvidas e Contato")
st.write("Tem alguma pergunta ou sugestão? Entre em contato conosco!")

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
            # Validação simples
            if not nome or not email or not assunto or not mensagem:
                st.warning("Por favor, preencha todos os campos obrigatórios.")
            else:
                salvar_contato(nome, email, telefone, assunto, mensagem)
                st.success("✅ Mensagem enviada com sucesso! Entraremos em contato em breve.")
