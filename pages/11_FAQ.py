import streamlit as st
import pandas as pd

st.set_page_config(page_title="Perguntas Frequentes", layout="wide")

@st.cache_data
def carregar_dados_faq():
    try:
        return pd.read_csv('data/faq.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['FAQ_ID', 'PERGUNTA', 'RESPOSTA', 'STATUS'])

st.title("❓ Perguntas Frequentes (FAQ)")
st.write("Encontre aqui as respostas para as dúvidas mais comuns sobre nossa associação.")

# --- BARRA DE BUSCA ---
search_term = st.text_input("🔎 Buscar na FAQ", placeholder="Digite uma palavra-chave...")

df_faq = carregar_dados_faq()

faq_ativos = df_faq[df_faq['STATUS'] == 'ATIVO']

# --- LÓGICA DE FILTRAGEM ---
if search_term:
    faq_filtrados = faq_ativos[
        faq_ativos['PERGUNTA'].str.contains(search_term, case=False, na=False) |
        faq_ativos['RESPOSTA'].str.contains(search_term, case=False, na=False)
    ]
else:
    faq_filtrados = faq_ativos

if faq_filtrados.empty:
    if search_term:
        st.warning("Nenhum resultado encontrado para sua busca.")
    else:
        st.info("Nenhuma pergunta frequente cadastrada no momento.")
else:
    for _, item in faq_filtrados.iterrows():
        with st.expander(item['PERGUNTA']):
            st.markdown(item['RESPOSTA'], unsafe_allow_html=True)