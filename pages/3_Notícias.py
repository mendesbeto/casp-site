import streamlit as st
import pandas as pd
import math
import os
from datetime import datetime

st.set_page_config(page_title="Notícias", layout="wide")

@st.cache_data
def carregar_dados_noticias():
    return pd.read_csv('data/noticias.csv')

@st.cache_data
def carregar_dados_galeria():
    filepath = 'data/galeria_fotos.csv'
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return pd.DataFrame(columns=['FOTO_ID', 'NOTICIA_ID', 'IMAGEM_URL', 'LEGENDA'])
    return pd.read_csv(filepath)

@st.cache_data
def carregar_dados_comentarios():
    filepath = 'data/comentarios.csv'
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return pd.DataFrame(columns=['COMENTARIO_ID', 'NOTICIA_ID', 'USER_ID', 'NOME_USUARIO', 'COMENTARIO', 'TIMESTAMP', 'STATUS'])
    return pd.read_csv(filepath)

@st.cache_data
def carregar_dados_likes():
    """Carrega os dados de curtidas do CSV."""
    filepath = 'data/noticia_likes.csv'
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return pd.DataFrame(columns=['LIKE_ID', 'NOTICIA_ID', 'USER_ID'])
    return pd.read_csv(filepath)

@st.cache_data
def carregar_tag_follows():
    """Carrega os dados de tags seguidas."""
    filepath = 'data/tag_follows.csv'
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return pd.DataFrame(columns=['FOLLOW_ID', 'USER_ID', 'TAG_NAME'])
    return pd.read_csv(filepath)

def salvar_tag_follows(user_id, tags_a_seguir):
    """Salva as preferências de tags de um usuário."""
    # Esta função será implementada no passo 5
    pass

def salvar_like(noticia_id, user_id):
    """Salva um novo like no CSV, lendo os dados mais recentes."""
    filepath = 'data/noticia_likes.csv'
    try:
        df_likes = pd.read_csv(filepath)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df_likes = pd.DataFrame(columns=['LIKE_ID', 'NOTICIA_ID', 'USER_ID'])

    new_id = 1
    if not df_likes.empty:
        new_id = df_likes['LIKE_ID'].max() + 1

    novo_like = pd.DataFrame([{'LIKE_ID': new_id, 'NOTICIA_ID': noticia_id, 'USER_ID': user_id}])
    df_final = pd.concat([df_likes, novo_like], ignore_index=True)
    df_final.to_csv(filepath, index=False)
    st.cache_data.clear()

def remover_like(noticia_id, user_id):
    """Remove um like do CSV, lendo os dados mais recentes."""
    filepath = 'data/noticia_likes.csv'
    df_likes = pd.read_csv(filepath)
    index_to_remove = df_likes[(df_likes['NOTICIA_ID'] == noticia_id) & (df_likes['USER_ID'] == user_id)].index
    df_likes.drop(index_to_remove, inplace=True)
    df_likes.to_csv(filepath, index=False)
    st.cache_data.clear()

def salvar_tag_follows(user_id, tags_a_seguir):
    """Salva as preferências de tags de um usuário, substituindo as antigas."""
    filepath = 'data/tag_follows.csv'
    try:
        df_follows = pd.read_csv(filepath)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df_follows = pd.DataFrame(columns=['FOLLOW_ID', 'USER_ID', 'TAG_NAME'])

    # Remove os follows antigos do usuário
    df_follows = df_follows[df_follows['USER_ID'] != user_id]

    # Adiciona os novos follows
    novos_follows_df = pd.DataFrame({
        'USER_ID': [user_id] * len(tags_a_seguir),
        'TAG_NAME': tags_a_seguir
    })
    df_final = pd.concat([df_follows, novos_follows_df], ignore_index=True)
    df_final.reset_index(drop=True, inplace=True)
    df_final['FOLLOW_ID'] = df_final.index + 1
    df_final.to_csv(filepath, index=False)
    st.cache_data.clear()

def salvar_comentario(noticia_id, user_id, nome_usuario, comentario):
    """Salva um novo comentário no CSV com status PENDENTE."""
    filepath = 'data/comentarios.csv'
    df_comentarios = carregar_dados_comentarios()

    new_id = 1
    if not df_comentarios.empty:
        new_id = df_comentarios['COMENTARIO_ID'].max() + 1

    novo_comentario = pd.DataFrame([{
        'COMENTARIO_ID': new_id,
        'NOTICIA_ID': noticia_id,
        'USER_ID': user_id,
        'NOME_USUARIO': nome_usuario,
        'COMENTARIO': comentario,
        'TIMESTAMP': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'STATUS': 'PENDENTE'
    }])
    novo_comentario.to_csv(filepath, mode='a', header=df_comentarios.empty, index=False)

df_noticias = carregar_dados_noticias()
df_galeria = carregar_dados_galeria()
df_comentarios = carregar_dados_comentarios()
df_likes = carregar_dados_likes()

st.title("Mural de Notícias")

noticias_publicadas = df_noticias[df_noticias['STATUS'] == 'PUBLICADO'].sort_values(by="DATA", ascending=False)

# --- LÓGICA DE FILTRAGEM POR TAG ---
all_tags = set()
if 'TAGS' in noticias_publicadas.columns:
    # Drop NaNs, split by comma, flatten the list of lists, strip whitespace, and get unique tags
    tags_series = noticias_publicadas['TAGS'].dropna().str.split(',')
    all_tags = sorted(list(set([tag.strip() for sublist in tags_series for tag in sublist if tag.strip()])))

# Widget de filtro
if all_tags:
    selected_tags = st.multiselect("Filtrar por tags:", options=all_tags)
else:
    selected_tags = []

if 'member_logged_in' in st.session_state and st.session_state['member_logged_in']:
    st.divider()
    with st.expander("🔔 Gerenciar notificações por tag"):
        user_id = st.session_state['member_info']['ID']
        df_follows = carregar_tag_follows()
        tags_seguidas = df_follows[df_follows['USER_ID'] == user_id]['TAG_NAME'].tolist()

        novas_tags_seguidas = st.multiselect(
            "Selecione as tags que você deseja seguir para receber novidades:",
            options=all_tags,
            default=tags_seguidas
        )

        if st.button("Salvar minhas preferências"):
            salvar_tag_follows(user_id, novas_tags_seguidas)
            st.success("Preferências salvas!")
            st.rerun()

# Filtrar notícias se alguma tag for selecionada
if selected_tags:
    def has_tags(row_tags):
        if pd.isna(row_tags):
            return False
        return any(tag in [t.strip() for t in row_tags.split(',')] for tag in selected_tags)

    noticias_filtradas = noticias_publicadas[noticias_publicadas['TAGS'].apply(has_tags)]
else:
    noticias_filtradas = noticias_publicadas

if not noticias_publicadas.empty:
    # --- LÓGICA DE PAGINAÇÃO ---
    if 'page_num' not in st.session_state:
        st.session_state.page_num = 1

    ITENS_POR_PAGINA = 5
    total_noticias = len(noticias_filtradas)
    total_paginas = math.ceil(total_noticias / ITENS_POR_PAGINA)

    # Garante que o número da página seja válido
    if st.session_state.page_num > total_paginas:
        st.session_state.page_num = total_paginas
    if st.session_state.page_num < 1:
        st.session_state.page_num = 1

    start_idx = (st.session_state.page_num - 1) * ITENS_POR_PAGINA
    end_idx = start_idx + ITENS_POR_PAGINA
    noticias_para_exibir = noticias_filtradas.iloc[start_idx:end_idx]

    # --- EXIBIÇÃO DAS NOTÍCIAS ---
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
            
            # Exibe as tags do artigo
            if 'TAGS' in noticia and pd.notna(noticia.TAGS):
                tags = [tag.strip() for tag in noticia.TAGS.split(',') if tag.strip()]
                st.write(" ".join([f"`#{tag}`" for tag in tags]))

            # --- SEÇÃO DE LIKES ---
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
            
            # --- EXIBIÇÃO DA GALERIA ---
            fotos_da_noticia = df_galeria[df_galeria['NOTICIA_ID'] == noticia.ID]
            if not fotos_da_noticia.empty:
                st.divider()
                st.subheader("Galeria de Fotos")
                
                # Define o número de colunas para a galeria
                num_colunas_galeria = 4
                cols_galeria = st.columns(num_colunas_galeria)
                for i, foto in enumerate(fotos_da_noticia.itertuples()):
                    cols_galeria[i % num_colunas_galeria].image(foto.IMAGEM_URL, caption=foto.LEGENDA, use_container_width=True)

            # --- SEÇÃO DE COMENTÁRIOS ---
            st.divider()
            st.subheader("Comentários")

            comentarios_aprovados = df_comentarios[(df_comentarios['NOTICIA_ID'] == noticia.ID) & (df_comentarios['STATUS'] == 'APROVADO')]
            if comentarios_aprovados.empty:
                st.write("_Seja o primeiro a comentar!_")
            else:
                for _, comentario in comentarios_aprovados.iterrows():
                    st.write(f"**{comentario['NOME_USUARIO']}** em {pd.to_datetime(comentario['TIMESTAMP']).strftime('%d/%m/%Y')}:")
                    st.info(f"{comentario['COMENTARIO']}")

            # Formulário para novo comentário (apenas para usuários logados)
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

        st.write("") # Adiciona um espaço vertical

    # --- CONTROLES DE PAGINAÇÃO ---
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