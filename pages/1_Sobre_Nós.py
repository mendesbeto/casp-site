import streamlit as st
import pandas as pd
from social_utils import display_social_media_links
from auth import get_db_connection

display_social_media_links()
st.set_page_config(page_title="Sobre Nós", layout="wide")

@st.cache_data
def carregar_dados_institucionais():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM institucional LIMIT 1", conn)
        df.columns = [x.lower() for x in df.columns]
        return df.iloc[0]
    except Exception as e:
        st.error(f"Erro ao carregar dados institucionais: {e}")
        return None
    finally:
        if conn:
            conn.close()

institucional = carregar_dados_institucionais()

if institucional is not None:
    st.title("Sobre a Nossa Associação")
    st.image(institucional['logo_url'], width=200)

    st.header("Nossa História")
    st.write(institucional['historico'])

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Missão")
        st.info(institucional['missao'])

    with col2:
        st.subheader("Visão")
        st.warning(institucional['visao'])

    with col3:
        st.subheader("Valores")
        st.success(institucional['valores'])
else:
    st.error("Não foi possível carregar as informações do site.")