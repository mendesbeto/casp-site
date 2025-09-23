import streamlit as st
import pandas as pd
import math
from datetime import datetime
from social_utils import display_social_media_links
from auth import get_db_connection, insert_record, delete_record, get_max_id

display_social_media_links()
st.set_page_config(page_title="Notícias", layout="wide")

# --- FUNÇÕES DE BANCO DE DADOS ---
@st.cache_data
def carregar_dados_db(table_name):
    """Carrega uma tabela inteira do banco de dados para um DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela {table_name}: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def salvar_like(noticia_id, user_id):
    """Salva um novo like no banco de dados."""
    new_id = get_max_id('noticia_likes', '"LIKE_ID"') + 1
    new_like = {
        '"LIKE_ID"': int(new_id),
        '"NOTICIA_ID"': noticia_id,
        '"USER_ID"': user_id
    }
    insert_record('noticia_likes', new_like)
    st.cache_data.clear()

def remover_like(noticia_id, user_id):
    """Remove um like do banco de dados."""
    delete_record('noticia_likes', {'"NOTICIA_ID"': noticia_id, '"USER_ID"': user_id})
    st.cache_data.clear()

def salvar_tag_follows(user_id, tags_a_seguir):
    """Salva as preferências de tags de um usuário, substituindo as antigas."""
    delete_record('tag_follows', {'"USER_ID"': user_id})
    for tag in tags_a_seguir:
        new_id = get_max_id('tag_follows', '"FOLLOW_ID"') + 1
        new_follow = {
            '"FOLLOW_ID"': int(new_id),
            '"USER_ID"': user_id,
            '"TAG_NAME"': tag
        }
        insert_record('tag_follows', new_follow)
    st.cache_data.clear()

def salvar_comentario(noticia_id, user_id, nome_usuario, comentario):
    """Salva um novo comentário no banco de dados com status PENDENTE."""
    new_id = get_max_id('comentarios', '"COMENTARIO_ID"') + 1
    novo_comentario = {
        '"COMENTARIO_ID"': int(new_id),
        '"NOTICIA_ID"': noticia_id,
        '"USER_ID"': user_id,
        '"NOME_USUARIO"': nome_usuario,
        '"COMENTARIO"': comentario,
        '"TIMESTAMP"': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        '"STATUS"': 'PENDENTE'
    }
    insert_record('comentarios', novo_comentario)

# --- CARREGAMENTO DOS DADOS ---
df_noticias = carregar_dados_db('noticias')
df_galeria = carregar_dados_db('galeria_fotos')
df_comentarios = carregar_dados_db('comentarios')
df_likes = carregar_dados_db('noticia_likes')
df_tag_follows = carregar_dados_db('tag_follows')

st.title("Mural de Notícias")

noticias_publicadas = df_noticias[df_noticias['STATUS'] == 'PUBLICADO'].sort_values(by="DATA", ascending=False)

# --- LÓGICA DE FILTRAGEM POR TAG ---
all_tags = set()
if 'TAGS' in noticias_publicadas.columns:
    tags_series = noticias_publicadas['TAGS'].dropna().str.split(',')
    all_tags = sorted(list(set([tag.strip() for sublist in tags_series for tag in sublist if tag.strip()])))

if all_tags:
    selected_tags = st.multiselect("Filtrar por tags:", options=all_tags)
else:
    selected_tags = []

if 'member_logged_in' in st.session_state and st.session_state['member_logged_in']:
    st.divider()
    with st.expander("🔔 Gerenciar notificações por tag"):
        user_id = st.session_state['member_info']['ID']
        tags_seguidas = df_tag_follows[df_tag_follows['USER_ID'] == user_id]['TAG_NAME'].tolist()

        novas_tags_seguidas = st.multiselect(
            "Selecione as tags que você deseja seguir para receber novidades:",
            options=all_tags,
            default=tags_seguidas
        )

        if st.button("Salvar minhas preferências"):
            salvar_tag_follows(user_id, novas_tags_seguidas)
            st.success("Preferências salvas!")
            st.rerun()

if selected_tags:
    def has_tags(row_tags):
        if pd.isna(row_tags):
            return False
        return any(tag in [t.strip() for t in row_tags.split(',')] for tag in selected_tags)

    noticias_filtradas = noticias_publicadas[noticias_publicadas['TAGS'].apply(has_tags)]
else:
    noticias_filtradas = noticias_publicadas

if not noticias_publicadas.empty:
    if 'page_num' not in st.session_state:
        st.session_state.page_num = 1

    ITENS_POR_PAGINA = 5
    total_noticias = len(noticias_filtradas)
    total_paginas = math.ceil(total_noticias / ITENS_POR_PAGINA)

    if st.session_state.page_num > total_paginas:
        st.session_state.page_num = total_paginas
    if st.session_state.page_num < 1:
        st.session_state.page_num = 1

    start_idx = (st.session_state.page_num - 1) * ITENS_POR_PAGINA
    end_idx = start_idx + ITENS_POR_PAGINA
    noticias_para_exibir = noticias_filtradas.iloc[start_idx:end_idx]

    for noticia in noticias_para_exibir.itertuples():
        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                if pd.notna(noticia.IMAGEM_URL):
                    st.image(noticia.IMAGEM_URL)
            
            with col2:
                st.subheader(noticia.TITULO)
                st.caption(f"Publicado em: {pd.to_datetime(noticia.DATA).strftime('%d/%m/%Y')}")
                st.markdown(noticia.CONTEUDO, unsafe_allow_html=True)
            
            if hasattr(noticia, 'TAGS') and pd.notna(noticia.TAGS):
                tags = [tag.strip() for tag in noticia.TAGS.split(',') if tag.strip()]
                st.write(" ".join([f"`#{tag}`" for tag in tags]))

            likes_desta_noticia = df_likes[df_likes['NOTICIA_ID'] == noticia.ID]
            like_count = len(likes_desta_noticia)

            col_like1, col_like2 = st.columns([0.2, 0.8])
            with col_like1:
                if 'member_logged_in' in st.session_state and st.session_state['member_logged_in']:
                    user_id = st.session_state['member_info']['ID']
                    ja_curtiu = not likes_desta_noticia[likes_desta_noticia['USER_ID'] == user_id].empty

                    if ja_curtiu:
                        if st.button("❤️ Curtido", key=f"unlike_{noticia.ID}", use_container_width=True, type="primary"):
                            remover_like(noticia.ID, user_id)
                            st.rerun()
                    else:
                        if st.button("🤍 Curtir", key=f"like_{noticia.ID}", use_container_width=True):
                            salvar_like(noticia.ID, user_id)
                            st.rerun()
                else:
                    st.button("🤍 Curtir", key=f"like_disabled_{noticia.ID}", use_container_width=True, disabled=True, help="Faça login para curtir")
            with col_like2:
                st.markdown(f"&nbsp; **{like_count}** curtida(s)")
            
            fotos_da_noticia = df_galeria[df_galeria['NOTICIA_ID'] == noticia.ID]
            if not fotos_da_noticia.empty:
                st.divider()
                st.subheader("Galeria de Fotos")
                
                num_colunas_galeria = 4
                cols_galeria = st.columns(num_colunas_galeria)
                for i, foto in enumerate(fotos_da_noticia.itertuples()):
                    cols_galeria[i % num_colunas_galeria].image(foto.IMAGEM_URL, caption=foto.LEGENDA, use_container_width=True)

            st.divider()
            st.subheader("Comentários")

            comentarios_aprovados = df_comentarios[(df_comentarios['NOTICIA_ID'] == noticia.ID) & (df_comentarios['STATUS'] == 'APROVADO')]
            if comentarios_aprovados.empty:
                st.write("_Seja o primeiro a comentar!_")
            else:
                for _, comentario in comentarios_aprovados.iterrows():
                    st.write(f"**{comentario['NOME_USUARIO']}** em {pd.to_datetime(comentario['TIMESTAMP']).strftime('%d/%m/%Y')}:")
                    st.info(f"{comentario['COMENTARIO']}")

            if 'member_logged_in' in st.session_state and st.session_state['member_logged_in']:
                with st.form(key=f"form_comentario_{noticia.ID}", clear_on_submit=True):
                    novo_comentario_texto = st.text_area("Deixe seu comentário:", height=100, label_visibility="collapsed", placeholder="Deixe seu comentário...")
                    submitted = st.form_submit_button("Enviar Comentário")
                    if submitted and novo_comentario_texto:
                        user_info = st.session_state['member_info']
                        salvar_comentario(noticia.ID, user_info['ID'], user_info['NOME'], novo_comentario_texto)
                        st.success("Seu comentário foi enviado para moderação. Obrigado!")
            else:
                st.info("Você precisa estar logado para comentar. [Faça o login aqui](/Área_do_Membro)")

        st.write("")

    if total_paginas > 1:
        st.divider()
        col1, col2, col3 = st.columns([2, 1, 2])

        if col1.button("⬅️ Anterior", disabled=(st.session_state.page_num <= 1)):
            st.session_state.page_num -= 1
            st.rerun()

        col2.write(f"Página {st.session_state.page_num} de {total_paginas}")

        if col3.button("Próxima ➡️", disabled=(st.session_state.page_num >= total_paginas)):
            st.session_state.page_num += 1
            st.rerun()
else:
    st.info("Nenhuma notícia publicada no momento.")