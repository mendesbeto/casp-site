import streamlit as st
import pandas as pd

st.set_page_config(page_title="Benefícios", layout="wide")

# Função para carregar os dados dos benefícios
@st.cache_data
def carregar_dados_beneficios():
    # Usamos um try-except para o caso do arquivo ainda não existir
    try:
        return pd.read_csv('data/beneficios.csv')
    except FileNotFoundError:
        # Se o arquivo não for encontrado, retorna um DataFrame vazio para não quebrar a aplicação
        return pd.DataFrame(columns=['TITULO', 'DESCRICAO_BENEFICIO', 'ICONE'])

# Carrega os dados
df_beneficios = carregar_dados_beneficios()

st.title("Vantagens de ser um Associado")
st.write("""
A nossa associação trabalha continuamente para oferecer um leque de benefícios que impactam positivamente a vida dos nossos membros. 
O nosso foco principal é garantir economia através de uma rede de convênios robusta, mas as vantagens não param por aí.
""")

st.divider()

# Verifica se há benefícios para exibir
if not df_beneficios.empty:
    # Itera sobre cada benefício e o exibe
    for index, beneficio in df_beneficios.iterrows():
        st.header(f"{beneficio['ICONE']} {beneficio['TITULO']}")
        st.write(beneficio['DESCRICAO_BENEFICIO'])
        st.write("---")
else:
    st.warning("Ainda não há benefícios cadastrados. Volte em breve!")

# --- Call to Action (CTA) ---
st.header("Pronto para Economizar?")
st.write("Nossos convênios são a porta de entrada para um mundo de descontos. Veja a lista completa de parceiros e comece a aproveitar agora mesmo.")

if st.button("Ver Todos os Convênios", type="primary", use_container_width=True):
    st.switch_page("pages/2_Convênios.py")