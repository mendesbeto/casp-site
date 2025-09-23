import streamlit as st
import pandas as pd
from auth import verify_password, get_user_by_email, get_db_connection, insert_record, update_record, delete_record, get_max_id
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
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela {table_name}: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def update_user_status(user_id, status):
    """Atualiza o status de um usuário no banco de dados."""
    update_record('usuarios', {'"STATUS"': status}, {'"ID"': user_id})

# --- PÁGINA DE LOGIN DO ADMIN ---
def pagina_login_admin():
    st.header("Login do Administrador")
    with st.form("admin_login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            user = get_user_by_email(email)
            
            if user:
                if user.get('NIVEL_ACESSO') == 'ADMIN':
                    if verify_password(senha, user.get('SENHA_HASH')):
                        st.session_state['admin_logged_in'] = True
                        st.session_state['admin_info'] = user
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
                else:
                    st.error(f"O usuário com email {email} não é um administrador.")
            else:
                st.error(f"Nenhum usuário encontrado com o email {email}.")

# --- PÁGINA PRINCIPAL DO ADMIN ---
def pagina_admin():
    st.title("Painel de Administração")
    st.write(f"Bem-vindo(a), {st.session_state['admin_info']['NOME']}!")

    if st.button("Sair"):
        del st.session_state['admin_logged_in']
        del st.session_state['admin_info']
        st.rerun()

    tabs = st.tabs([
        "👥 Usuários", "📰 Institucional", "🏥 Convênios", "📰 Notícias", "🎉 Eventos", 
        "💰 Financeiro", "🤝 Parceiros", "🛠️ Serviços", "✨ Benefícios", 
        "💬 Comentários", "📧 Contatos", "📜 Log de Atividades"
    ])
    
    with tabs[0]:
        gerenciar_usuarios()
    with tabs[1]:
        gerenciar_institucional()
    with tabs[2]:
        gerenciar_convenios()
    with tabs[3]:
        gerenciar_noticias()
    with tabs[4]:
        gerenciar_eventos()
    with tabs[5]:
        gerenciar_financas()
    with tabs[6]:
        gerenciar_parceiros()
    with tabs[7]:
        gerenciar_servicos()
    with tabs[8]:
        gerenciar_beneficios()
    with tabs[9]:
        gerenciar_comentarios()
    with tabs[10]:
        gerenciar_contatos()
    with tabs[11]:
        gerenciar_log_atividades()

def gerenciar_usuarios():
    st.subheader("Gerenciamento de Usuários")
    df_users = carregar_dados_db('usuarios')

    if df_users.empty:
        st.info("Nenhum usuário cadastrado.")

    st.dataframe(df_users)

    if not df_users.empty:
        st.subheader("Aprovar/Bloquear Usuários")
        user_id_to_update = st.selectbox("Selecione o ID do usuário", df_users['ID'])
        new_status = st.selectbox("Selecione o novo status", ["ATIVO", "INATIVO", "PENDENTE", "BLOQUEADO"])
        if st.button("Atualizar Status"):
            update_user_status(user_id_to_update, new_status)
            st.success(f"Status do usuário {user_id_to_update} atualizado para {new_status}.")
            st.rerun()

    st.subheader("Adicionar Novo Usuário")
    with st.form("add_user_form", clear_on_submit=True):
        new_user_nome = st.text_input("Nome")
        new_user_email = st.text_input("Email")
        new_user_senha = st.text_input("Senha", type="password")
        new_user_nivel = st.selectbox("Nível de Acesso", ["MEMBRO", "ADMIN"])
        add_user_submitted = st.form_submit_button("Adicionar Usuário")

        if add_user_submitted:
            from auth import hash_password
            hashed_password = hash_password(new_user_senha)
            
            max_id = get_max_id('usuarios', '"ID"')
            new_id = int(max_id) + 1 if max_id else 1

            new_user_data = {
                '"ID"': str(new_id),
                '"NOME"': new_user_nome,
                '"EMAIL"': new_user_email,
                '"SENHA_HASH"': hashed_password,
                '"NIVEL_ACESSO"': new_user_nivel,
                '"STATUS"': 'ATIVO'
            }
            insert_record('usuarios', new_user_data)
            st.success("Novo usuário adicionado com sucesso.")
            st.rerun()

    if not df_users.empty:
        st.subheader("Editar Usuário")
        user_id_to_edit = st.selectbox("Selecione o ID do usuário para editar", df_users['ID'], key="edit_user_select")
        user_to_edit = df_users[df_users['ID'] == user_id_to_edit].iloc[0]

        with st.form("edit_user_form"):
            edit_user_nome = st.text_input("Nome", value=user_to_edit['NOME'])
            edit_user_email = st.text_input("Email", value=user_to_edit['EMAIL'])
            edit_user_nivel = st.selectbox("Nível de Acesso", ["MEMBRO", "ADMIN"], index=["MEMBRO", "ADMIN"].index(user_to_edit['NIVEL_ACESSO']))
            edit_user_submitted = st.form_submit_button("Salvar Alterações")

            if edit_user_submitted:
                updated_user_data = {
                    '"NOME"': edit_user_nome,
                    '"EMAIL"': edit_user_email,
                    '"NIVEL_ACESSO"': edit_user_nivel
                }
                update_record('usuarios', updated_user_data, {'"ID"': user_id_to_edit})
                st.success(f"Usuário {user_id_to_edit} atualizado com sucesso.")
                st.rerun()

        st.subheader("Excluir Usuário")
        user_id_to_delete = st.selectbox("Selecione o ID do usuário para excluir", df_users['ID'], key="delete_user_select")
        if st.button("Excluir Usuário", type="primary"):
            delete_record('usuarios', {'"ID"': user_id_to_delete})
            st.success(f"Usuário {user_id_to_delete} excluído com sucesso.")
            st.rerun()

def gerenciar_institucional():
    st.subheader("Gerenciamento Institucional")
    
    df_institucional = carregar_dados_db('institucional')
    
    if df_institucional.empty:
        st.warning("Nenhuma informação institucional encontrada. Por favor, adicione as informações.")
        with st.form("add_institucional_form"):
            institucional_data = {
                '"TITULO_SITE"': st.text_input("Título do Site"),
                '"LOGO_URL"': st.text_input("URL do Logo"),
                '"CNPJ_CPF"': st.text_input("CNPJ/CPF"),
                '"DATA_FUNDACAO"': st.text_input("Data de Fundação"),
                '"HISTORICO"': st_quill(placeholder="Histórico..."),
                '"MISSAO"': st_quill(placeholder="Missão..."),
                '"VISAO"': st_quill(placeholder="Visão..."),
                '"VALORES"': st_quill(placeholder="Valores..."),
                '"EMAIL_CONTATO"': st.text_input("Email de Contato"),
                '"TELEFONE_CONTATO"': st.text_input("Telefone de Contato"),
                '"ENDERECO"': st.text_input("Endereço"),
            }
            submitted = st.form_submit_button("Salvar Informações")
            if submitted:
                insert_record('institucional', institucional_data)
                st.success("Informações institucionais salvas com sucesso!")
                st.rerun()
        return

    item = df_institucional.iloc[0]
    
    with st.form("edit_institucional_form"):
        st.write("Edite as informações institucionais do site.")
        
        updated_data = {
            '"TITULO_SITE"': st.text_input("Título do Site", value=item.get('TITULO_SITE', '')),
            '"LOGO_URL"': st.text_input("URL do Logo", value=item.get('LOGO_URL', '')),
            '"CNPJ_CPF"': st.text_input("CNPJ/CPF", value=item.get('CNPJ_CPF', '')),
            '"DATA_FUNDACAO"': st.text_input("Data de Fundação", value=item.get('DATA_FUNDACAO', '')),
            '"HISTORICO"': st_quill(value=item.get('HISTORICO', ''), placeholder="Histórico..."),
            '"MISSAO"': st_quill(value=item.get('MISSAO', ''), placeholder="Missão..."),
            '"VISAO"': st_quill(value=item.get('VISAO', ''), placeholder="Visão..."),
            '"VALORES"': st_quill(value=item.get('VALORES', ''), placeholder="Valores..."),
            '"EMAIL_CONTATO"': st.text_input("Email de Contato", value=item.get('EMAIL_CONTATO', '')),
            '"TELEFONE_CONTATO"': st.text_input("Telefone de Contato", value=item.get('TELEFONE_CONTATO', '')),
            '"ENDERECO"': st.text_input("Endereço", value=item.get('ENDERECO', '')),
        }

        submitted = st.form_submit_button("Atualizar Informações")
        
        if submitted:
            update_record('institucional', updated_data, {'"ID"': item['ID']})
            st.success("Informações institucionais atualizadas com sucesso!")
            st.rerun()

def gerenciar_convenios():
    st.subheader("Gerenciamento de Convênios")
    df_convenios = carregar_dados_db('convenios')

    st.dataframe(df_convenios)

    st.subheader("Adicionar/Editar Convênio")

    convenio_options = {row['CONVENIO_ID']: row['NOME_CONVENIO'] for index, row in df_convenios.iterrows()}
    convenio_options['new'] = 'Adicionar Novo'
    selected_id = st.selectbox("Selecione um convênio para editar ou adicione um novo", options=list(convenio_options.keys()), format_func=lambda x: convenio_options[x])

    convenio_data = {}
    if selected_id != 'new':
        convenio_data = df_convenios[df_convenios['CONVENIO_ID'] == selected_id].iloc[0].to_dict()

    with st.form("convenio_form", clear_on_submit=True):
        nome = st.text_input("Nome do Convênio", value=convenio_data.get('NOME_CONVENIO', ''))
        descricao = st_quill(value=convenio_data.get('DESCRICAO', ''), placeholder="Descreva o convênio...")
        categoria = st.text_input("Tipo de Serviço", value=convenio_data.get('TIPO_SERVICO', ''))
        icon_url = st.text_input("URL do Ícone", value=convenio_data.get('ICON_URL', ''))
        imagem_url = st.text_input("URL da Imagem", value=convenio_data.get('IMAGEM_URL', ''))
        destaque = st.checkbox("Destaque?", value=bool(convenio_data.get('DESTAQUE', 0)))
        status = st.selectbox("Status", ["ATIVO", "INATIVO"], index=0 if convenio_data.get('STATUS', 'ATIVO') == 'ATIVO' else 1)
        
        uploaded_file = st.file_uploader("Ou faça upload de uma nova imagem", type=['png', 'jpg', 'jpeg'])

        submitted = st.form_submit_button("Salvar")

        if submitted:
            if uploaded_file is not None:
                imagem_url = save_uploaded_file(uploaded_file, "convenios")

            new_data = {
                '"NOME_CONVENIO"': nome,
                '"DESCRICAO"': descricao,
                '"TIPO_SERVICO"': categoria,
                '"ICON_URL"': icon_url,
                '"IMAGEM_URL"': imagem_url,
                '"DESTAQUE"': 1 if destaque else 0,
                '"STATUS"': status
            }

            if selected_id == 'new':
                insert_record('convenios', new_data)
                st.success("Convênio adicionado com sucesso!")
            else:
                update_record('convenios', new_data, {'"CONVENIO_ID"': selected_id})
                st.success("Convênio atualizado com sucesso!")
            
            st.rerun()

    st.subheader("Excluir Convênio")
    convenio_to_delete = st.selectbox("Selecione o convênio para excluir", options=list(convenio_options.keys())[:-1], format_func=lambda x: convenio_options[x], key="delete_convenio")
    if st.button("Excluir Convênio"):
        if convenio_to_delete:
            delete_record('convenios', {'"CONVENIO_ID"': convenio_to_delete})
            st.success("Convênio excluído com sucesso!")
            st.rerun()

def gerenciar_noticias():
    st.subheader("Gerenciamento de Notícias")
    df_noticias = carregar_dados_db('noticias')

    st.dataframe(df_noticias)

    st.subheader("Adicionar/Editar Notícia")

    noticia_options = {row['ID']: row['TITULO'] for index, row in df_noticias.iterrows()}
    noticia_options['new'] = 'Adicionar Nova'
    selected_id = st.selectbox("Selecione uma notícia para editar ou adicione uma nova", options=list(noticia_options.keys()), format_func=lambda x: noticia_options[x])

    noticia_data = {}
    if selected_id != 'new':
        noticia_data = df_noticias[df_noticias['ID'] == selected_id].iloc[0].to_dict()

    with st.form("noticia_form", clear_on_submit=True):
        titulo = st.text_input("Título", value=noticia_data.get('TITULO', ''))
        conteudo = st_quill(value=noticia_data.get('CONTEUDO', ''), placeholder="Conteúdo da notícia...")
        imagem_url = st.text_input("URL da Imagem", value=noticia_data.get('IMAGEM_URL', ''))
        destaque = st.checkbox("Destaque?", value=bool(noticia_data.get('DESTAQUE', 0)))
        status = st.selectbox("Status", ["ATIVO", "INATIVO"], index=0 if noticia_data.get('STATUS', 'ATIVO') == 'ATIVO' else 1)
        tags = st.text_input("Tags", value=noticia_data.get('TAGS', ''))
        
        uploaded_file = st.file_uploader("Ou faça upload de uma nova imagem", type=['png', 'jpg', 'jpeg'])

        submitted = st.form_submit_button("Salvar")

        if submitted:
            if uploaded_file is not None:
                imagem_url = save_uploaded_file(uploaded_file, "noticias")

            new_data = {
                '"TITULO"': titulo,
                '"CONTEUDO"': conteudo,
                '"IMAGEM_URL"': imagem_url,
                '"DESTAQUE"': 1 if destaque else 0,
                '"STATUS"': status,
                '"DATA"': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                '"TAGS"': tags
            }

            if selected_id == 'new':
                insert_record('noticias', new_data)
                st.success("Notícia adicionada com sucesso!")
            else:
                update_record('noticias', new_data, {'"ID"': selected_id})
                st.success("Notícia atualizada com sucesso!")
            
            st.rerun()

    st.subheader("Excluir Notícia")
    noticia_to_delete = st.selectbox("Selecione a notícia para excluir", options=list(noticia_options.keys())[:-1], format_func=lambda x: noticia_options[x], key="delete_noticia")
    if st.button("Excluir Notícia"):
        if noticia_to_delete:
            delete_record('noticias', {'"ID"': noticia_to_delete})
            st.success("Notícia excluída com sucesso!")
            st.rerun()

def gerenciar_eventos():
    st.subheader("Gerenciamento de Eventos")
    df_eventos = carregar_dados_db('eventos')

    st.dataframe(df_eventos)

    st.subheader("Adicionar/Editar Evento")

    evento_options = {row['EVENTO_ID']: row['TITULO'] for index, row in df_eventos.iterrows()}
    evento_options['new'] = 'Adicionar Novo'
    selected_id = st.selectbox("Selecione um evento para editar ou adicione um novo", options=list(evento_options.keys()), format_func=lambda x: evento_options[x])

    evento_data = {}
    if selected_id != 'new':
        evento_data = df_eventos[df_eventos['EVENTO_ID'] == selected_id].iloc[0].to_dict()

    with st.form("evento_form", clear_on_submit=True):
        titulo = st.text_input("Título do Evento", value=evento_data.get('TITULO', ''))
        descricao = st_quill(value=evento_data.get('DESCRICAO', ''), placeholder="Descrição do evento...")
        data_evento = st.date_input("Data do Evento", value=pd.to_datetime(evento_data.get('DATA_EVENTO'))) if 'DATA_EVENTO' in evento_data else st.date_input("Data do Evento")
        hora_evento = st.text_input("Hora do Evento", value=evento_data.get('HORA_EVENTO', ''))
        local = st.text_input("Local", value=evento_data.get('LOCAL', ''))
        imagem_url = st.text_input("URL da Imagem", value=evento_data.get('IMAGEM_URL', ''))
        status = st.selectbox("Status", ["ATIVO", "INATIVO"], index=0 if evento_data.get('STATUS', 'ATIVO') == 'ATIVO' else 1)
        
        uploaded_file = st.file_uploader("Ou faça upload de uma nova imagem", type=['png', 'jpg', 'jpeg'])

        submitted = st.form_submit_button("Salvar")

        if submitted:
            if uploaded_file is not None:
                imagem_url = save_uploaded_file(uploaded_file, "eventos")

            new_data = {
                '"TITULO"': titulo,
                '"DESCRICAO"': descricao,
                '"DATA_EVENTO"': data_evento.strftime("%Y-%m-%d"),
                '"HORA_EVENTO"': hora_evento,
                '"LOCAL"': local,
                '"IMAGEM_URL"': imagem_url,
                '"STATUS"': status
            }

            if selected_id == 'new':
                insert_record('eventos', new_data)
                st.success("Evento adicionado com sucesso!")
            else:
                update_record('eventos', new_data, {'"EVENTO_ID"': selected_id})
                st.success("Evento atualizado com sucesso!")
            
            st.rerun()

    st.subheader("Excluir Evento")
    evento_to_delete = st.selectbox("Selecione o evento para excluir", options=list(evento_options.keys())[:-1], format_func=lambda x: evento_options[x], key="delete_evento")
    if st.button("Excluir Evento"):
        if evento_to_delete:
            delete_record('eventos', {'"EVENTO_ID"': evento_to_delete})
            st.success("Evento excluído com sucesso!")
            st.rerun()

def gerenciar_financas():
    st.subheader("Gerenciamento Financeiro")

    df_usuarios = carregar_dados_db('usuarios')
    df_servicos = carregar_dados_db('servicos')
    df_financas = carregar_dados_db('financas')

    total_por_status = df_financas.groupby('STATUS')['VALOR'].sum().reindex(["PENDENTE", "PAGO", "VENCIDO"]).fillna(0)
    
    st.markdown("""
    <style>
    .metric-container {
        border: 2px solid #ccc;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .metric-container .stMetric-label {
        font-weight: bold;
    }
    .metric-container .stMetric-value {
        font-size: 24px;
    }
    .metric-container.pending { border-color: #ffc107; }
    .metric-container.paid { border-color: #28a745; }
    .metric-container.overdue { border-color: #dc3545; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-container pending"><b>Total Pendente</b><br><span class="stMetric-value">R$ {total_por_status['PENDENTE']:.2f}</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-container paid"><b>Total Pago</b><br><span class="stMetric-value">R$ {total_por_status['PAGO']:.2f}</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-container overdue"><b>Total Vencido</b><br><span class="stMetric-value">R$ {total_por_status['VENCIDO']:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Adicionar Novas Cobranças")
    with st.expander("Adicionar Novo Registro Financeiro"):
        with st.form("form_add_financa", clear_on_submit=True):
            
            user_options = {row['ID']: row['NOME'] for index, row in df_usuarios.iterrows()}
            if not user_options:
                st.warning("Nenhum usuário cadastrado. Adicione usuários antes de criar registros financeiros.")
                return

            selected_user_id = st.selectbox("Selecione o Usuário", options=list(user_options.keys()), format_func=lambda x: user_options[x])

            servico_contratado = ""
            valor = 0.0

            if selected_user_id:
                selected_user = df_usuarios[df_usuarios['ID'] == selected_user_id].iloc[0]
                servico_contratado = selected_user.get('SERVICO_ESCOLHIDO', '')
                
                if servico_contratado:
                    servico_info_row = df_servicos[df_servicos['TIPO_SERVICO'] == servico_contratado.split(' - ')[0]]
                    if not servico_info_row.empty:
                        valor = servico_info_row.iloc[0].get('VALOR_MENSAL', 0.0)

            servico_contratado_input = st.text_input("Serviço Contratado", value=servico_contratado)
            valor_input = st.number_input("Valor", min_value=0.0, value=float(valor), format="%.2f")
            data_vencimento = st.date_input("Data de Vencimento")
            status = st.selectbox("Status", ["PENDENTE", "PAGO", "VENCIDO"])
            submit_button = st.form_submit_button("Adicionar Registro")

            if submit_button:
                max_id = get_max_id('financas', '"COBRANCA_ID"')
                new_id = int(max_id) + 1 if max_id else 1
                
                novo_registro = {
                    '"COBRANCA_ID"': new_id,
                    '"USER_ID"': selected_user_id,
                    '"SERVICO_CONTRATADO"': servico_contratado_input,
                    '"VALOR"': valor_input,
                    '"DATA_EMISSAO"': pd.to_datetime("today").strftime('%Y-%m-%d'),
                    '"DATA_VENCIMENTO"': data_vencimento.strftime('%Y-%m-%d'),
                    '"STATUS"': status
                }
                if insert_record('financas', novo_registro):
                    st.success("Registro financeiro adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao adicionar registro financeiro.")
    
    st.subheader("Atualizar Status de Cobranças Existentes e Excluir Registros Financeiros")
    if df_financas.empty:
        st.info("Nenhum registro financeiro encontrado.")
        return  
    with st.form("form_update_financa"):
        financa_options = {row['COBRANCA_ID']: f"ID {row['COBRANCA_ID']} - Usuário {row['USER_ID']} - Valor R$ {row['VALOR']:.2f} - Status {row['STATUS']}" for index, row in df_financas.iterrows()}
        selected_financa_id = st.selectbox("Selecione o Registro Financeiro", options=list(financa_options.keys()), format_func=lambda x: financa_options[x])

        if selected_financa_id:
            selected_financa = df_financas[df_financas['COBRANCA_ID'] == selected_financa_id].iloc[0]
            new_status = st.selectbox("Atualizar Status", ["PENDENTE", "PAGO", "VENCIDO"], index=["PENDENTE", "PAGO", "VENCIDO"].index(selected_financa['STATUS']))
            update_button = st.form_submit_button("Atualizar Status")
            delete_button = st.form_submit_button("Excluir Registro")

            if update_button:
                if update_record('financas', {'"STATUS"': new_status}, {'"COBRANCA_ID"': selected_financa_id}):
                    st.success("Status atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao atualizar status.")

            if delete_button:
                if delete_record('financas', {'"COBRANCA_ID"': selected_financa_id}):
                    st.success("Registro financeiro excluído com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao excluir registro financeiro.")    

    st.markdown("---")
    st.subheader("Registros Financeiros")
    st.dataframe(df_financas)

def gerenciar_parceiros():
    st.subheader("Gerenciamento de Parceiros")
    df_parceiros = carregar_dados_db('parceiros')

    st.dataframe(df_parceiros)

    st.subheader("Adicionar/Editar Parceiro")

    parceiro_options = {row['PARCEIRO_ID']: row['NOME_PARCEIRO'] for index, row in df_parceiros.iterrows()}
    parceiro_options['new'] = 'Adicionar Novo'
    selected_id = st.selectbox("Selecione um parceiro para editar ou adicione um novo", options=list(parceiro_options.keys()), format_func=lambda x: parceiro_options[x])

    parceiro_data = {}
    if selected_id != 'new':
        parceiro_data = df_parceiros[df_parceiros['PARCEIRO_ID'] == selected_id].iloc[0].to_dict()

    with st.form("parceiro_form", clear_on_submit=True):
        nome = st.text_input("Nome do Parceiro", value=parceiro_data.get('NOME_PARCEIRO', ''))
        contato_nome = st.text_input("Nome do Contato", value=parceiro_data.get('CONTATO_NOME', ''))
        email = st.text_input("Email", value=parceiro_data.get('EMAIL', ''))
        telefone = st.text_input("Telefone", value=parceiro_data.get('TELEFONE', ''))
        detalhes = st_quill(value=parceiro_data.get('DETALHES', ''), placeholder="Detalhes do parceiro...")
        status = st.selectbox("Status", ["ATIVO", "INATIVO"], index=0 if parceiro_data.get('STATUS', 'ATIVO') == 'ATIVO' else 1)
        
        submitted = st.form_submit_button("Salvar")

        if submitted:
            new_data = {
                '"NOME_PARCEIRO"': nome,
                '"CONTATO_NOME"': contato_nome,
                '"EMAIL"': email,
                '"TELEFONE"': telefone,
                '"DETALHES"': detalhes,
                '"STATUS"': status
            }

            if selected_id == 'new':
                insert_record('parceiros', new_data)
                st.success("Parceiro adicionado com sucesso!")
            else:
                update_record('parceiros', new_data, {'"PARCEIRO_ID"': selected_id})
                st.success("Parceiro atualizado com sucesso!")
            
            st.rerun()

    st.subheader("Excluir Parceiro")
    parceiro_to_delete = st.selectbox("Selecione o parceiro para excluir", options=list(parceiro_options.keys())[:-1], format_func=lambda x: parceiro_options[x], key="delete_parceiro")
    if st.button("Excluir Parceiro"):
        if parceiro_to_delete:
            delete_record('parceiros', {'"PARCEIRO_ID"': parceiro_to_delete})
            st.success("Parceiro excluído com sucesso!")
            st.rerun()

def gerenciar_servicos():
    st.subheader("Gerenciamento de Serviços")
    df_servicos = carregar_dados_db('servicos')

    st.dataframe(df_servicos)

    st.subheader("Adicionar/Editar Serviço")

    servico_options = {row['SERVICO_ID']: row['TIPO_SERVICO'] for index, row in df_servicos.iterrows()}
    servico_options['new'] = 'Adicionar Novo'
    selected_id = st.selectbox("Selecione um serviço para editar ou adicione um novo", options=list(servico_options.keys()), format_func=lambda x: servico_options[x])

    servico_data = {}
    if selected_id != 'new':
        servico_data = df_servicos[df_servicos['SERVICO_ID'] == selected_id].iloc[0].to_dict()

    with st.form("servico_form", clear_on_submit=True):
        tipo_servico = st.text_input("Tipo de Serviço", value=servico_data.get('TIPO_SERVICO', ''))
        descricao = st_quill(value=servico_data.get('DESCRICAO_SERVICO', ''), placeholder="Descrição do serviço...")
        valor_mensal = st.number_input("Valor Mensal", value=servico_data.get('VALOR_MENSAL', 0.0))
        
        submitted = st.form_submit_button("Salvar")

        if submitted:
            new_data = {
                '"TIPO_SERVICO"': tipo_servico,
                '"DESCRICAO_SERVICO"': descricao,
                '"VALOR_MENSAL"': valor_mensal
            }

            if selected_id == 'new':
                insert_record('servicos', new_data)
                st.success("Serviço adicionado com sucesso!")
            else:
                update_record('servicos', new_data, {'"SERVICO_ID"': selected_id})
                st.success("Serviço atualizado com sucesso!")
            
            st.rerun()

    st.subheader("Excluir Serviço")
    servico_to_delete = st.selectbox("Selecione o serviço para excluir", options=list(servico_options.keys())[:-1], format_func=lambda x: servico_options[x], key="delete_servico")
    if st.button("Excluir Serviço"):
        if servico_to_delete:
            delete_record('servicos', {'"SERVICO_ID"': servico_to_delete})
            st.success("Serviço excluído com sucesso!")
            st.rerun()

def gerenciar_beneficios():
    st.subheader("Gerenciamento de Benefícios")
    df_beneficios = carregar_dados_db('beneficios')

    st.dataframe(df_beneficios)

    st.subheader("Adicionar/Editar Benefício")

    beneficio_options = {row['BENEFICIO_ID']: row['TITULO'] for index, row in df_beneficios.iterrows()}
    beneficio_options['new'] = 'Adicionar Novo'
    selected_id = st.selectbox("Selecione um benefício para editar ou adicione um novo", options=list(beneficio_options.keys()), format_func=lambda x: beneficio_options[x])

    beneficio_data = {}
    if selected_id != 'new':
        beneficio_data = df_beneficios[df_beneficios['BENEFICIO_ID'] == selected_id].iloc[0].to_dict()

    with st.form("beneficio_form", clear_on_submit=True):
        titulo = st.text_input("Título do Benefício", value=beneficio_data.get('TITULO', ''))
        descricao = st_quill(value=beneficio_data.get('DESCRICAO_BENEFICIO', ''), placeholder="Descrição do benefício...")
        icone = st.text_input("Ícone", value=beneficio_data.get('ICONE', ''))
        
        submitted = st.form_submit_button("Salvar")

        if submitted:
            new_data = {
                '"TITULO"': titulo,
                '"DESCRICAO_BENEFICIO"': descricao,
                '"ICONE"': icone
            }

            if selected_id == 'new':
                insert_record('beneficios', new_data)
                st.success("Benefício adicionado com sucesso!")
            else:
                update_record('beneficios', new_data, {'"BENEFICIO_ID"': selected_id})
                st.success("Benefício atualizado com sucesso!")
            
            st.rerun()

    st.subheader("Excluir Benefício")
    beneficio_to_delete = st.selectbox("Selecione o benefício para excluir", options=list(beneficio_options.keys())[:-1], format_func=lambda x: beneficio_options[x], key="delete_beneficio")
    if st.button("Excluir Benefício"):
        if beneficio_to_delete:
            delete_record('beneficios', {'"BENEFICIO_ID"': beneficio_to_delete})
            st.success("Benefício excluído com sucesso!")
            st.rerun()

def gerenciar_comentarios():
    st.subheader("Gerenciamento de Comentários")
    st.info("A estrutura da tabela 'comentarios' parece estar corrompida ou inconsistente. A funcionalidade de gerenciamento de comentários está desativada para prevenir mais problemas.")

def gerenciar_contatos():
    st.subheader("Gerenciamento de Contatos")
    df_contatos = carregar_dados_db('contatos')

    if df_contatos.empty:
        st.info("Nenhuma mensagem de contato.")
        return

    st.dataframe(df_contatos)

    st.subheader("Moderar Contato")
    contato_id = st.selectbox("Selecione o ID do contato", df_contatos['ID'])
    novo_status = st.selectbox("Selecione o novo status", ['NOVO', 'LIDO', 'RESPONDIDO'])
    
    if st.button("Atualizar Status do Contato"):
        update_record('contatos', {'"STATUS_ATENDIMENTO"': novo_status}, {'"ID"': contato_id})
        st.success("Status do contato atualizado.")
        st.rerun()

    if st.button("Excluir Contato Permanentemente"):
        delete_record('contatos', {'"ID"': contato_id})
        st.success("Contato excluído.")
        st.rerun()

def gerenciar_log_atividades():
    st.subheader("Log de Atividades")
    st.info("A estrutura da tabela 'log_atividades' parece estar corrompida ou inconsistente. A funcionalidade de visualização de logs está desativada.")

# --- CONTROLE PRINCIPAL DA PÁGINA ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if st.session_state.admin_logged_in:
    pagina_admin()
else:
    pagina_login_admin()