
import streamlit as st
import pandas as pd
from social_utils import display_social_media_links
from auth import get_db_connection

display_social_media_links()
st.set_page_config(page_title="Perguntas Frequentes", layout="wide")

@st.cache_data
def carregar_dados_faq():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM faq WHERE STATUS = 'ATIVO'", conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar FAQ: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

st.title("❓ Perguntas Frequentes (FAQ)")
st.write("Encontre aqui as respostas para as dúvidas mais comuns sobre nossa associação.")

search_term = st.text_input("🔎 Buscar na FAQ", placeholder="Digite uma palavra-chave...")

df_faq = carregar_dados_faq()

if search_term:
    faq_filtrados = df_faq[
        df_faq['PERGUNTA'].str.contains(search_term, case=False, na=False) |
        df_faq['RESPOSTA'].str.contains(search_term, case=False, na=False)
    ]
else:
    faq_filtrados = df_faq

if faq_filtrados.empty:
    if search_term:
        st.warning("Nenhum resultado encontrado para sua busca.")
    else:
        st.info("Nenhuma pergunta frequente cadastrada no momento.")
else:
    for _, item in faq_filtrados.iterrows():
        with st.expander(item['PERGUNTA']):
            st.markdown(item['RESPOSTA'], unsafe_allow_html=True)
