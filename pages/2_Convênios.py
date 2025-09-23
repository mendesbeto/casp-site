import streamlit as st
import pandas as pd
import numpy as np
from social_utils import display_social_media_links
from auth import get_db_connection, insert_record, update_record, get_max_id

display_social_media_links()
st.set_page_config(page_title="Nossos Convênios", layout="wide")

# --- FUNÇÕES DE BANCO DE DADOS ---
@st.cache_data
def carregar_dados_db(table_name):
    """Carrega uma tabela inteira do banco de dados para um DataFrame."""
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

def salvar_rating(convenio_id, user_id, rating):
    """Salva ou atualiza a avaliação de um usuário para um convênio."""
    df_ratings = carregar_dados_db('convenio_ratings')

    existing_rating = df_ratings[(df_ratings['user_id'] == user_id) & (df_ratings['convenio_id'] == convenio_id)]

    if not existing_rating.empty:
        rating_id = existing_rating.iloc[0]['rating_id']
        update_record('convenio_ratings', {'rating': rating}, {'rating_id': rating_id})
    else:
        new_id = get_max_id('convenio_ratings', 'rating_id') + 1
        new_rating = {
            'rating_id': int(new_id),
            'convenio_id': convenio_id,
            'user_id': user_id,
            'rating': rating
        }
        insert_record('convenio_ratings', new_rating)
    
    st.cache_data.clear()

# --- CARREGAMENTO INICIAL DOS DADOS ---
df_convenios = carregar_dados_db('convenios')
df_parceiros = carregar_dados_db('parceiros')
df_ratings = carregar_dados_db('convenio_ratings')

st.title("Rede de Convênios")
st.write("Explore os benefícios exclusivos para nossos associados.")

# --- LÓGICA DE EXIBIÇÃO ---
if 'convenio_selecionado' not in st.session_state:
    st.session_state.convenio_selecionado = None

if st.session_state.convenio_selecionado:
    convenio = st.session_state.convenio_selecionado
    
    if st.button("⬅️ Voltar para a lista"):
        st.session_state.convenio_selecionado = None
        st.rerun()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(convenio['imagem_url'], use_container_width=True)

    with col2:
        st.image(convenio['icon_url'], width=60)
        st.write(convenio['descricao'])

        ratings_deste_convenio = df_ratings[df_ratings['convenio_id'] == convenio['convenio_id']]
        avg_rating = ratings_deste_convenio['rating'].mean()
        rating_count = len(ratings_deste_convenio)

        st.write("---")
        if pd.isna(avg_rating):
            st.write("⭐ Ainda não avaliado")
        else:
            estrelas = "★" * int(round(avg_rating, 0)) + "☆" * (5 - int(round(avg_rating, 0)))
            st.markdown(f"### <span style='color: #ffc107;'>{estrelas}</span> ({avg_rating:.1f} de 5)", unsafe_allow_html=True)
            st.caption(f"{rating_count} avaliação(ões)")

        if 'member_logged_in' in st.session_state and st.session_state['member_logged_in']:
            user_id = st.session_state['member_info']['id']
            user_rating_df = ratings_deste_convenio[ratings_deste_convenio['user_id'] == user_id]
            user_rating = int(user_rating_df['rating'].iloc[0]) if not user_rating_df.empty else 0

            with st.form(key=f"form_rating_{convenio['convenio_id']}"):
                st.write("**Sua avaliação:**")
                nova_avaliacao = st.selectbox("Escolha sua nota:", [1, 2, 3, 4, 5], index=user_rating - 1 if user_rating > 0 else 2, label_visibility="collapsed")
                if st.form_submit_button("Avaliar"):
                    salvar_rating(convenio['convenio_id'], user_id, nova_avaliacao)
                    st.success("Obrigado pela sua avaliação!")
                    st.rerun()
        else:
            st.info("Faça login para avaliar este convênio.")

        st.divider()
        st.subheader("Parceiros Associados")
        parceiros_do_convenio = df_parceiros[df_parceiros['convenio_id'] == convenio['convenio_id']]

        if parceiros_do_convenio.empty:
            st.info("Nenhum parceiro específico cadastrado para este convênio ainda.")
        else:
            for _, parceiro in parceiros_do_convenio.iterrows():
                with st.container(border=True):
                    st.write(f"**{parceiro['nome_parceiro']}**")
                    st.write(f"_{parceiro['detalhes']}_")
                    if pd.notna(parceiro['endereco']): st.write(f"📍 {parceiro['endereco']}")
                    if pd.notna(parceiro['telefone']): st.write(f"📞 {parceiro['telefone']}")
                    if pd.notna(parceiro['website']): st.markdown(f"🌐 [{parceiro['website']}]({parceiro['website']})")
else:
    search_term = st.text_input("🔎 Buscar por nome ou tipo de serviço", placeholder="Ex: Saúde, Educação, Academia...")
    st.write("Clique em 'Ver Mais' para detalhes de cada convênio.")
    
    convenios_ativos = df_convenios[df_convenios['status'] == 'ATIVO']

    if search_term:
        convenios_filtrados = convenios_ativos[
            convenios_ativos['nome_convenio'].str.contains(search_term, case=False, na=False) |
            convenios_ativos['tipo_servico'].str.contains(search_term, case=False, na=False)
        ]
    else:
        convenios_filtrados = convenios_ativos

    num_colunas = 3
    cols = st.columns(num_colunas)

    if convenios_filtrados.empty:
        st.warning("Nenhum convênio encontrado para sua busca.")
    else:
        for i, convenio in enumerate(convenios_filtrados.itertuples()):
            col_index = i % num_colunas
            with cols[col_index]:
                with st.container(border=True):
                    st.subheader(convenio.nome_convenio)
                    st.image(convenio.icon_url, width=50)
                    
                    if st.button("Ver Mais", key=f"btn_{convenio.convenio_id}"):
                        st.session_state.convenio_selecionado = df_convenios.loc[df_convenios['convenio_id'] == convenio.convenio_id].to_dict('records')[0]
                        st.rerun()