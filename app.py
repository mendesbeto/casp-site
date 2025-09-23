import streamlit as st
import pandas as pd
from streamlit_carousel import carousel
from social_utils import display_social_media_links
from auth import get_db_connection

display_social_media_links()

st.set_page_config(
    page_title="CASP",
    page_icon="🤝",
    layout="wide"
)

with st.sidebar:
    st.image("assets/logo.png", width=150)

@st.cache_data
def carregar_dados_db(table_name):
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df.columns = [x.lower() for x in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela {table_name}: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

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

df_convenios = carregar_dados_db('convenios')
df_noticias = carregar_dados_db('noticias')
institucional = carregar_dados_institucionais()

if institucional is not None:
    col_titulo, col_login = st.columns([3, 1])
    with col_titulo:
        st.image(institucional['logo_url'], width=200)
    with col_login:
        st.page_link("pages/8_Área_do_Membro.py", label="Login do Associado", icon="👤")
    
    with st.container():
        st.subheader("Bem-vindo ao nosso portal de benefícios!")
        st.write("""
        Aqui você encontra uma rede de parceiros e convênios pensada para trazer mais economia e qualidade de vida para você e sua família.
        Explore nosso site e descubra todas as vantagens de ser um associado.
        """)
        st.page_link("pages/1_Sobre_Nós.py", label="Saiba mais sobre nós", icon="➡️")

    st.divider()

    with st.container():
        st.header("Conheça a  Nossa Associação")
        video_url = "https://youtube.com/embed/tOXmIrJe1_g?feature=share"
        if video_url:
            st.video(video_url)
        else:
            st.info("Vídeo institucional em breve.")

    with st.container():
        st.header("Nossos Convênios em Destaque")
        convenios_destaque = df_convenios[df_convenios['destaque'] == 1]
        carousel_items = [
            dict(img=row.imagem_url, title=row.nome_convenio, text=row.nome_convenio)
            for row in convenios_destaque.itertuples()
        ]
        if carousel_items:
            carousel(items=carousel_items)
        else:
            st.info("Não há convênios em destaque no momento.")

    st.divider()

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header("Principais Benefícios")
            st.info("Conheça nossa ampla rede de convênios e economize!")
            st.write("- Descontos em saúde e bem-estar.")
            st.write("- Vantagens em educação e lazer.")
            st.write("- Parcerias com comércios locais.")

            b1, b2 = st.columns(2)
            with b1:
                if st.button("Associe-se Agora", type="primary", use_container_width=True):
                    st.switch_page("pages/6_Associe-se.py")
            with b2:
                if st.button("Ver Todos os Convênios", use_container_width=True):
                    st.switch_page("pages/2_Convênios.py")

        with col2:
            st.header("Últimas Notícias")
            noticia_destaque = df_noticias[df_noticias['destaque'] == 1].sort_values(by="data", ascending=False).iloc[0]

            st.subheader(noticia_destaque['titulo'])
            if pd.notna(noticia_destaque['imagem_url']):
                st.image(noticia_destaque['imagem_url'])
            st.markdown(noticia_destaque['conteudo'], unsafe_allow_html=True)
            st.page_link("pages/3_Notícias.py", label="Ver todas as notícias", icon="📰")
else:
    st.error("Não foi possível carregar as informações do site.")