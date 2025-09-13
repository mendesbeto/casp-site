
import streamlit as st
import pandas as pd
from social_utils import display_social_media_links
from auth import get_db_connection

display_social_media_links()
st.set_page_config(page_title="Benefícios", layout="wide")

@st.cache_data
def carregar_dados_beneficios():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM beneficios", conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar benefícios: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

df_beneficios = carregar_dados_beneficios()

st.title("Vantagens de ser um Associado")
st.write("""
A nossa associação trabalha continuamente para oferecer um leque de benefícios que impactam positivamente a vida dos nossos membros. 
O nosso foco principal é garantir economia através de uma rede de convênios robusta, mas as vantagens não param por aí.
""")

st.divider()

if not df_beneficios.empty:
    for index, beneficio in df_beneficios.iterrows():
        st.header(f"{beneficio['ICONE']} {beneficio['TITULO']}")
        st.write(beneficio['DESCRICAO_BENEFICIO'])
        st.write("---")
else:
    st.warning("Ainda não há benefícios cadastrados. Volte em breve!")

st.header("Pronto para Economizar?")
st.write("Nossos convênios são a porta de entrada para um mundo de descontos. Veja a lista completa de parceiros e comece a aproveitar agora mesmo.")

if st.button("Ver Todos os Convênios", type="primary", use_container_width=True):
    st.switch_page("pages/2_Convênios.py")
