
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
        return df.iloc[0]
    except Exception as e:
        st.error(f"Erro ao carregar dados institucionais: {e}")
        return None
    finally:
        conn.close()

institucional = carregar_dados_institucionais()

if institucional is not None:
    st.title("Sobre a Nossa Associação")
    st.image(institucional['LOGO_URL'], width=200)

    st.header("Nossa História")
    st.write(institucional['HISTORICO'])

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Missão")
        st.info(institucional['MISSAO'])

    with col2:
        st.subheader("Visão")
        st.warning(institucional['VISAO'])

    with col3:
        st.subheader("Valores")
        st.success(institucional['VALORES'])
else:
    st.error("Não foi possível carregar as informações do site.")
