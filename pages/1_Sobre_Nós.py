import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sobre Nós", layout="wide")

@st.cache_data
def carregar_dados_institucionais():
    # .iloc[0] pega a primeira (e única) linha do CSV como uma Série
    return pd.read_csv('data/institucional.csv').iloc[0]

institucional = carregar_dados_institucionais()

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

