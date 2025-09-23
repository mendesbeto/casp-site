import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from social_utils import display_social_media_links
from auth import get_db_connection, insert_record, get_max_id

display_social_media_links()
st.set_page_config(page_title="Mural de Classificados", layout="wide")

# --- FUNÇÕES DE BANCO DE DADOS ---
@st.cache_data
def carregar_classificados():
    """Carrega os dados de classificados do banco de dados."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query('SELECT * FROM "classificados"', conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar classificados: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def salvar_classificado(user_id, nome_usuario, titulo, descricao, contato, categoria):
    """Salva um novo classificado com status PENDENTE."""
    new_id = get_max_id('classificados', '"CLASSIFICADO_ID"') + 1
    
    novo_classificado = {
        '"CLASSIFICADO_ID"': str(new_id),
        '"USER_ID"': user_id,
        '"NOME_USUARIO"': nome_usuario,
        '"TITULO"': titulo,
        '"DESCRICAO"': descricao,
        '"CONTATO"': contato,
        '"DATA_CRIACAO"': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        '"STATUS"': 'PENDENTE',
        '"CATEGORIA"': categoria,
        '"DESTAQUE"': 'FALSE'
    }
    insert_record('classificados', novo_classificado)
    st.cache_data.clear()

# --- CONFIGURAÇÕES ---
CATEGORIAS_CLASSIFICADOS = ["Venda", "Serviço", "Aluguel", "Doação", "Outros"]
LIMITE_ANUNCIOS_POR_MEMBRO = 3
DIAS_EXPIRACAO_ANUNCIO = 30

st.title("📢 Mural de Classificados")
st.write("Um espaço para membros anunciarem produtos e serviços.")

# --- Formulário para Novo Anúncio ---
if 'member_logged_in' in st.session_state and st.session_state['member_logged_in']:
    user_info = st.session_state['member_info']
    df_classificados_check = carregar_classificados()
    anuncios_do_usuario = df_classificados_check[
        (df_classificados_check['USER_ID'] == user_info['ID']) & 
        (df_classificados_check['STATUS'].isin(['ATIVO', 'PENDENTE']))
    ]
    num_anuncios = len(anuncios_do_usuario)

    if num_anuncios >= LIMITE_ANUNCIOS_POR_MEMBRO:
        st.warning(f"Você atingiu o seu limite de {LIMITE_ANUNCIOS_POR_MEMBRO} anúncios ativos ou pendentes.")
    else:
        with st.expander(f"➕ Publicar um novo anúncio ({num_anuncios}/{LIMITE_ANUNCIOS_POR_MEMBRO} publicados)"):
            with st.form("form_novo_classificado", clear_on_submit=True):
                titulo = st.text_input("Título do Anúncio")
                categoria = st.selectbox("Categoria", CATEGORIAS_CLASSIFICADOS)
                descricao = st.text_area("Descrição do Produto/Serviço")
                contato = st.text_input("Seu Contato (Telefone, Email, etc.)")
                
                if st.form_submit_button("Enviar Anúncio para Moderação"):
                    if all([titulo, descricao, contato, categoria]):
                        salvar_classificado(user_info['ID'], user_info['NOME'], titulo, descricao, contato, categoria)
                        st.success("Seu anúncio foi enviado para moderação. Obrigado!")
                        st.rerun()
                    else:
                        st.warning("Por favor, preencha todos os campos.")
else:
    st.info("Você precisa estar logado para publicar um anúncio. [Faça o login aqui](/Área_do_Membro)")

st.divider()

# --- Barra de Busca e Exibição ---
st.header("Anúncios Ativos")

col1, col2 = st.columns(2)
search_term = col1.text_input("🔎 Buscar por palavra-chave", placeholder="Ex: Bicicleta, Serviço...")
selected_category = col2.selectbox("Filtrar por categoria:", ["Todas"] + CATEGORIAS_CLASSIFICADOS)

df_classificados = carregar_classificados()

df_classificados['DATA_CRIACAO'] = pd.to_datetime(df_classificados['DATA_CRIACAO'])
data_limite = datetime.now() - timedelta(days=DIAS_EXPIRACAO_ANUNCIO)
df_classificados['DESTAQUE'] = df_classificados['DESTAQUE'].fillna(False)
anuncios_validos = df_classificados[
    (df_classificados['STATUS'] == 'ATIVO') &
    (df_classificados['DATA_CRIACAO'] >= data_limite)
].sort_values(by="DATA_CRIACAO", ascending=False)

anuncios_para_exibir = anuncios_validos

if selected_category != "Todas":
    anuncios_para_exibir = anuncios_para_exibir[anuncios_para_exibir['CATEGORIA'] == selected_category]

if search_term:
    anuncios_para_exibir = anuncios_para_exibir[
        anuncios_para_exibir['TITULO'].str.contains(search_term, case=False, na=False) |
        anuncios_para_exibir['DESCRICAO'].str.contains(search_term, case=False, na=False)
    ]

anuncios_destaque = anuncios_para_exibir[anuncios_para_exibir['DESTAQUE'] == 'TRUE']
anuncios_normais = anuncios_para_exibir[anuncios_para_exibir['DESTAQUE'] != 'TRUE']

if anuncios_destaque.empty and anuncios_normais.empty:
    if search_term:
        st.warning("Nenhum anúncio encontrado para sua busca.")
    else:
        st.info("Nenhum anúncio ativo no momento.")
else:
    if not anuncios_destaque.empty:
        st.subheader("🌟 Anúncios em Destaque")
        for _, anuncio in anuncios_destaque.iterrows():
            with st.container(border=True):
                st.subheader(f"🌟 {anuncio['TITULO']}")
                categoria_tag = f"| Categoria: **{anuncio.get('CATEGORIA', 'N/A')}**"
                st.caption(f"Publicado por: {anuncio['NOME_USUARIO']} em {pd.to_datetime(anuncio['DATA_CRIACAO']).strftime('%d/%m/%Y')} {categoria_tag}")
                st.write(anuncio['DESCRICAO'])
                st.success(f"**Contato:** {anuncio['CONTATO']}")
        st.divider()

    for _, anuncio in anuncios_normais.iterrows():
        with st.container(border=True):
            st.subheader(anuncio['TITULO'])
            categoria_tag = f"| Categoria: **{anuncio.get('CATEGORIA', 'N/A')}**"
            st.caption(f"Publicado por: {anuncio['NOME_USUARIO']} em {pd.to_datetime(anuncio['DATA_CRIACAO']).strftime('%d/%m/%Y')} {categoria_tag}")
            st.write(anuncio['DESCRICAO'])
            st.success(f"**Contato:** {anuncio['CONTATO']}")
