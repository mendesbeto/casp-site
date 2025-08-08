import streamlit as st
import pandas as pd
from streamlit_carousel import carousel

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="CASP",
    page_icon="🤝",
    layout="wide"
)

# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---
# O decorator @st.cache_data otimiza o carregamento, guardando os dados em memória.
@st.cache_data
def carregar_dados_convenios():
    return pd.read_csv('data/convenios.csv')

@st.cache_data
def carregar_dados_noticias():
    return pd.read_csv('data/noticias.csv')

@st.cache_data
def carregar_dados_institucionais():
    return pd.read_csv('data/institucional.csv').iloc[0]

# --- CARREGAMENTO DOS DADOS ---
df_convenios = carregar_dados_convenios()
df_noticias = carregar_dados_noticias()
institucional = carregar_dados_institucionais()

# --- BARRA LATERAL COM LOGO ---
with st.sidebar:
    st.logo("assets/logo.png")

# --- PÁGINA INICIAL ---

# --- SEÇÃO DE BOAS-VINDAS ---
col_titulo, col_login = st.columns([3, 1])
with col_titulo:
    st.title(institucional['TITULO_SITE'])
with col_login:
    st.page_link("pages/8_Área_do_Membro.py", label="Login do Associado", icon="👤")

with st.container():
    st.subheader("Bem-vindo ao nosso portal de benefícios!")
    st.write("""
    Aqui você encontra uma rede de parceiros e convênios pensada para trazer mais economia e qualidade de vida para você e sua família.
    Explore nosso site e descubra todas as vantagens de ser um associado.
    """)
    # O Streamlit não tem um "redirect" simples. Usamos o link para a página.
    st.page_link("pages/1_Sobre_Nós.py", label="Saiba mais sobre nós", icon="➡️")

st.divider()

# --- VÍDEO INSTITUCIONAL ---
with st.container():
    st.header("Conheça a  Nossa Associação")
    # Substitua pelo link do seu vídeo no YouTube ou Vimeo
    video_url = "https://youtube.com/embed/tOXmIrJe1_g?feature=share"
    if video_url:
        st.video(video_url)
    else:
        st.info("Vídeo institucional em breve.")

# --- SEÇÃO BANNER/CARROSSEL DE CONVÊNIOS EM DESTAQUE ---
with st.container():
    st.header("Nossos Convênios em Destaque")

    # Filtra apenas os convênios com DESTAQUE = TRUE
    convenios_destaque = df_convenios[df_convenios['DESTAQUE'] == True]

    # Prepara as imagens para o carrossel no formato correto (lista de dicionários)
    carousel_items = [
        dict(img=row.IMAGEM_URL, title=row.NOME_CONVENIO, text=row.NOME_CONVENIO)
        for row in convenios_destaque.itertuples()
    ]

    # Exibe o carrossel se houver itens
    if carousel_items:
        carousel(items=carousel_items)
    else:
        st.info("Não há convênios em destaque no momento.")

st.divider()

# --- SEÇÃO DE CHAMADA PARA AÇÃO (CTA) E NOTÍCIAS ---
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.header("Principais Benefícios")
        st.info("Conheça nossa ampla rede de convênios e economize!")
        st.write("- Descontos em saúde e bem-estar.")
        st.write("- Vantagens em educação e lazer.")
        st.write("- Parcerias com comércios locais.")

        # Botões de ação
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Associe-se Agora", type="primary", use_container_width=True):
                # Futuramente, isso levará para uma página de cadastro
                st.switch_page("pages/6_Associe-se.py")
        with b2:
            if st.button("Ver Todos os Convênios", use_container_width=True):
                st.switch_page("pages/2_Convênios.py")

    with col2:
        st.header("Últimas Notícias")
        # Filtra apenas notícias com DESTAQUE = TRUE e pega a mais recente
        noticia_destaque = df_noticias[df_noticias['DESTAQUE'] == True].sort_values(by="DATA", ascending=False).iloc[0]

        st.subheader(noticia_destaque['TITULO'])
        if pd.notna(noticia_destaque['IMAGEM_URL']):
            st.image(noticia_destaque['IMAGEM_URL'])
        st.write(noticia_destaque['CONTEUDO'])
        st.page_link("pages/3_Notícias.py", label="Ver todas as notícias", icon="📰")