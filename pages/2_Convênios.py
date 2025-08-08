import streamlit as st
import pandas as pd
import os
import numpy as np

st.set_page_config(page_title="Nossos Convênios", layout="wide")

@st.cache_data
def carregar_dados_convenios():
    return pd.read_csv('data/convenios.csv')

@st.cache_data
def carregar_dados_parceiros():
    filepath = 'data/parceiros.csv'
    return pd.read_csv(filepath) if os.path.exists(filepath) else pd.DataFrame()

@st.cache_data
def carregar_dados_ratings():
    """Carrega os dados de avaliações do CSV."""
    filepath = 'data/convenio_ratings.csv'
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return pd.DataFrame(columns=['RATING_ID', 'CONVENIO_ID', 'USER_ID', 'RATING'])
    return pd.read_csv(filepath)

def salvar_rating(convenio_id, user_id, rating):
    """Salva ou atualiza a avaliação de um usuário para um convênio."""
    filepath = 'data/convenio_ratings.csv'
    df_ratings = carregar_dados_ratings().copy()

    # Verifica se o usuário já avaliou este convênio
    existing_rating_index = df_ratings[(df_ratings['USER_ID'] == user_id) & (df_ratings['CONVENIO_ID'] == convenio_id)].index

    if not existing_rating_index.empty:
        # Atualiza a avaliação existente
        df_ratings.loc[existing_rating_index, 'RATING'] = rating
    else:
        # Adiciona uma nova avaliação
        new_id = (df_ratings['RATING_ID'].max() + 1) if not df_ratings.empty else 1
        new_rating = pd.DataFrame([{'RATING_ID': new_id, 'CONVENIO_ID': convenio_id, 'USER_ID': user_id, 'RATING': rating}])
        df_ratings = pd.concat([df_ratings, new_rating], ignore_index=True)
    
    df_ratings.to_csv(filepath, index=False)
    st.cache_data.clear()

df_convenios = carregar_dados_convenios()

st.title("Rede de Convênios")
st.write("Explore os benefícios exclusivos para nossos associados.")

# --- LÓGICA PARA EXIBIÇÃO ---
# Usamos o st.session_state para "lembrar" qual convênio foi selecionado.
if 'convenio_selecionado' not in st.session_state:
    st.session_state.convenio_selecionado = None

# Se um convênio foi selecionado, mostramos a página de detalhes
if st.session_state.convenio_selecionado:
    convenio = st.session_state.convenio_selecionado
    
    st.header(convenio['NOME_CONVENIO'])
    
    if st.button("⬅️ Voltar para a lista"):
        st.session_state.convenio_selecionado = None
        st.rerun() # Recarrega a página para mostrar a lista

    col1, col2 = st.columns([1, 2]) # Coluna da imagem menor que a do texto

    with col1:
        st.image(convenio['IMAGEM_URL'], use_container_width=True)

    with col2:
        st.image(convenio['ICON_URL'], width=60)
        st.write(convenio['DESCRICAO'])

        # --- SEÇÃO DE AVALIAÇÃO ---
        df_ratings = carregar_dados_ratings()
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

        df_parceiros = carregar_dados_parceiros()
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

# Se nenhum convênio foi selecionado, mostramos a lista
else:
    # --- BARRA DE BUSCA ---
    search_term = st.text_input("🔎 Buscar por nome ou tipo de serviço", placeholder="Ex: Saúde, Educação, Academia...")

    st.write("Clique em 'Ver Mais' para detalhes de cada convênio.")
    
    convenios_ativos = df_convenios[df_convenios['STATUS'] == 'ATIVO']

    # --- FILTRAGEM DOS DADOS ---
    if search_term:
        # Filtra por nome do convênio OU tipo de serviço. A busca é case-insensitive.
        convenios_filtrados = convenios_ativos[
            convenios_ativos['NOME_CONVENIO'].str.contains(search_term, case=False, na=False) |
            convenios_ativos['TIPO_SERVICO'].str.contains(search_term, case=False, na=False)
        ]
    else:
        convenios_filtrados = convenios_ativos

    # Criando colunas para um layout de grade
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
