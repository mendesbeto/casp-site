import streamlit as st
import pandas as pd
import sqlite3
from auth import verify_password, get_user_by_email, get_db_connection
from file_utils import save_uploaded_file
from streamlit_quill import st_quill
import matplotlib.pyplot as plt
from social_utils import display_social_media_links
from datetime import datetime

display_social_media_links()

st.set_page_config(page_title="Área do Administrador", layout="wide")

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

def update_user_status(user_id, status):
    """Atualiza o status de um usuário no banco de dados."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET STATUS = ? WHERE ID = ?", (status, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar status do usuário: {e}")
        return False
    finally:
        conn.close()

def insert_record(table_name, record_dict):
    """Insere um novo registro em uma tabela."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        columns = ', '.join(record_dict.keys())
        placeholders = ', '.join(['?'] * len(record_dict))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(record_dict.values()))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao inserir registro: {e}")
        return False
    finally:
        conn.close()

def update_record(table_name, record_dict, where_clause):
    """Atualiza um registro em uma tabela."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in record_dict.keys()])
        params = list(record_dict.values()) + list(where_clause.values())
        where_keys = " AND ".join([f"{key} = ?" for key in where_clause.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_keys}"
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar registro: {e}")
        return False
    finally:
        conn.close()

def delete_record(table_name, where_clause):
    """Deleta um registro de uma tabela."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        where_keys = " AND ".join([f"{key} = ?" for key in where_clause.keys()])
        params = list(where_clause.values())
        query = f"DELETE FROM {table_name} WHERE {where_keys}"
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao deletar registro: {e}")
        return False
    finally:
        conn.close()

# --- PÁGINA DE LOGIN DO ADMIN ---
def pagina_login_admin():
    st.header("Login do Administrador")
    with st.form("admin_login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            user = get_user_by_email(email)
            
            if user and user['NIVEL_ACESSO'] == 'ADMIN':
                if verify_password(senha, user['SENHA_HASH']):
                    st.session_state['admin_logged_in'] = True
                    st.session_state['admin_info'] = dict(user)
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos.")
            else:
                st.error("Acesso negado. Verifique as credenciais.")

# --- PÁGINA PRINCIPAL DO ADMIN ---
def pagina_admin():
    st.title("Painel de Administração")
    st.write(f"Bem-vindo(a), {st.session_state['admin_info']['NOME']}!")

    if st.button("Sair"):
        del st.session_state['admin_logged_in']
        del st.session_state['admin_info']
        st.rerun()

    tab_usuarios, tab_institucional, tab_convenios, tab_noticias, tab_eventos, tab_financas, tab_parceiros, tab_servicos, tab_beneficios, tab_comentarios, tab_contatos, tab_log_login = st.tabs([
        "👥 Usuários", "📰 Institucional", "🏥 Convênios", "📰 Notícias", "🎉 Eventos", "💰 Financeiro", "🤝 Parceiros", "🛠️ Serviços", "✨ Benefícios", "💬 Comentários", "📧 Contatos", "📜 Log de Atividades"
    ])

    with tab_usuarios:
        gerenciar_usuarios()
    with tab_institucional:
        gerenciar_institucional()
    with tab_convenios:
        gerenciar_convenios()
    with tab_noticias:
        gerenciar_noticias()
    with tab_eventos:
        gerenciar_eventos()
    with tab_financas:
        gerenciar_financas()
    with tab_parceiros:
        gerenciar_parceiros()
    with tab_servicos:
        gerenciar_servicos()
    with tab_beneficios:
        gerenciar_beneficios()
    with tab_comentarios:
        gerenciar_comentarios()
    with tab_contatos:
        gerenciar_contatos()
    with tab_log_login:
        gerenciar_log_atividades()

# --- GERENCIAMENTO DE USUÁRIOS ---
def gerenciar_usuarios():
    st.subheader("Visão Geral dos Usuários")
    df_usuarios = carregar_dados_db('usuarios')

    if df_usuarios.empty:
        st.info("Nenhum usuário para exibir.")
        return

    # Estilos CSS para os cartões de métricas
    st.markdown("""
    <style>
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: box-shadow 0.3s ease-in-out;
    }
    .metric-card:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .metric-card h3 {
        margin: 0 0 10px 0;
        font-size: 1.1rem;
        color: #4F4F4F;
        font-weight: bold;
    }
    .metric-card p {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 600;
    }
    .status-ativo p { color: #28a745; }
    .status-inativo p { color: #dc3545; }
    .status-pendente p { color: #ffc107; }
    .nivel-admin p { color: #007bff; }
    .nivel-membro p { color: #6c757d; }
    </style>
    """, unsafe_allow_html=True)

    # Contagens
    status_counts = df_usuarios['STATUS'].value_counts()
    nivel_counts = df_usuarios['NIVEL_ACESSO'].value_counts()
    total_users = len(df_usuarios)

    # Card para total de usuários
    st.markdown(f"""
    <div class="metric-card">
        <h3>Total de Usuários</h3>
        <p>{total_users}</p>
    </div>
    """, unsafe_allow_html=True)

    # Cards para Status
    st.markdown("### Usuários por Status")
    status_map = {'ATIVO': 'ativo', 'INATIVO': 'inativo', 'PENDENTE': 'pendente'}
    
    # Garante que todos os status principais sejam exibidos, mesmo que a contagem seja 0
    for status in ['ATIVO', 'INATIVO', 'PENDENTE']:
        if status not in status_counts:
            status_counts[status] = 0
            
    cols_status = st.columns(len(status_counts))
    
    for i, (status, count) in enumerate(status_counts.items()):
        with cols_status[i]:
            st.markdown(f"""
            <div class="metric-card status-{status_map.get(status, '')}">
                <h3>{status.capitalize()}</h3>
                <p>{count}</p>
            </div>
            """, unsafe_allow_html=True)

    # Cards para Nível de Acesso
    st.markdown("### Usuários por Nível de Acesso")
    nivel_map = {'ADMIN': 'admin', 'MEMBRO': 'membro'}

    # Garante que todos os níveis de acesso principais sejam exibidos
    for nivel in ['ADMIN', 'MEMBRO']:
        if nivel not in nivel_counts:
            nivel_counts[nivel] = 0
            
    cols_nivel = st.columns(len(nivel_counts))

    for i, (nivel, count) in enumerate(nivel_counts.items()):
        with cols_nivel[i]:
            st.markdown(f"""
            <div class="metric-card nivel-{nivel_map.get(nivel, '')}">
                <h3>{nivel.capitalize()}</h3>
                <p>{count}</p>
            </div>
            """, unsafe_allow_html=True)


    st.subheader("Novos Cadastros ao Longo do Tempo")
    # Certifica-se de que a coluna de data está no formato datetime
    df_usuarios['DATA_CADASTRO'] = pd.to_datetime(df_usuarios['DATA_CADASTRO'], errors='coerce')
    cadastros_por_dia = df_usuarios.dropna(subset=['DATA_CADASTRO']).set_index('DATA_CADASTRO').resample('D').size()
    st.line_chart(cadastros_por_dia)

    st.divider()

    # Botão para exportar dados
    st.subheader("Exportar Relatório de Usuários")
    csv = df_usuarios.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exportar Relatório de Usuários (CSV)",
        data=csv,
        file_name='relatorio_usuarios.csv',
        mime='text/csv',
    )

    st.divider()

    # Seção de Aprovações Pendentes
    st.subheader("Aprovações Pendentes")
    df_pendentes = df_usuarios[df_usuarios['STATUS'] == 'PENDENTE']

    if df_pendentes.empty:
        st.info("Nenhuma solicitação pendente.")
    else:
        for index, row in df_pendentes.iterrows():
            with st.expander(f"{row['NOME']} ({row['EMAIL']})"):
                st.write(f"**Plano:** {row.get('PLANO_ESCOLHIDO', 'N/A')}")
                st.write(f"**Serviço:** {row.get('SERVICO_ESCOLHIDO', 'N/A')}")
                st.write(f"**Dependentes:** {row.get('ADICIONAIS_NOMES', 'Nenhum')}")
                if st.button("Aprovar Usuário", key=f"approve_{row['ID']}"):
                    if update_user_status(row['ID'], 'ATIVO'):
                        st.success(f"Usuário {row['NOME']} aprovado!")
                        st.rerun()

def gerenciar_institucional():
    st.subheader("Gerenciar Informações Institucionais")
    
    df_institucional = carregar_dados_db('institucional')
    
    if df_institucional.empty:
        st.warning("Tabela 'institucional' está vazia. Inserindo dados padrão.")
        conn = get_db_connection()
        try:
            default_data = {
                'TITULO_SITE': 'Nome da Associação', 'LOGO_URL': '', 'HISTORICO': '',
                'MISSAO': '', 'VISAO': '', 'VALORES': '', 'EMAIL_CONTATO': '',
                'TELEFONE_CONTATO': '', 'ENDERECO': ''
            }
            pd.DataFrame([default_data]).to_sql('institucional', conn, if_exists='append', index=False)
            st.rerun()
        finally:
            conn.close()
        return

    institucional_data = df_institucional.iloc[0].to_dict()

    with st.form("form_institucional"):
        st.write("Edite as informações que aparecem em várias partes do site.")
        
        novos_dados = {}
        novos_dados['TITULO_SITE'] = st.text_input("Título do Site", value=institucional_data.get('TITULO_SITE', ''))
        novos_dados['LOGO_URL'] = st.text_input("URL da Logo Principal", value=institucional_data.get('LOGO_URL', ''))
        
        st.subheader("Página 'Sobre Nós'")
        novos_dados['HISTORICO'] = st.text_area("Nossa História", value=institucional_data.get('HISTORICO', ''), height=200)
        novos_dados['MISSAO'] = st.text_area("Missão", value=institucional_data.get('MISSAO', ''), height=100)
        novos_dados['VISAO'] = st.text_area("Visão", value=institucional_data.get('VISAO', ''), height=100)
        novos_dados['VALORES'] = st.text_area("Valores", value=institucional_data.get('VALORES', ''), height=100)
        
        st.subheader("Informações de Contato")
        novos_dados['EMAIL_CONTATO'] = st.text_input("Email de Contato", value=institucional_data.get('EMAIL_CONTATO', ''))
        novos_dados['TELEFONE_CONTATO'] = st.text_input("Telefone de Contato", value=institucional_data.get('TELEFONE_CONTATO', ''))
        novos_dados['ENDERECO'] = st.text_input("Endereço Físico", value=institucional_data.get('ENDERECO', ''))

        if st.form_submit_button("Salvar Alterações Institucionais", type="primary"):
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                set_clause = ", ".join([f"{key} = ?" for key in novos_dados.keys()])
                params = list(novos_dados.values())
                cursor.execute(f"UPDATE institucional SET {set_clause} WHERE rowid = 1", params)
                conn.commit()
                st.success("Informações institucionais atualizadas com sucesso!")
                st.cache_data.clear()
                st.rerun()
            except sqlite3.Error as e:
                st.error(f"Erro ao salvar no banco de dados: {e}")
            finally:
                conn.close()

def gerenciar_convenios():
    st.subheader("Gerenciar Convênios")
    
    df_convenios = carregar_dados_db('convenios')

    st.write("Adicionar, editar ou remover convênios da plataforma.")

    # Formulário para adicionar novo convênio
    with st.expander("➕ Adicionar Novo Convênio"):
        with st.form("form_novo_convenio", clear_on_submit=True):
            nome = st.text_input("Nome do Convênio")
            tipo_servico = st.text_input("Tipo de Serviço (Ex: Saúde, Educação)")
            descricao = st.text_area("Descrição Completa")
            imagem_url = st.text_input("URL da Imagem de Destaque")
            icon_url = st.text_input("URL do Ícone")
            destaque = st.checkbox("Marcar como Destaque na Home")
            status = st.selectbox("Status", ["ATIVO", "INATIVO"])

            if st.form_submit_button("Adicionar Convênio"):
                if nome and tipo_servico and descricao:
                    new_id = df_convenios['CONVENIO_ID'].max() + 1 if not df_convenios.empty else 1
                    novo_convenio = {
                        'CONVENIO_ID': int(new_id),
                        'NOME_CONVENIO': nome,
                        'TIPO_SERVICO': tipo_servico,
                        'DESCRICAO': descricao,
                        'IMAGEM_URL': imagem_url,
                        'ICON_URL': icon_url,
                        'DESTAQUE': destaque,
                        'STATUS': status
                    }
                    if insert_record('convenios', novo_convenio):
                        st.success(f"Convênio '{nome}' adicionado com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("Nome, Tipo de Serviço e Descrição são obrigatórios.")

    st.divider()

    # Listagem e edição dos convênios existentes
    st.write("Convênios Cadastrados")
    if not df_convenios.empty:
        for index, row in df_convenios.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.subheader(row['NOME_CONVENIO'])
                
                with col2.expander("Editar/Excluir"):
                    with st.form(f"form_edit_{row['CONVENIO_ID']}"):
                        nome_edit = st.text_input("Nome", value=row['NOME_CONVENIO'], key=f"nome_{row['CONVENIO_ID']}")
                        tipo_edit = st.text_input("Tipo", value=row['TIPO_SERVICO'], key=f"tipo_{row['CONVENIO_ID']}")
                        desc_edit = st.text_area("Descrição", value=row['DESCRICAO'], key=f"desc_{row['CONVENIO_ID']}")
                        img_edit = st.text_input("Imagem URL", value=row['IMAGEM_URL'], key=f"img_{row['CONVENIO_ID']}")
                        icon_edit = st.text_input("Ícone URL", value=row['ICON_URL'], key=f"icon_{row['CONVENIO_ID']}")
                        destaque_edit = st.checkbox("Destaque", value=row['DESTAQUE'], key=f"dest_{row['CONVENIO_ID']}")
                        status_edit = st.selectbox("Status", ["ATIVO", "INATIVO"], index=["ATIVO", "INATIVO"].index(row['STATUS']), key=f"stat_{row['CONVENIO_ID']}")

                        col_edit, col_del = st.columns(2)
                        if col_edit.form_submit_button("Salvar Alterações"):
                            dados_atualizados = {
                                'NOME_CONVENIO': nome_edit, 
                                'TIPO_SERVICO': tipo_edit, 
                                'DESCRICAO': desc_edit, 
                                'IMAGEM_URL': img_edit, 
                                'ICON_URL': icon_edit, 
                                'DESTAQUE': destaque_edit, 
                                'STATUS': status_edit
                            }
                            if update_record('convenios', dados_atualizados, {'CONVENIO_ID': row['CONVENIO_ID']}):
                                st.success("Alterações salvas!")
                                st.cache_data.clear()
                                st.rerun()
                        
                        if col_del.form_submit_button("Excluir"):
                            if delete_record('convenios', {'CONVENIO_ID': row['CONVENIO_ID']}):
                                st.warning(f"Convênio '{row['NOME_CONVENIO']}' excluído.")
                                st.cache_data.clear()
                                st.rerun()
    else:
        st.info("Nenhum convênio cadastrado.")

def gerenciar_noticias():
    st.subheader("Gerenciar Notícias")
    
    df_noticias = carregar_dados_db('noticias')

    with st.expander("➕ Adicionar Nova Notícia"):
        with st.form("form_nova_noticia", clear_on_submit=True):
            titulo = st.text_input("Título da Notícia")
            conteudo = st_quill(placeholder="Escreva o conteúdo aqui...", html=True)
            imagem_url = st.text_input("URL da Imagem de Capa")
            destaque = st.checkbox("Marcar como Destaque na Home")
            status = st.selectbox("Status da Publicação", ["PUBLICADO", "RASCUNHO"])
            tags = st.text_input("Tags (separadas por vírgula)")

            if st.form_submit_button("Salvar Notícia"):
                if titulo and conteudo:
                    new_id = df_noticias['ID'].max() + 1 if not df_noticias.empty else 1
                    nova_noticia = {
                        'ID': int(new_id),
                        'TITULO': titulo,
                        'CONTEUDO': conteudo,
                        'DATA': datetime.now().strftime('%Y-%m-%d'),
                        'IMAGEM_URL': imagem_url,
                        'DESTAQUE': destaque,
                        'STATUS': status,
                        'TAGS': tags
                    }
                    if insert_record('noticias', nova_noticia):
                        st.success("Notícia salva com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("Título e Conteúdo são obrigatórios.")

    st.divider()
    st.write("Notícias Cadastradas")
    
    if not df_noticias.empty:
        for index, row in df_noticias.iterrows():
            with st.expander(f"{row['TITULO']} ({row['STATUS']})"):
                with st.form(f"form_edit_noticia_{row['ID']}"):
                    titulo_edit = st.text_input("Título", value=row['TITULO'], key=f"titulo_n_{row['ID']}")
                    conteudo_edit = st_quill(value=row['CONTEUDO'], key=f"cont_n_{row['ID']}")
                    imagem_edit = st.text_input("Imagem URL", value=row['IMAGEM_URL'], key=f"img_n_{row['ID']}")
                    destaque_edit = st.checkbox("Destaque", value=row['DESTAQUE'], key=f"dest_n_{row['ID']}")
                    status_edit = st.selectbox("Status", ["PUBLICADO", "RASCUNHO"], index=["PUBLICADO", "RASCUNHO"].index(row['STATUS']), key=f"stat_n_{row['ID']}")
                    tags_edit = st.text_input("Tags", value=row.get('TAGS', ''), key=f"tags_n_{row['ID']}")

                    col_edit, col_del = st.columns(2)
                    if col_edit.form_submit_button("Salvar"):
                        dados_atualizados = {
                            'TITULO': titulo_edit, 
                            'CONTEUDO': conteudo_edit, 
                            'IMAGEM_URL': imagem_edit, 
                            'DESTAQUE': destaque_edit, 
                            'STATUS': status_edit, 
                            'TAGS': tags_edit
                        }
                        if update_record('noticias', dados_atualizados, {'ID': row['ID']}):
                            st.success("Notícia atualizada.")
                            st.cache_data.clear()
                            st.rerun()
                    
                    if col_del.form_submit_button("Excluir"):
                        if delete_record('noticias', {'ID': row['ID']}):
                            st.warning("Notícia excluída.")
                            st.cache_data.clear()
                            st.rerun()
    else:
        st.info("Nenhuma notícia cadastrada.")

def gerenciar_eventos():
    st.subheader("Gerenciar Eventos")
    
    df_eventos = carregar_dados_db('eventos')

    with st.expander("➕ Adicionar Novo Evento"):
        with st.form("form_novo_evento", clear_on_submit=True):
            titulo = st.text_input("Título do Evento")
            descricao = st.text_area("Descrição")
            data_evento = st.date_input("Data do Evento")
            hora_evento = st.time_input("Hora do Evento")
            local = st.text_input("Local")
            imagem_url = st.text_input("URL da Imagem")
            status = st.selectbox("Status", ["AGENDADO", "REALIZADO", "CANCELADO"])

            if st.form_submit_button("Adicionar Evento"):
                if titulo and descricao and data_evento and hora_evento and local:
                    new_id = df_eventos['EVENTO_ID'].max() + 1 if not df_eventos.empty else 1
                    novo_evento = {
                        'EVENTO_ID': int(new_id),
                        'TITULO': titulo,
                        'DESCRICAO': descricao,
                        'DATA_EVENTO': data_evento.strftime('%Y-%m-%d'),
                        'HORA_EVENTO': hora_evento.strftime('%H:%M'),
                        'LOCAL': local,
                        'IMAGEM_URL': imagem_url,
                        'STATUS': status
                    }
                    if insert_record('eventos', novo_evento):
                        st.success(f"Evento '{titulo}' adicionado com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("Todos os campos, exceto imagem, são obrigatórios.")

    st.divider()
    st.write("Eventos Cadastrados")

    if not df_eventos.empty:
        for index, row in df_eventos.iterrows():
            with st.expander(f"{row['TITULO']} - {pd.to_datetime(row['DATA_EVENTO']).strftime('%d/%m/%Y')}"):
                with st.form(f"form_edit_evento_{row['EVENTO_ID']}"):
                    titulo_edit = st.text_input("Título", value=row['TITULO'], key=f"titulo_e_{row['EVENTO_ID']}")
                    desc_edit = st.text_area("Descrição", value=row['DESCRICAO'], key=f"desc_e_{row['EVENTO_ID']}")
                    data_edit = st.date_input("Data", value=pd.to_datetime(row['DATA_EVENTO']), key=f"data_e_{row['EVENTO_ID']}")
                    hora_edit = st.time_input("Hora", value=datetime.strptime(row['HORA_EVENTO'], '%H:%M').time(), key=f"hora_e_{row['EVENTO_ID']}")
                    local_edit = st.text_input("Local", value=row['LOCAL'], key=f"local_e_{row['EVENTO_ID']}")
                    img_edit = st.text_input("Imagem URL", value=row['IMAGEM_URL'], key=f"img_e_{row['EVENTO_ID']}")
                    status_edit = st.selectbox("Status", ["AGENDADO", "REALIZADO", "CANCELADO"], index=["AGENDADO", "REALIZADO", "CANCELADO"].index(row['STATUS']), key=f"stat_e_{row['EVENTO_ID']}")

                    col_edit, col_del = st.columns(2)
                    if col_edit.form_submit_button("Salvar Alterações"):
                        dados_atualizados = {
                            'TITULO': titulo_edit, 
                            'DESCRICAO': desc_edit, 
                            'DATA_EVENTO': data_edit.strftime('%Y-%m-%d'), 
                            'HORA_EVENTO': hora_edit.strftime('%H:%M'), 
                            'LOCAL': local_edit, 
                            'IMAGEM_URL': img_edit, 
                            'STATUS': status_edit
                        }
                        if update_record('eventos', dados_atualizados, {'EVENTO_ID': row['EVENTO_ID']}):
                            st.success("Alterações salvas!")
                            st.cache_data.clear()
                            st.rerun()
                    
                    if col_del.form_submit_button("Excluir"):
                        if delete_record('eventos', {'EVENTO_ID': row['EVENTO_ID']}):
                            st.warning(f"Evento '{row['TITULO']}' excluído.")
                            st.cache_data.clear()
                            st.rerun()
    else:
        st.info("Nenhum evento cadastrado.")

def gerenciar_financas():
    st.subheader("Gerenciar Finanças")
    
    df_financas = carregar_dados_db('financas')
    
    if df_financas.empty:
        st.info("Nenhum registro financeiro encontrado.")
        return

    st.write("Histórico de Transações")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    status_filter = col1.multiselect("Filtrar por Status", options=df_financas['STATUS'].unique(), default=df_financas['STATUS'].unique())
    
    df_filtered = df_financas[df_financas['STATUS'].isin(status_filter)]
    
    st.dataframe(df_filtered)

def gerenciar_parceiros():
    st.subheader("Gerenciar Parceiros")
    
    df_parceiros = carregar_dados_db('parceiros')
    df_convenios = carregar_dados_db('convenios')
    
    if df_convenios.empty:
        st.warning("Cadastre um convênio antes de adicionar parceiros.")
        return

    convenio_map = dict(zip(df_convenios['CONVENIO_ID'], df_convenios['NOME_CONVENIO']))

    with st.expander("➕ Adicionar Novo Parceiro"):
        with st.form("form_novo_parceiro", clear_on_submit=True):
            convenio_id = st.selectbox("Convênio Associado", options=convenio_map.keys(), format_func=lambda x: convenio_map[x])
            nome = st.text_input("Nome do Parceiro")
            detalhes = st.text_area("Detalhes (descontos, etc)")
            endereco = st.text_input("Endereço")
            telefone = st.text_input("Telefone")
            website = st.text_input("Website")

            if st.form_submit_button("Adicionar Parceiro"):
                if nome and convenio_id:
                    new_id = df_parceiros['PARCEIRO_ID'].max() + 1 if not df_parceiros.empty else 1
                    novo_parceiro = {
                        'PARCEIRO_ID': int(new_id),
                        'CONVENIO_ID': convenio_id,
                        'NOME_PARCEIRO': nome,
                        'DETALHES': detalhes,
                        'ENDERECO': endereco,
                        'TELEFONE': telefone,
                        'WEBSITE': website
                    }
                    if insert_record('parceiros', novo_parceiro):
                        st.success(f"Parceiro '{nome}' adicionado com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("Nome e Convênio são obrigatórios.")

    st.divider()
    st.write("Parceiros Cadastrados")

    if not df_parceiros.empty:
        for index, row in df_parceiros.iterrows():
            with st.expander(f"{row['NOME_PARCEIRO']} (Convênio: {convenio_map.get(row['CONVENIO_ID'], 'N/A')})"):
                with st.form(f"form_edit_parceiro_{row['PARCEIRO_ID']}"):
                    convenio_id_edit = st.selectbox("Convênio", options=convenio_map.keys(), format_func=lambda x: convenio_map[x], index=list(convenio_map.keys()).index(row['CONVENIO_ID']), key=f"conv_p_{row['PARCEIRO_ID']}")
                    nome_edit = st.text_input("Nome", value=row['NOME_PARCEIRO'], key=f"nome_p_{row['PARCEIRO_ID']}")
                    detalhes_edit = st.text_area("Detalhes", value=row['DETALHES'], key=f"det_p_{row['PARCEIRO_ID']}")
                    endereco_edit = st.text_input("Endereço", value=row['ENDERECO'], key=f"end_p_{row['PARCEIRO_ID']}")
                    telefone_edit = st.text_input("Telefone", value=row['TELEFONE'], key=f"tel_p_{row['PARCEIRO_ID']}")
                    website_edit = st.text_input("Website", value=row['WEBSITE'], key=f"web_p_{row['PARCEIRO_ID']}")

                    col_edit, col_del = st.columns(2)
                    if col_edit.form_submit_button("Salvar"):
                        dados_atualizados = {
                            'CONVENIO_ID': convenio_id_edit, 
                            'NOME_PARCEIRO': nome_edit, 
                            'DETALHES': detalhes_edit, 
                            'ENDERECO': endereco_edit, 
                            'TELEFONE': telefone_edit, 
                            'WEBSITE': website_edit
                        }
                        if update_record('parceiros', dados_atualizados, {'PARCEIRO_ID': row['PARCEIRO_ID']}):
                            st.success("Parceiro atualizado.")
                            st.cache_data.clear()
                            st.rerun()
                    
                    if col_del.form_submit_button("Excluir"):
                        if delete_record('parceiros', {'PARCEIRO_ID': row['PARCEIRO_ID']}):
                            st.warning("Parceiro excluído.")
                            st.cache_data.clear()
                            st.rerun()
    else:
        st.info("Nenhum parceiro cadastrado.")

def gerenciar_servicos():
    st.subheader("Gerenciar Serviços e Planos")
    
    df_servicos = carregar_dados_db('servicos')

    with st.expander("➕ Adicionar Novo Serviço"):
        with st.form("form_novo_servico", clear_on_submit=True):
            tipo_servico = st.text_input("Tipo de Serviço (Ex: Plano Odontológico)")
            descricao = st.text_area("Descrição do Serviço")
            valor_mensal = st.number_input("Valor Mensal (R$)", min_value=0.0, format="%.2f")
            cupom_mensal = st.number_input("Cupom Mensal (R$)", min_value=0.0, format="%.2f")
            cupom_semestral = st.number_input("Cupom Semestral (%)", min_value=0.0, max_value=100.0)
            cupom_anual = st.number_input("Cupom Anual (%)", min_value=0.0, max_value=100.0)
            valor_adicional = st.number_input("Valor por Dependente (R$)", min_value=0.0, format="%.2f")

            if st.form_submit_button("Adicionar Serviço"):
                if tipo_servico and valor_mensal > 0:
                    new_id = df_servicos['SERVICO_ID'].max() + 1 if not df_servicos.empty else 1
                    novo_servico = {
                        'SERVICO_ID': int(new_id),
                        'TIPO_SERVICO': tipo_servico,
                        'DESCRICAO_SERVICO': descricao,
                        'VALOR_MENSAL': valor_mensal,
                        'CUPOM_MESAL': cupom_mensal,
                        'CUPOM_SEMESTRAL': cupom_semestral,
                        'CUPOM_ANUAL': cupom_anual,
                        'VALOR_ADICIONAL': valor_adicional
                    }
                    if insert_record('servicos', novo_servico):
                        st.success(f"Serviço '{tipo_servico}' adicionado com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("Tipo de Serviço and Valor Mensal are required.")

    st.divider()
    st.write("Serviços Cadastrados")

    if not df_servicos.empty:
        for index, row in df_servicos.iterrows():
            with st.expander(f"{row['TIPO_SERVICO']}"):
                with st.form(f"form_edit_servico_{row['SERVICO_ID']}"):
                    tipo_servico_edit = st.text_input("Tipo de Serviço", value=row['TIPO_SERVICO'], key=f"tipo_s_{row['SERVICO_ID']}")
                    desc_edit = st.text_area("Descrição", value=row['DESCRICAO_SERVICO'], key=f"desc_s_{row['SERVICO_ID']}")
                    valor_mensal_edit = st.number_input("Valor Mensal (R$)", value=row['VALOR_MENSAL'], min_value=0.0, format="%.2f", key=f"valor_s_{row['SERVICO_ID']}")
                    cupom_mensal_edit = st.number_input("Cupom Mensal (R$)", value=row['CUPOM_MESAL'], min_value=0.0, format="%.2f", key=f"cupom_m_s_{row['SERVICO_ID']}")
                    cupom_semestral_edit = st.number_input("Cupom Semestral (%)", value=float(row['CUPOM_SEMESTRAL']), min_value=0.0, max_value=100.0, key=f"cupom_s_s_{row['SERVICO_ID']}")
                    cupom_anual_edit = st.number_input("Cupom Anual (%)", value=float(row['CUPOM_ANUAL']), min_value=0.0, max_value=100.0, key=f"cupom_a_s_{row['SERVICO_ID']}")
                    valor_adicional_edit = st.number_input("Valor por Dependente (R$)", value=row['VALOR_ADICIONAL'], min_value=0.0, format="%.2f", key=f"add_s_{row['SERVICO_ID']}")

                    col_edit, col_del = st.columns(2)
                    if col_edit.form_submit_button("Salvar"):
                        dados_atualizados = {
                            'TIPO_SERVICO': tipo_servico_edit, 
                            'DESCRICAO_SERVICO': desc_edit, 
                            'VALOR_MENSAL': valor_mensal_edit, 
                            'CUPOM_MESAL': cupom_mensal_edit, 
                            'CUPOM_SEMESTRAL': cupom_semestral_edit, 
                            'CUPOM_ANUAL': cupom_anual_edit, 
                            'VALOR_ADICIONAL': valor_adicional_edit
                        }
                        if update_record('servicos', dados_atualizados, {'SERVICO_ID': row['SERVICO_ID']}):
                            st.success("Serviço atualizado.")
                            st.cache_data.clear()
                            st.rerun()
                    
                    if col_del.form_submit_button("Excluir"):
                        if delete_record('servicos', {'SERVICO_ID': row['SERVICO_ID']}):
                            st.warning("Serviço excluído.")
                            st.cache_data.clear()
                            st.rerun()
    else:
        st.info("Nenhum serviço cadastrado.")

def gerenciar_beneficios():
    st.subheader("Gerenciar Benefícios")
    
    df_beneficios = carregar_dados_db('beneficios')

    with st.expander("➕ Adicionar Novo Benefício"):
        with st.form("form_novo_beneficio", clear_on_submit=True):
            titulo = st.text_input("Título do Benefício")
            descricao = st.text_area("Descrição do Benefício")
            icone = st.text_input("Ícone (Emoji)")

            if st.form_submit_button("Adicionar Benefício"):
                if titulo and descricao:
                    new_id = df_beneficios['BENEFICIO_ID'].max() + 1 if not df_beneficios.empty else 1
                    novo_beneficio = {
                        'BENEFICIO_ID': int(new_id),
                        'TITULO': titulo,
                        'DESCRICAO_BENEFICIO': descricao,
                        'ICONE': icone
                    }
                    if insert_record('beneficios', novo_beneficio):
                        st.success(f"Benefício '{titulo}' adicionado com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                else:
                    st.warning("Título e Descrição são obrigatórios.")

    st.divider()
    st.write("Benefícios Cadastrados")

    if not df_beneficios.empty:
        for index, row in df_beneficios.iterrows():
            with st.expander(f"{row['ICONE']} {row['TITULO']}"):
                with st.form(f"form_edit_beneficio_{row['BENEFICIO_ID']}"):
                    titulo_edit = st.text_input("Título", value=row['TITULO'], key=f"titulo_b_{row['BENEFICIO_ID']}")
                    desc_edit = st.text_area("Descrição", value=row['DESCRICAO_BENEFICIO'], key=f"desc_b_{row['BENEFICIO_ID']}")
                    icone_edit = st.text_input("Ícone", value=row['ICONE'], key=f"icon_b_{row['BENEFICIO_ID']}")

                    col_edit, col_del = st.columns(2)
                    if col_edit.form_submit_button("Salvar"):
                        dados_atualizados = {
                            'TITULO': titulo_edit, 
                            'DESCRICAO_BENEFICIO': desc_edit, 
                            'ICONE': icone_edit
                        }
                        if update_record('beneficios', dados_atualizados, {'BENEFICIO_ID': row['BENEFICIO_ID']}):
                            st.success("Benefício atualizado.")
                            st.cache_data.clear()
                            st.rerun()
                    
                    if col_del.form_submit_button("Excluir"):
                        if delete_record('beneficios', {'BENEFICIO_ID': row['BENEFICIO_ID']}):
                            st.warning("Benefício excluído.")
                            st.cache_data.clear()
                            st.rerun()
    else:
        st.info("Nenhum benefício cadastrado.")

def gerenciar_comentarios():
    st.subheader("Moderar Comentários")
    
    df_comentarios = carregar_dados_db('comentarios')
    
    if df_comentarios.empty:
        st.info("Nenhum comentário para moderar.")
        return

    st.write("Comentários pendentes de aprovação, aprovados e rejeitados.")
    
    status_filter = st.selectbox("Filtrar por Status", options=['PENDENTE', 'APROVADO', 'REJEITADO'])
    
    df_filtered = df_comentarios[df_comentarios['STATUS'] == status_filter]

    if df_filtered.empty:
        st.info(f"Nenhum comentário com o status '{status_filter}'.")
    else:
        for index, row in df_filtered.iterrows():
            with st.container(border=True):
                st.write(f"**Autor:** {row['NOME_USUARIO']} em {row['TIMESTAMP']}")
                st.write(f"**Notícia ID:** {row['NOTICIA_ID']}")
                st.info(f"**Comentário:** {row['COMENTARIO']}")

                if row['STATUS'] == 'PENDENTE':
                    col1, col2 = st.columns(2)
                    if col1.button("Aprovar", key=f"approve_c_{row['COMENTARIO_ID']}"):
                        if update_record('comentarios', {'STATUS': 'APROVADO'}, {'COMENTARIO_ID': row['COMENTARIO_ID']}):
                            st.success("Comentário aprovado.")
                            st.cache_data.clear()
                            st.rerun()
                    if col2.button("Rejeitar", key=f"reject_c_{row['COMENTARIO_ID']}"):
                        if update_record('comentarios', {'STATUS': 'REJEITADO'}, {'COMENTARIO_ID': row['COMENTARIO_ID']}):
                            st.warning("Comentário rejeitado.")
                            st.cache_data.clear()
                            st.rerun()

def gerenciar_contatos():
    st.subheader("Gerenciar Mensagens de Contato")
    
    df_contatos = carregar_dados_db('contatos')
    
    if df_contatos.empty:
        st.info("Nenhuma mensagem de contato recebida.")
        return

    st.write("Mensagens recebidas através do formulário de contato.")
    
    status_filter = st.selectbox("Filtrar por Status", options=['NOVO', 'LIDO', 'RESPONDIDO', 'RESOLVIDO'])
    
    df_filtered = df_contatos[df_contatos['STATUS_ATENDIMENTO'] == status_filter]

    if df_filtered.empty:
        st.info(f"Nenhuma mensagem com o status '{status_filter}'.")
    else:
        for index, row in df_filtered.iterrows():
            with st.expander(f"De: {row['NOME']} ({row['EMAIL']}) - Assunto: {row['ASSUNTO']}"):
                st.write(f"**Recebido em:** {row['TIMESTAMP']}")
                st.write(f"**Telefone:** {row.get('TELEFONE', 'Não informado')}")
                st.info(f"**Mensagem:**\n\n{row['MENSAGEM']}")

                new_status = st.selectbox(
                    "Alterar status para:",
                    options=['NOVO', 'LIDO', 'RESPONDIDO', 'RESOLVIDO'],
                    index=['NOVO', 'LIDO', 'RESPONDIDO', 'RESOLVIDO'].index(row['STATUS_ATENDIMENTO']),
                    key=f"status_contato_{row['ID']}"
                )
                if st.button("Atualizar Status", key=f"update_contato_{row['ID']}"):
                    if update_record('contatos', {'STATUS_ATENDIMENTO': new_status}, {'ID': row['ID']}):
                        st.success("Status do contato atualizado.")
                        st.cache_data.clear()
                        st.rerun()

def gerenciar_log_atividades():
    st.subheader("Log de Atividades dos Usuários")
    
    df_log = carregar_dados_db('log_atividades')
    
    if df_log.empty:
        st.info("Nenhum registro de atividade encontrado.")
        return

    st.write("Logs de ações importantes realizadas pelos usuários no sistema.")
    
    st.dataframe(df_log.sort_values(by="TIMESTAMP", ascending=False))

# --- CONTROLE PRINCIPAL DA PÁGINA ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if st.session_state.admin_logged_in:
    pagina_admin()
else:
    pagina_login_admin()