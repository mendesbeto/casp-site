
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
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela {table_name}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def salvar_rating(convenio_id, user_id, rating):
    """Salva ou atualiza a avaliação de um usuário para um convênio."""
    df_ratings = carregar_dados_db('convenio_ratings')

    existing_rating = df_ratings[(df_ratings['USER_ID'] == user_id) & (df_ratings['CONVENIO_ID'] == convenio_id)]

    if not existing_rating.empty:
        rating_id = existing_rating.iloc[0]['RATING_ID']
        update_record('convenio_ratings', {'RATING': rating}, {'RATING_ID': rating_id})
    else:
        new_id = get_max_id('convenio_ratings', 'RATING_ID') + 1
        new_rating = {
            'RATING_ID': int(new_id),
            'CONVENIO_ID': convenio_id,
            'USER_ID': user_id,
            'RATING': rating
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
        st.image(convenio['IMAGEM_URL'], use_container_width=True)

    with col2:
        st.image(convenio['ICON_URL'], width=60)
        st.write(convenio['DESCRICAO'])

        ratings_deste_convenio = df_ratings[df_ratings['CONVENIO_ID'] == convenio['CONVENIO_ID']]
        avg_rating = ratings_deste_convenio['RATING'].mean()
        rating_count = len(ratings_deste_convenio)

        st.write("---")
        if pd.isna(avg_rating):
            st.write("⭐ Ainda não avaliado")
        else:
            estrelas = "★" * int(round(avg_rating, 0)) + "☆" * (5 - int(round(avg_rating, 0)))
            st.markdown(f"### <span style='color: #ffc107;'>{estrelas}</span> ({avg_rating:.1f} de 5)", unsafe_allow_html=True)
            st.caption(f"{rating_count} avaliação(ões)")

        if 'member_logged_in' in st.session_state and st.session_state['member_logged_in']:
            user_id = st.session_state['member_info']['ID']
            user_rating_df = ratings_deste_convenio[ratings_deste_convenio['USER_ID'] == user_id]
            user_rating = int(user_rating_df['RATING'].iloc[0]) if not user_rating_df.empty else 0

            with st.form(key=f"form_rating_{convenio['CONVENIO_ID']}"):
                st.write("**Sua avaliação:**")
                nova_avaliacao = st.selectbox("Escolha sua nota:", [1, 2, 3, 4, 5], index=user_rating - 1 if user_rating > 0 else 2, label_visibility="collapsed")
                if st.form_submit_button("Avaliar"):
                    salvar_rating(convenio['CONVENIO_ID'], user_id, nova_avaliacao)
                    st.success("Obrigado pela sua avaliação!")
                    st.rerun()
        else:
            st.info("Faça login para avaliar este convênio.")

        st.divider()
        st.subheader("Parceiros Associados")
        parceiros_do_convenio = df_parceiros[df_parceiros['CONVENIO_ID'] == convenio['CONVENIO_ID']]

        if parceiros_do_convenio.empty:
            st.info("Nenhum parceiro específico cadastrado para este convênio ainda.")
        else:
            for _, parceiro in parceiros_do_convenio.iterrows():
                with st.container(border=True):
                    st.write(f"**{parceiro['NOME_PARCEIRO']}**")
                    st.write(f"_{parceiro['DETALHES']}_")
                    if pd.notna(parceiro['ENDERECO']): st.write(f"📍 {parceiro['ENDERECO']}")
                    if pd.notna(parceiro['TELEFONE']): st.write(f"📞 {parceiro['TELEFONE']}")
                    if pd.notna(parceiro['WEBSITE']): st.markdown(f"🌐 [{parceiro['WEBSITE']}]({parceiro['WEBSITE']})")
else:
    search_term = st.text_input("🔎 Buscar por nome ou tipo de serviço", placeholder="Ex: Saúde, Educação, Academia...")
    st.write("Clique em 'Ver Mais' para detalhes de cada convênio.")
    
    convenios_ativos = df_convenios[df_convenios['STATUS'] == 'ATIVO']

    if search_term:
        convenios_filtrados = convenios_ativos[
            convenios_ativos['NOME_CONVENIO'].str.contains(search_term, case=False, na=False) |
            convenios_ativos['TIPO_SERVICO'].str.contains(search_term, case=False, na=False)
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
                    st.subheader(convenio.NOME_CONVENIO)
                    st.image(convenio.ICON_URL, width=50)
                    
                    if st.button("Ver Mais", key=f"btn_{convenio.CONVENIO_ID}"):
                        st.session_state.convenio_selecionado = df_convenios.loc[df_convenios['CONVENIO_ID'] == convenio.CONVENIO_ID].to_dict('records')[0]
                        st.rerun()