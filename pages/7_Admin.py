import streamlit as st
import pandas as pd
import os
from auth import verify_password, hash_password
from file_utils import save_uploaded_file
from streamlit_quill import st_quill
import matplotlib.pyplot as plt

st.set_page_config(page_title="Área do Administrador", layout="wide")

# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---
def carregar_dados(filepath):
    """Carrega um arquivo CSV, se existir."""
    return pd.read_csv(filepath) if os.path.exists(filepath) else pd.DataFrame()

def salvar_dados(df, filepath):
    """Salva um DataFrame em um arquivo CSV."""
    df.to_csv(filepath, index=False)

# --- PÁGINA DE LOGIN DO ADMIN ---
def pagina_login_admin():
    st.header("Login do Administrador")
    with st.form("admin_login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            df_usuarios = carregar_dados('data/usuarios.csv')
            if df_usuarios.empty:
                st.error("Nenhum usuário cadastrado.")
                return

            admin_user = df_usuarios[(df_usuarios['EMAIL'].str.lower() == email.lower()) & (df_usuarios['NIVEL_ACESSO'] == 'ADMIN')]
            
            if not admin_user.empty:
                user_data = admin_user.iloc[0]
                if verify_password(senha, user_data['SENHA_HASH']):
                    st.session_state['admin_logged_in'] = True
                    st.session_state['admin_info'] = user_data.to_dict()
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
    df_usuarios = carregar_dados('data/usuarios.csv')

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
    df_usuarios['DATA_CADASTRO'] = pd.to_datetime(df_usuarios['DATA_CADASTRO'])
    cadastros_por_dia = df_usuarios.set_index('DATA_CADASTRO').resample('D').size()
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
                    df_usuarios.loc[df_usuarios['ID'] == row['ID'], 'STATUS'] = 'ATIVO'
                    salvar_dados(df_usuarios, 'data/usuarios.csv')
                    st.success(f"Usuário {row['NOME']} aprovado com sucesso!")
                    st.rerun()

    st.divider()

    # Seção de Gerenciamento e Visualização Detalhada de Usuários
    st.subheader("Gerenciamento e Visualização Detalhada de Usuários")

    if df_usuarios.empty:
        st.info("Nenhum usuário para gerenciar ou visualizar.")
        return

    user_options = ["Selecione um usuário"] + [f"{row['NOME']} ({row['EMAIL']})" for index, row in df_usuarios.iterrows()]
    selected_user_option = st.selectbox("Selecione um usuário:", user_options, key="select_user_for_management")

    if selected_user_option != "Selecione um usuário":
        selected_user_index = user_options.index(selected_user_option) - 1 # Adjust index because of "Selecione um usuário"
        selected_user_data = df_usuarios.iloc[selected_user_index]
        
        st.markdown(f"### Detalhes de {selected_user_data['NOME']}")
        
        # Display user details in document form
        for col in df_usuarios.columns:
            if col not in ['SENHA_HASH', 'TOKEN_RECUPERACAO', 'DATA_EXPIRACAO_TOKEN']: # Exclude sensitive/internal fields
                st.write(f"**{col.replace('_', ' ').title()}:** {selected_user_data.get(col, 'N/A')}")

        # Edit and Remove section for the selected user
        st.divider()
        st.subheader("Editar/Remover Usuário Selecionado")

        with st.form(f"form_edit_user_{selected_user_data['ID']}"):
            col1, col2 = st.columns(2)
            with col1:
                new_status = st.selectbox(
                    "Status",
                    ["ATIVO", "INATIVO", "PENDENTE"],
                    index=["ATIVO", "INATIVO", "PENDENTE"].index(selected_user_data['STATUS']),
                    key=f"status_edit_{selected_user_data['ID']}"
                )
            with col2:
                new_nivel = st.selectbox(
                    "Nível",
                    ["MEMBRO", "ADMIN"],
                    index=["MEMBRO", "ADMIN"].index(selected_user_data['NIVEL_ACESSO']),
                    key=f"nivel_edit_{selected_user_data['ID']}"
                )
            
            col_save, col_delete = st.columns(2)
            with col_save:
                if st.form_submit_button("Salvar Alterações"):
                    df_usuarios.loc[selected_user_data.name, 'STATUS'] = new_status
                    df_usuarios.loc[selected_user_data.name, 'NIVEL_ACESSO'] = new_nivel
                    salvar_dados(df_usuarios, 'data/usuarios.csv')
                    st.success(f"Usuário {selected_user_data['NOME']} atualizado com sucesso!")
                    st.rerun()
            with col_delete:
                if st.form_submit_button("Remover Usuário"):
                    st.session_state.to_delete = selected_user_data.to_dict()
                    st.rerun()
        
        # Contract download for the selected user
        st.divider()
        st.subheader("Download de Contrato")
        contract_path = selected_user_data.get('CONTRATO_ASSINADO_URL')
        if isinstance(contract_path, str) and os.path.exists(contract_path):
            try:
                with open(contract_path, "rb") as f:
                    contract_bytes = f.read()
                
                file_name = os.path.basename(contract_path)
                st.download_button(
                    label=f"Baixar Contrato: {file_name}",
                    data=contract_bytes,
                    file_name=file_name,
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Erro ao carregar o contrato: {e}")
        else:
            st.info("Nenhum contrato assinado encontrado para este usuário ou o arquivo não existe.")

    st.divider()

    st.subheader("Adicionar Novo Usuário Manualmente")
    with st.form("form_add_usuario", clear_on_submit=True):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        perfil = st.selectbox("Nível de Acesso", ["MEMBRO", "ADMIN"])
        status = st.selectbox("Status", ["ATIVO", "INATIVO"])
        senha = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Adicionar Usuário")

        if submit_button:
            if not nome or not email or not senha:
                st.error("Todos os campos são obrigatórios.")
                return

            novo_usuario = {
                "ID": len(df_usuarios) + 1,
                "NOME": nome,
                "EMAIL": email,
                "NIVEL_ACESSO": perfil,
                "STATUS": status,
                "SENHA_HASH": hash_password(senha)
            }
            df_usuarios = pd.concat([df_usuarios, pd.DataFrame([novo_usuario])], ignore_index=True)
            salvar_dados(df_usuarios, 'data/usuarios.csv')
            st.success("Usuário adicionado com sucesso!")
            st.rerun()  
            
# --- GERENCIAMENTO INSTITUCIONAL ---
def gerenciar_institucional():
    st.subheader("Gerenciamento Institucional")
    df_institucional = carregar_dados('data/institucional.csv')

    if df_institucional.empty:
        st.info("Nenhum dado institucional para exibir.")
        return

    if 'to_delete' not in st.session_state:
        st.session_state.to_delete = None
    if st.session_state.to_delete:
        st.warning(f"Tem certeza que deseja remover o item {st.session_state.to_delete['TITULO_SITE']}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sim, remover"):
                df_institucional = df_institucional[df_institucional['TITULO_SITE'] != st.session_state.to_delete['TITULO_SITE']]
                salvar_dados(df_institucional, 'data/institucional.csv')
                st.success(f"Item {st.session_state.to_delete['TITULO_SITE']} removido com sucesso!")
                st.rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.to_delete = None
                st.rerun()
        return
    st.write("Selecione um item institucional para editar ou remover.")
    item_selecionado = st.selectbox("Selecionar item", df_institucional['TITULO_SITE'])

    if item_selecionado:
        st.subheader(f"Editando {item_selecionado}")
        item_data = df_institucional[df_institucional['TITULO_SITE'] == item_selecionado].iloc[0]

        with st.form("form_edit_item", clear_on_submit=True):
            logo = st.text_input("URL do Logo", value=item_data['LOGO_URL'])
            titulo = st.text_input("Título", value=item_data['TITULO_SITE'])
            cnpj_cpf = st.text_area("Conteúdo", value=item_data['CNPJ_CPF'])
            data_fundacao = st.text_area("Conteúdo", value=item_data['DATA_FUNDACAO'])
            historico = st.text_area("Conteúdo", value=item_data['HISTORICO'])
            visao = st.text_area("Conteúdo", value=item_data['VISAO'])
            missao = st.text_area("Conteúdo", value=item_data['MISSAO'])
            valores = st.text_area("Conteúdo", value=item_data['VALORES'])
            email = st.text_area("Conteúdo", value=item_data['EMAIL_CONTATO'])
            telefone = st.text_area("Conteúdo", value=item_data['TELEFONE_CONTATO'])
            endereco = st.text_area("Conteúdo", value=item_data['ENDERECO'])      
            
            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("Salvar Alterações")
            with col2:
                delete_button = st.form_submit_button("Remover Item")

            if save_button:
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'LOGO_URL'] = logo
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'TITULO_SITE'] = titulo
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'CNPJ_CPF'] = cnpj_cpf
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'DATA_FUNDACAO'] = data_fundacao
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'HISTORICO'] = historico
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'VISAO'] = visao
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'MISSAO'] = missao
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'VALORES'] = valores
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'EMAIL_CONTATO'] = email
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'TELEFONE_CONTATO'] = telefone
                df_institucional.loc[df_institucional['TITULO_SITE'] == item_selecionado, 'ENDERECO'] = endereco
                
                
                salvar_dados(df_institucional, 'data/institucional.csv')
                st.success("Item institucional atualizado com sucesso!")
                st.rerun()

            if delete_button:
                st.session_state.to_delete = item_data
                st.rerun()
    st.subheader("Adicionar Novo Item Institucional")
    with st.form("form_add_item", clear_on_submit=True):
        logo = st.text_input("URL do Logo")
        titulo = st.text_input("Título")
        conteudo = st.text_area("Conteúdo (CNPJ/CPF)")
        data_fundacao = st.text_input("Data de Fundação (DD/MM/AAAA)", value="01/01/2000")  # Data padrão, pode ser alterada    
        historico = st.text_area("Histórico")
        visao = st.text_area("Visão")
        missao = st.text_area("Missão")
        valores = st.text_area("Valores")
        email = st.text_input("Email de Contato")
        telefone = st.text_input("Telefone de Contato")
        endereco = st.text_input("Endereço")

        submit_button = st.form_submit_button("Adicionar Item")

        if submit_button:
            if not titulo or not conteudo:
                st.error("Todos os campos são obrigatórios.")
                return

            novo_item = {
                "ID": len(df_institucional) + 1,
                "LOGO_URL": "https://example.com/logo.png",  # URL padrão, pode ser alterada
                "TITULO_SITE": titulo,
                "CNPJ_CPF": conteudo,
                "DATA_FUNDACAO": "01/01/2000",  # Data padrão, pode ser alterada
                "HISTORICO": "História da instituição",
                "VISAO": "Visão da instituição",
                "MISSAO": "Missão da instituição",
                "VALORES": "Valores da instituição",
                "EMAIL_CONTATO": "",
                "TELEFONE_CONTATO": "",
                "ENDERECO": ""  # Endereço padrão, pode ser alterado
            }
            df_institucional = pd.concat([df_institucional, pd.DataFrame([novo_item])], ignore_index=True)
            salvar_dados(df_institucional, 'data/institucional.csv')
            st.success("Item institucional adicionado com sucesso!")
            st.rerun()  


    

# --- GERENCIAMENTO DE CONVÊNIOS ---
def gerenciar_convenios():
    st.subheader("Gerenciamento de Convênios")
    df_convenios = carregar_dados('data/convenios.csv')

    # Adicionar novo convênio
    with st.expander("Adicionar Novo Convênio"):
        with st.form("form_add_convenio", clear_on_submit=True):
            nome = st.text_input("Nome do Convênio", key="add_convenio_nome")
            descricao = st.text_area("Descrição", key="add_convenio_descricao")
            tipo_servico = st.text_input("Tipo de Serviço", key="add_convenio_tipo")
            status = st.selectbox("Status", ["ATIVO", "INATIVO"], key="add_convenio_status")
            destaque = st.checkbox("Destaque", key="add_convenio_destaque")
            
            uploaded_image = st.file_uploader("Imagem Principal", type=['png', 'jpg', 'jpeg'], key="add_convenio_img")
            uploaded_icon = st.file_uploader("Ícone", type=['png', 'jpg', 'jpeg'], key="add_convenio_icon")

            submit_button = st.form_submit_button("Adicionar Convênio")

            if submit_button:
                if not nome or not descricao:
                    st.error("Nome e descrição são obrigatórios.")
                    return

                imagem_url = save_uploaded_file(uploaded_image, "convenios") if uploaded_image else ""
                icon_url = save_uploaded_file(uploaded_icon, "convenios") if uploaded_icon else ""

                novo_id = (df_convenios['CONVENIO_ID'].max() + 1) if not df_convenios.empty else 1
                novo_convenio = {
                    "CONVENIO_ID": novo_id,
                    "NOME_CONVENIO": nome,
                    "DESCRICAO": descricao,
                    "TIPO_SERVICO": tipo_servico,
                    "STATUS": status,
                    "DESTAQUE": destaque,
                    "IMAGEM_URL": imagem_url,
                    "ICON_URL": icon_url
                }
                df_convenios = pd.concat([df_convenios, pd.DataFrame([novo_convenio])], ignore_index=True)
                salvar_dados(df_convenios, 'data/convenios.csv')
                st.success("Convênio adicionado com sucesso!")
                st.rerun()

    st.divider()

    # Exibir convênios existentes
    for index, row in df_convenios.iterrows():
        convenio_id = row['CONVENIO_ID']
        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            with col1:
                image_url = row.get("IMAGEM_URL")
                if isinstance(image_url, str) and os.path.exists(image_url):
                    st.image(image_url, width=150)
                icon_url = row.get("ICON_URL")
                if isinstance(icon_url, str) and os.path.exists(icon_url):
                    st.image(icon_url, width=50)
            with col2:
                st.subheader(row["NOME_CONVENIO"])
                st.write(f"**Tipo:** {row.get('TIPO_SERVICO', 'N/A')}")
                st.write(f"**Status:** {row['STATUS']}")
                st.write(row["DESCRICAO"])

            with st.expander("Editar/Remover"):
                with st.form(f"form_edit_convenio_{convenio_id}"):
                    nome = st.text_input("Nome do Convênio", value=row["NOME_CONVENIO"], key=f"convenio_nome_{convenio_id}")
                    descricao = st.text_area("Descrição", value=row["DESCRICAO"], key=f"convenio_desc_{convenio_id}")
                    tipo_servico = st.text_input("Tipo de Serviço", value=row.get("TIPO_SERVICO", ""), key=f"convenio_tipo_{convenio_id}")
                    status = st.selectbox("Status", ["ATIVO", "INATIVO"], index=["ATIVO", "INATIVO"].index(row['STATUS']), key=f"convenio_status_{convenio_id}")
                    destaque = st.checkbox("Destaque", value=row.get("DESTAQUE", False), key=f"convenio_destaque_{convenio_id}")
                    
                    new_image = st.file_uploader("Nova Imagem Principal", type=['png', 'jpg', 'jpeg'], key=f"convenio_img_{convenio_id}")
                    new_icon = st.file_uploader("Novo Ícone", type=['png', 'jpg', 'jpeg'], key=f"convenio_icon_{convenio_id}")

                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.form_submit_button("Salvar Alterações"):
                            df_convenios.loc[index, "NOME_CONVENIO"] = nome
                            df_convenios.loc[index, "DESCRICAO"] = descricao
                            df_convenios.loc[index, "TIPO_SERVICO"] = tipo_servico
                            df_convenios.loc[index, "STATUS"] = status
                            df_convenios.loc[index, "DESTAQUE"] = destaque
                            
                            if new_image:
                                df_convenios.loc[index, "IMAGEM_URL"] = save_uploaded_file(new_image, "convenios")
                            if new_icon:
                                df_convenios.loc[index, "ICON_URL"] = save_uploaded_file(new_icon, "convenios")
                                
                            salvar_dados(df_convenios, 'data/convenios.csv')
                            st.success("Convênio atualizado com sucesso!")
                            st.rerun()
                    with col_delete:
                        if st.form_submit_button("Remover"):
                            df_convenios = df_convenios.drop(index)
                            salvar_dados(df_convenios, 'data/convenios.csv')
                            st.success("Convênio removido com sucesso!")
                            st.rerun()


# --- GERENCIAMENTO DE NOTÍCIAS ---
def gerenciar_noticias():
    st.subheader("Gerenciamento de Notícias")
    df_noticias = carregar_dados('data/noticias.csv')

    # Adicionar nova notícia
    with st.expander("Adicionar Nova Notícia"):
        with st.form("form_add_noticia", clear_on_submit=True):
            titulo = st.text_input("Título")
            conteudo = st_quill(placeholder="Escreva o conteúdo da notícia aqui...", html=True)
            tags = st.text_input("Tags (separadas por vírgula)")
            status = st.selectbox("Status", ["PUBLICADO", "RASCUNHO"])
            destaque = st.checkbox("Destaque")
            
            uploaded_image = st.file_uploader("Imagem da Notícia", type=['png', 'jpg', 'jpeg'])

            submit_button = st.form_submit_button("Adicionar Notícia")

            if submit_button:
                if not titulo or not conteudo:
                    st.error("Título e conteúdo são obrigatórios.")
                    return

                imagem_url = save_uploaded_file(uploaded_image, "noticias") if uploaded_image else ""

                novo_id = (df_noticias['ID'].max() + 1) if not df_noticias.empty else 1
                nova_noticia = {
                    "ID": novo_id,
                    "TITULO": titulo,
                    "CONTEUDO": conteudo,
                    "DATA": pd.to_datetime("today").strftime('%Y-%m-%d'),
                    "IMAGEM_URL": imagem_url,
                    "DESTAQUE": destaque,
                    "STATUS": status,
                    "TAGS": tags
                }
                df_noticias = pd.concat([df_noticias, pd.DataFrame([nova_noticia])], ignore_index=True)
                salvar_dados(df_noticias, 'data/noticias.csv')
                st.success("Notícia adicionada com sucesso!")
                st.rerun()

    st.divider()

    # Selecionar notícia para editar/remover
    if not df_noticias.empty:
        noticia_selecionada_titulo = st.selectbox("Selecione uma notícia para editar ou remover", df_noticias['TITULO'])
        noticia_selecionada = df_noticias[df_noticias['TITULO'] == noticia_selecionada_titulo].iloc[0]
        index = noticia_selecionada.name

        st.subheader(f"Editando: {noticia_selecionada['TITULO']}")
        with st.form(f"form_edit_noticia_{index}"):
            titulo = st.text_input("Título", value=noticia_selecionada["TITULO"])
            
            conteudo = st_quill(value=noticia_selecionada["CONTEUDO"], html=True, key=f"editor_{index}")
            
            tags = st.text_input("Tags", value=noticia_selecionada.get("TAGS", ""))
            status = st.selectbox("Status", ["PUBLICADO", "RASCUNHO"], index=["PUBLICADO", "RASCUNHO"].index(noticia_selecionada['STATUS']))
            destaque = st.checkbox("Destaque", value=noticia_selecionada.get("DESTAQUE", False))
            
            image_url = noticia_selecionada.get("IMAGEM_URL")
            if isinstance(image_url, str) and os.path.exists(image_url):
                st.image(image_url, width=200)
            new_image = st.file_uploader("Substituir Imagem", type=['png', 'jpg', 'jpeg'])

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.form_submit_button("Salvar Alterações"):
                    df_noticias.loc[index, "TITULO"] = titulo
                    df_noticias.loc[index, "CONTEUDO"] = conteudo
                    df_noticias.loc[index, "TAGS"] = tags
                    df_noticias.loc[index, "STATUS"] = status
                    df_noticias.loc[index, "DESTAQUE"] = destaque
                    
                    if new_image:
                        df_noticias.loc[index, "IMAGEM_URL"] = save_uploaded_file(new_image, "noticias")
                        
                    salvar_dados(df_noticias, 'data/noticias.csv')
                    st.success("Notícia atualizada com sucesso!")
                    st.rerun()
            with col_delete:
                if st.form_submit_button("Remover"):
                    df_noticias = df_noticias.drop(index)
                    salvar_dados(df_noticias, 'data/noticias.csv')
                    st.success("Notícia removida com sucesso!")
                    st.rerun()

# --- GERENCIAMENTO DE EVENTOS ---
def gerenciar_eventos():
    st.subheader("Gerenciamento de Eventos")
    df_eventos = carregar_dados('data/eventos.csv')

    # Adicionar novo evento
    with st.expander("Adicionar Novo Evento"):
        with st.form("form_add_evento", clear_on_submit=True):
            titulo = st.text_input("Título do Evento")
            descricao = st_quill(placeholder="Escreva a descrição do evento aqui...", html=True)
            data = st.date_input("Data do Evento")
            hora = st.time_input("Hora do Evento")
            local = st.text_input("Local do Evento")
            status = st.selectbox("Status", ["AGENDADO", "REALIZADO", "CANCELADO"])
            
            uploaded_image = st.file_uploader("Imagem do Evento", type=['png', 'jpg', 'jpeg'])

            submit_button = st.form_submit_button("Adicionar Evento")

            if submit_button:
                if not titulo or not descricao:
                    st.error("Título and descrição são obrigatórios.")
                    return

                imagem_url = save_uploaded_file(uploaded_image, "eventos") if uploaded_image else ""

                novo_id = (df_eventos['EVENTO_ID'].max() + 1) if not df_eventos.empty else 1
                novo_evento = {
                    "EVENTO_ID": novo_id,
                    "TITULO": titulo,
                    "DESCRICAO": descricao,
                    "DATA_EVENTO": data.strftime('%Y-%m-%d'),
                    "HORA_EVENTO": hora.strftime('%H:%M'),
                    "LOCAL": local,
                    "IMAGEM_URL": imagem_url,
                    "STATUS": status
                }
                df_eventos = pd.concat([df_eventos, pd.DataFrame([novo_evento])], ignore_index=True)
                salvar_dados(df_eventos, 'data/eventos.csv')
                st.success("Evento adicionado com sucesso!")
                st.rerun()

    st.divider()

    # Selecionar evento para editar/remover
    if not df_eventos.empty:
        evento_selecionado_titulo = st.selectbox("Selecione um evento para editar ou remover", df_eventos['TITULO'])
        evento_selecionado = df_eventos[df_eventos['TITULO'] == evento_selecionado_titulo].iloc[0]
        index = evento_selecionado.name

        st.subheader(f"Editando: {evento_selecionado['TITULO']}")
        with st.form(f"form_edit_evento_{index}"):
            titulo = st.text_input("Título", value=evento_selecionado["TITULO"])
            
            servico_contratado = st_quill(value=evento_selecionado["DESCRICAO"], html=True, key=f"editor_evento_{index}")
            
            data = st.date_input("Data do Evento", value=pd.to_datetime(evento_selecionado['DATA_EVENTO']))
            hora = st.time_input("Hora do Evento", value=pd.to_datetime(evento_selecionado['HORA_EVENTO']).time())
            local = st.text_input("Local", value=evento_selecionado.get("LOCAL", ""))
            status = st.selectbox("Status", ["AGENDADO", "REALIZADO", "CANCELADO"], index=["AGENDADO", "REALIZADO", "CANCELADO"].index(evento_selecionado['STATUS']))
            
            image_url = evento_selecionado.get("IMAGEM_URL")
            if isinstance(image_url, str) and os.path.exists(image_url):
                st.image(image_url, width=200)
            new_image = st.file_uploader("Substituir Imagem", type=['png', 'jpg', 'jpeg'])

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.form_submit_button("Salvar Alterações"):
                    df_eventos.loc[index, "TITULO"] = titulo
                    df_eventos.loc[index, "SERVICO_CONTRATADO"] = servico_contratado
                    df_eventos.loc[index, "DATA_EVENTO"] = data.strftime('%Y-%m-%d')
                    df_eventos.loc[index, "HORA_EVENTO"] = hora.strftime('%H:%M')
                    df_eventos.loc[index, "LOCAL"] = local
                    df_eventos.loc[index, "STATUS"] = status
                    
                    if new_image:
                        df_eventos.loc[index, "IMAGEM_URL"] = save_uploaded_file(new_image, "eventos")
                        
                    salvar_dados(df_eventos, 'data/eventos.csv')
                    st.success("Evento atualizado com sucesso!")
                    st.rerun()
            with col_delete:
                if st.form_submit_button("Remover"):
                    df_eventos = df_eventos.drop(index)
                    salvar_dados(df_eventos, 'data/eventos.csv')
                    st.success("Evento removido com sucesso!")
                    st.rerun()

# --- GERENCIAMENTO FINANCEIRO ---
def gerenciar_financas():
    st.subheader("Gerenciamento Financeiro")
    df_financas = carregar_dados('data/financas.csv')

    if df_financas.empty:
        st.info("Nenhum registro financeiro para exibir.")
        return

    # Gráficos
    st.subheader("Visão Geral Financeira")
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

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.pie(total_por_status, labels=total_por_status.index, autopct='%1.1f%%', startangle=90, colors=['#ffc107', '#28a745', '#dc3545'])
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

    st.divider()

    # Adicionar novo registro
    with st.expander("Adicionar Novo Registro Financeiro"):
        with st.form("form_add_financa", clear_on_submit=True):
            user_id = st.number_input("ID do Usuário", min_value=1, step=1)
            servico_contratado = st.text_input("Serviço Contratado")
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")
            data_vencimento = st.date_input("Data de Vencimento")
            status = st.selectbox("Status", ["PENDENTE", "PAGO", "VENCIDO"])
            submit_button = st.form_submit_button("Adicionar Registro")

            if submit_button:
                novo_registro = {
                    "COBRANCA_ID": len(df_financas) + 1,
                    "USER_ID": user_id,
                    "SERVICO_CONTRATADO": servico_contratado,
                    "VALOR": valor,
                    "DATA_EMISSAO": pd.to_datetime("today").strftime('%Y-%m-%d'),
                    "DATA_VENCIMENTO": data_vencimento.strftime('%Y-%m-%d'),
                    "STATUS": status
                }
                df_financas = pd.concat([df_financas, pd.DataFrame([novo_registro])], ignore_index=True)
                salvar_dados(df_financas, 'data/financas.csv')
                st.success("Registro financeiro adicionado com sucesso!")
                st.rerun()

    st.divider()

    # Exibir registros por status
    for status_option in ["PENDENTE", "PAGO", "VENCIDO"]:
        with st.expander(f"{status_option}s"):
            df_status = df_financas[df_financas['STATUS'] == status_option]
            if df_status.empty:
                st.write("Nenhum registro encontrado.")
                continue

            for index, row in df_status.iterrows():
                st.write(f"**ID:** {row['COBRANCA_ID']} | **Usuário ID:** {row['USER_ID']} | **Serviço Contratado:** {row['SERVICO_CONTRATADO']}")
                with st.form(f"form_edit_financa_{index}"):
                    user_id = st.number_input("ID do Usuário", min_value=1, step=1, value=row['USER_ID'], key=f"user_id_{index}")
                    servico_contratado = st.text_input("Serviço Contratado", value=row['SERVICO_CONTRATADO'], key=f"desc_financa_{index}")
                    valor = st.number_input("Valor", min_value=0.0, format="%.2f", value=row['VALOR'], key=f"valor_{index}")
                    data_vencimento = st.date_input("Data de Vencimento", value=pd.to_datetime(row['DATA_VENCIMENTO']), key=f"vencimento_{index}")
                    status = st.selectbox("Status", ["PENDENTE", "PAGO", "VENCIDO"], index=["PENDENTE", "PAGO", "VENCIDO"].index(row['STATUS']), key=f"status_financa_{index}")
                    
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.form_submit_button("Salvar Alterações"):
                            df_financas.loc[index, 'USER_ID'] = user_id
                            df_financas.loc[index, 'SERVICO_CONTRATADO'] = servico_contratado
                            df_financas.loc[index, 'VALOR'] = valor
                            df_financas.loc[index, 'DATA_VENCIMENTO'] = data_vencimento.strftime('%Y-%m-%d')
                            df_financas.loc[index, 'STATUS'] = status
                            salvar_dados(df_financas, 'data/financas.csv')
                            st.success("Registro atualizado com sucesso!")
                            st.rerun()
                    with col_delete:
                        if st.form_submit_button("Remover"):
                            df_financas = df_financas.drop(index)
                            salvar_dados(df_financas, 'data/financas.csv')
                            st.success("Registro removido com sucesso!")
                            st.rerun()

# --- GERENCIAMENTO DE PARCEIROS ---
def gerenciar_parceiros():
    st.subheader("Gerenciamento de Parceiros")
    df_parceiros = carregar_dados('data/parceiros.csv')

    # Adicionar novo parceiro
    with st.expander("Adicionar Novo Parceiro"):
        with st.form("form_add_parceiro", clear_on_submit=True):
            nome = st.text_input("Nome do Parceiro")
            contato_nome = st.text_input("Nome do Contato")
            email = st.text_input("Email")
            telefone = st.text_input("Telefone")
            convenio_id = st.number_input("ID do Convênio", min_value=1, step=1)
            detalhes = st.text_area("Detalhes")
            status = st.selectbox("Status", ["ATIVO", "INATIVO"])
            endereco = st.text_input("Endereço")
            website = st.text_input("Website")
            redes_sociais = st.text_input("Redes Sociais")
            
            uploaded_image = st.file_uploader("Imagem Principal", type=['png', 'jpg', 'jpeg'])
            uploaded_icon = st.file_uploader("Ícone", type=['png', 'jpg', 'jpeg'])

            submit_button = st.form_submit_button("Adicionar Parceiro")

            if submit_button:
                if not nome:
                    st.error("Nome do parceiro é obrigatório.")
                    return

                imagem_url = save_uploaded_file(uploaded_image, "parceiros") if uploaded_image else ""
                icon_url = save_uploaded_file(uploaded_icon, "parceiros") if uploaded_icon else ""

                novo_id = (df_parceiros['PARCEIRO_ID'].max() + 1) if not df_parceiros.empty else 1
                novo_parceiro = {
                    "PARCEIRO_ID": novo_id,
                    "NOME_PARCEIRO": nome,
                    "CONTATO_NOME": contato_nome,
                    "EMAIL": email,
                    "TELEFONE": telefone,
                    "CONVENIO_ID": convenio_id,
                    "DETALHES": detalhes,
                    "STATUS": status,
                    "ENDERECO": endereco,
                    "WEBSITE": website,
                    "REDES_SOCIAIS": redes_sociais,
                    "IMAGEM_URL": imagem_url,
                    "ICON_URL": icon_url
                }
                df_parceiros = pd.concat([df_parceiros, pd.DataFrame([novo_parceiro])], ignore_index=True)
                salvar_dados(df_parceiros, 'data/parceiros.csv')
                st.success("Parceiro adicionado com sucesso!")
                st.rerun()

    st.divider()

    # Selecionar parceiro para editar/remover
    if not df_parceiros.empty:
        parceiro_selecionado_nome = st.selectbox("Selecione um parceiro para editar ou remover", df_parceiros['NOME_PARCEIRO'])
        parceiro_selecionado = df_parceiros[df_parceiros['NOME_PARCEIRO'] == parceiro_selecionado_nome].iloc[0]
        index = parceiro_selecionado.name

        st.subheader(f"Editando: {parceiro_selecionado['NOME_PARCEIRO']}")
        with st.form(f"form_edit_parceiro_{index}"):
            nome = st.text_input("Nome do Parceiro", value=parceiro_selecionado["NOME_PARCEIRO"])
            contato_nome = st.text_input("Nome do Contato", value=parceiro_selecionado.get("CONTATO_NOME", ""))
            email = st.text_input("Email", value=parceiro_selecionado.get("EMAIL", ""))
            telefone = st.text_input("Telefone", value=parceiro_selecionado.get("TELEFONE", ""))
            convenio_id = st.number_input("ID do Convênio", min_value=1, step=1, value=parceiro_selecionado.get("CONVENIO_ID", 0))
            detalhes = st.text_area("Detalhes", value=parceiro_selecionado.get("DETALHES", ""))
            status = st.selectbox("Status", ["ATIVO", "INATIVO"], index=["ATIVO", "INATIVO"].index(parceiro_selecionado['STATUS']))
            endereco = st.text_input("Endereço", value=parceiro_selecionado.get("ENDERECO", ""))
            website = st.text_input("Website", value=parceiro_selecionado.get("WEBSITE", ""))
            redes_sociais = st.text_input("Redes Sociais", value=parceiro_selecionado.get("REDES_SOCIAIS", ""))
            
            image_url = parceiro_selecionado.get("IMAGEM_URL")
            if isinstance(image_url, str) and os.path.exists(image_url):
                st.image(image_url, width=200)
            new_image = st.file_uploader("Substituir Imagem Principal", type=['png', 'jpg', 'jpeg'])

            icon_url = parceiro_selecionado.get("ICON_URL")
            if isinstance(icon_url, str) and os.path.exists(icon_url):
                st.image(icon_url, width=50)
            new_icon = st.file_uploader("Substituir Ícone", type=['png', 'jpg', 'jpeg'])

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.form_submit_button("Salvar Alterações"):
                    df_parceiros.loc[index, "NOME_PARCEIRO"] = nome
                    df_parceiros.loc[index, "CONTATO_NOME"] = contato_nome
                    df_parceiros.loc[index, "EMAIL"] = email
                    df_parceiros.loc[index, "TELEFONE"] = telefone
                    df_parceiros.loc[index, "CONVENIO_ID"] = convenio_id
                    df_parceiros.loc[index, "DETALHES"] = detalhes
                    df_parceiros.loc[index, "STATUS"] = status
                    df_parceiros.loc[index, "ENDERECO"] = endereco
                    df_parceiros.loc[index, "WEBSITE"] = website
                    df_parceiros.loc[index, "REDES_SOCIAIS"] = redes_sociais
                    
                    if new_image:
                        df_parceiros.loc[index, "IMAGEM_URL"] = save_uploaded_file(new_image, "parceiros")
                    if new_icon:
                        df_parceiros.loc[index, "ICON_URL"] = save_uploaded_file(new_icon, "parceiros")
                        
                    salvar_dados(df_parceiros, 'data/parceiros.csv')
                    st.success("Parceiro atualizado com sucesso!")
                    st.rerun()
            with col_delete:
                if st.form_submit_button("Remover"):
                    df_parceiros = df_parceiros.drop(index)
                    salvar_dados(df_parceiros, 'data/parceiros.csv')
                    st.success("Parceiro removido com sucesso!")
                    st.rerun()

# --- GERENCIAMENTO DE SERVIÇOS ---
def gerenciar_servicos():
    st.subheader("Gerenciamento de Serviços")
    df_servicos = carregar_dados('data/servicos.csv')

    # Adicionar novo serviço
    with st.expander("Adicionar Novo Serviço"):
        with st.form("form_add_servico", clear_on_submit=True):
            tipo_servico = st.text_input("Tipo de Serviço")
            descricao = st.text_area("Descrição")
            valor_mensal = st.number_input("Valor Mensal", min_value=0.0, format="%.2f")
            valor_adicional = st.number_input("Valor Adicional", min_value=0.0, format="%.2f")
            cupom_mensal = st.number_input("Cupom Mensal", min_value=0.0, format="%.2f")
            cupom_semestral = st.number_input("Cupom Semestral", min_value=0.0, format="%.2f")
            cupom_anual = st.number_input("Cupom Anual", min_value=0.0, format="%.2f")
            submit_button = st.form_submit_button("Adicionar Serviço")

            if submit_button:
                novo_id = (df_servicos['SERVICO_ID'].max() + 1) if not df_servicos.empty else 1
                novo_servico = {
                    "SERVICO_ID": novo_id,
                    "TIPO_SERVICO": tipo_servico,
                    "DESCRICAO_SERVICO": descricao,
                    "VALOR_MENSAL": valor_mensal,
                    "VALOR_ADICIONAL": valor_adicional,
                    "CUPOM_MESAL": cupom_mensal,
                    "CUPOM_SEMESTRAL": cupom_semestral,
                    "CUPOM_ANUAL": cupom_anual
                }
                df_servicos = pd.concat([df_servicos, pd.DataFrame([novo_servico])], ignore_index=True)
                salvar_dados(df_servicos, 'data/servicos.csv')
                st.success("Serviço adicionado com sucesso!")
                st.rerun()

    st.divider()

    # Selecionar serviço para editar/remover
    if not df_servicos.empty:
        servico_selecionado_nome = st.selectbox("Selecione um serviço para editar ou remover", df_servicos['TIPO_SERVICO'])
        servico_selecionado = df_servicos[df_servicos['TIPO_SERVICO'] == servico_selecionado_nome].iloc[0]
        index = servico_selecionado.name

        st.subheader(f"Editando: {servico_selecionado['TIPO_SERVICO']}")
        with st.form(f"form_edit_servico_{index}"):
            tipo_servico = st.text_input("Tipo de Serviço", value=servico_selecionado["TIPO_SERVICO"])
            descricao = st.text_area("Descrição", value=servico_selecionado["DESCRICAO_SERVICO"])
            valor_mensal = st.number_input("Valor Mensal", min_value=0.0, format="%.2f", value=servico_selecionado['VALOR_MENSAL'])
            valor_adicional = st.number_input("Valor Adicional", min_value=0.0, format="%.2f", value=servico_selecionado['VALOR_ADICIONAL'])
            cupom_mensal = st.number_input("Cupom Mensal", min_value=0.0, format="%.2f", value=servico_selecionado['CUPOM_MESAL'])
            cupom_semestral = st.number_input("Cupom Semestral", min_value=0.0, format="%.2f", value=servico_selecionado['CUPOM_SEMESTRAL'])
            cupom_anual = st.number_input("Cupom Anual", min_value=0.0, format="%.2f", value=servico_selecionado['CUPOM_ANUAL'])

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.form_submit_button("Salvar Alterações"):
                    df_servicos.loc[index, "TIPO_SERVICO"] = tipo_servico
                    df_servicos.loc[index, "DESCRICAO_SERVICO"] = descricao
                    df_servicos.loc[index, "VALOR_MENSAL"] = valor_mensal
                    df_servicos.loc[index, "VALOR_ADICIONAL"] = valor_adicional
                    df_servicos.loc[index, "CUPOM_MESAL"] = cupom_mensal
                    df_servicos.loc[index, "CUPOM_SEMESTRAL"] = cupom_semestral
                    df_servicos.loc[index, "CUPOM_ANUAL"] = cupom_anual
                    salvar_dados(df_servicos, 'data/servicos.csv')
                    st.success("Serviço atualizado com sucesso!")
                    st.rerun()
            with col_delete:
                if st.form_submit_button("Remover"):
                    df_servicos = df_servicos.drop(index)
                    salvar_dados(df_servicos, 'data/servicos.csv')
                    st.success("Serviço removido com sucesso!")
                    st.rerun()

# --- GERENCIAMENTO DE BENEFÍCIOS ---
def gerenciar_beneficios():
    st.subheader("Gerenciamento de Benefícios")
    df_beneficios = carregar_dados('data/beneficios.csv')

    if 'to_delete' not in st.session_state:
        st.session_state.to_delete = None

    if st.session_state.to_delete is not None:
        st.warning(f"Tem certeza que deseja remover o benefício {st.session_state.to_delete['TITULO']}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sim, remover"):
                df_beneficios = df_beneficios[df_beneficios['TITULO'] != st.session_state.to_delete['TITULO']]
                salvar_dados(df_beneficios, 'data/beneficios.csv')
                st.success(f"Benefício {st.session_state.to_delete['TITULO']} removido com sucesso!")
                st.rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.to_delete = None
                st.rerun()
        return

    st.write("Selecione um benefício para editar ou remover.")
    beneficio_selecionado = st.selectbox("Selecionar benefício", df_beneficios['TITULO'])

    if beneficio_selecionado:
        st.subheader(f"Editando {beneficio_selecionado}")
        beneficio_data = df_beneficios[df_beneficios['TITULO'] == beneficio_selecionado].iloc[0]

        with st.form("form_edit_beneficio"):
            titulo = st.text_input("Título", value=beneficio_data['TITULO'])
            descricao = st.text_area("Descrição", value=beneficio_data['DESCRICAO_BENEFICIO'])
            icone = st.text_input("Ícone", value=beneficio_data['ICONE'])

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("Salvar Alterações")
            with col2:
                delete_button = st.form_submit_button("Remover Benefício")

            if save_button:
                df_beneficios.loc[df_beneficios['TITULO'] == beneficio_selecionado, 'TITULO'] = titulo
                df_beneficios.loc[df_beneficios['TITULO'] == beneficio_selecionado, 'DESCRICAO_BENEFICIO'] = descricao
                df_beneficios.loc[df_beneficios['TITULO'] == beneficio_selecionado, 'ICONE'] = icone
                
                salvar_dados(df_beneficios, 'data/beneficios.csv')
                st.success("Benefício atualizado com sucesso!")
                st.rerun()

            if delete_button:
                st.session_state.to_delete = beneficio_data.to_dict()
                st.rerun()

    st.subheader("Adicionar Novo Benefício")
    with st.form("form_add_beneficio", clear_on_submit=True):
        titulo = st.text_input("Título")
        descricao = st.text_area("Descrição")
        icone = st.text_input("Ícone")
        submit_button = st.form_submit_button("Adicionar Benefício")

        if submit_button:
            novo_id = (df_beneficios['ID'].max() + 1) if not df_beneficios.empty else 1
            novo_beneficio = {
                "ID": novo_id,
                "TITULO": titulo,
                "DESCRICAO_BENEFICIO": descricao,
                "ICONE": icone
            }
            df_beneficios = pd.concat([df_beneficios, pd.DataFrame([novo_beneficio])], ignore_index=True)
            salvar_dados(df_beneficios, 'data/beneficios.csv')
            st.success("Benefício adicionado com sucesso!")
            st.rerun()

# --- GERENCIAMENTO DE COMENTÁRIOS ---
def gerenciar_comentarios():
    st.subheader("Gerenciamento de Comentários")
    df_comentarios = carregar_dados('data/comentarios.csv')

    if df_comentarios.empty:
        st.info("Nenhum comentário para exibir.")
        return

    if 'to_delete' not in st.session_state:
        st.session_state.to_delete = None

    if st.session_state.to_delete is not None:
        st.warning(f"Tem certeza que deseja remover o comentário ID {st.session_state.to_delete['COMENTARIO_ID']}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sim, remover"):
                df_comentarios = df_comentarios[df_comentarios['COMENTARIO_ID'] != st.session_state.to_delete['COMENTARIO_ID']]
                salvar_dados(df_comentarios, 'data/comentarios.csv')
                st.success(f"Comentário ID {st.session_state.to_delete['COMENTARIO_ID']} removido com sucesso!")
                st.rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.to_delete = None
                st.rerun()
        return

    st.write("Selecione um comentário para remover.")
    
    for index, row in df_comentarios.iterrows():
        st.write(f"**ID:** {row['COMENTARIO_ID']} **Usuário ID:** {row['USER_ID']} **Notícia ID:** {row['NOTICIA_ID']}")
        st.write(f"**Comentário:** {row['COMENTARIO']}")
        st.write(f"**Data:** {row['TIMESTAMP']}")
        if st.button(f"Remover Comentário ID {row['COMENTARIO_ID']}", key=f"delete_comment_{row['COMENTARIO_ID']}"):
            st.session_state.to_delete = row.to_dict()
            st.rerun()
        st.divider()

# --- GERENCIAMENTO DE CONTATOS ---
def gerenciar_contatos():
    st.subheader("Gerenciamento de Contatos")
    df_contatos = carregar_dados('data/contatos.csv')

    if df_contatos.empty:
        st.info("Nenhuma mensagem de contato para exibir.")
        return

    if 'to_delete' not in st.session_state:
        st.session_state.to_delete = None

    if st.session_state.to_delete is not None:
        st.warning(f"Tem certeza que deseja remover a mensagem de {st.session_state.to_delete['NOME']}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sim, remover"):
                df_contatos = df_contatos[df_contatos['ID'] != st.session_state.to_delete['ID']]
                salvar_dados(df_contatos, 'data/contatos.csv')
                st.success(f"Mensagem de {st.session_state.to_delete['NOME']} removida com sucesso!")
                st.rerun()
        with col2:
            if st.button("Cancelar"):
                st.session_state.to_delete = None
                st.rerun()
        return

    st.write("Selecione uma mensagem para remover.")
    
    for index, row in df_contatos.iterrows():
        st.write(f"**ID:** {row['ID']} **Nome:** {row['NOME']} **Email:** {row['EMAIL']}")
        st.write(f"**Mensagem:** {row['MENSAGEM']}")
        st.write(f"**Data:** {row['TIMESTAMP']}")
        if st.button(f"Remover Mensagem de {row['ID']}", key=f"delete_contact_{row['ID']}"):
            st.session_state.to_delete = row.to_dict()
            st.rerun()
        st.divider()

# --- GERENCIAMENTO DE LOG DE ATIVIDADES ---
def gerenciar_log_atividades():
    st.subheader("Log de Atividades")
    df_log = carregar_dados('data/log_atividades.csv')

    if df_log.empty:
        st.info("Nenhum registro de log para exibir.")
        return

    st.dataframe(df_log)

# --- CONTROLE PRINCIPAL ---
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

if st.session_state['admin_logged_in']:
    pagina_admin()
else:
    pagina_login_admin()